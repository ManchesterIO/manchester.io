include_recipe "htpasswd"
include_recipe "python"
include_recipe "supervisor"

user node['sentry']['user'] do
  home node['sentry']['root']
end

directory node['sentry']['root'] do
  owner node.sentry.user
  group node.sentry.user
end

python_virtualenv node['sentry']['root'] do
  owner node.sentry.user
  group node.sentry.user
end

python_pip "sentry" do
  virtualenv node['sentry']['root']
end

python_pip "django-nginx-remote-user-middleware" do
  virtualenv node['sentry']['root']
end

template "/etc/sentry.conf.py" do
  source "sentry.conf.py.erb"
  mode "0644"
  secret_key = node.sentry.secret_key
  secret_key = Chef::EncryptedDataBagItem.load('secrets', 'sentry')['secret_key'] if secret_key.nil?
  variables "sentry_db" => node.sentry.db_file,
            "sentry_hostname" => node.sentry.hostname,
            "sentry_email" => node.sentry.email,
            "secret_key" => secret_key
end

bash "running db upgrade for sentry" do
  code "#{node.sentry.root}/bin/sentry --config=/etc/sentry.conf.py upgrade --noinput"
  user node.sentry.user
  group node.sentry.user
end

if node.sentry.superusers.empty?
  sentry_superusers = []
  data_bag('sentry_users').each do |item|
    sentry_superusers << Chef::EncryptedDataBagItem.load('sentry_users', item)
  end
else
  sentry_superusers = node.sentry.superusers
end

sentry_superusers.each do | user |
  bash "set up superuser for #{user['username']}" do
    code "#{node.sentry.root}/bin/sentry --config=/etc/sentry.conf.py createsuperuser --username=#{user['username']} --email=#{user['username']}@manchester.io --noinput || true"
    user node.sentry.user
    group node.sentry.user
  end

  htpasswd "#{node['sentry']['root']}/htpasswd" do
    user user['username']
    password user['password']
  end
end

template "/tmp/sentry-fixtures.json" do
  source "sentry-fixtures.json.erb"
  api_dsn = node.manchesterio.sentry_dsn
  api_dsn = Chef::EncryptedDataBagItem.load('secrets', 'sentry')['api_dsn'] if api_dsn.nil?
  ui_dsn = node.manchesterio.ui_sentry_dsn
  ui_dsn = Chef::EncryptedDataBagItem.load('secrets', 'sentry')['ui_dsn'] if ui_dsn.nil?
  url_regex = /http:\/\/([^:]+):([^@]+)@.+/
  variables "api_secret" => url_regex.match(api_dsn)[2],
            "api_key" => url_regex.match(api_dsn)[1],
            "ui_secret" => url_regex.match(ui_dsn)[2],
            "ui_key" => url_regex.match(ui_dsn)[1]
end

bash "import sentry fixtures" do
  code "#{node.sentry.root}/bin/sentry --config=/etc/sentry.conf.py loaddata /tmp/sentry-fixtures.json"
  user node.sentry.user
  group node.sentry.user
end
supervisor_service 'sentry' do
  directory node['sentry']['root']
  command "#{node['sentry']['root']}/bin/sentry --config=/etc/sentry.conf.py run_gunicorn -b #{node['sentry']['host']}:#{node['sentry']['port']}"
  user node['sentry']['user']
end