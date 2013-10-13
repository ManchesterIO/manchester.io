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
  variables "sentry_db" => node.sentry.db_file,
            "sentry_hostname" => node.sentry.hostname,
            "sentry_email" => node.sentry.email,
            "secret_key" => node.sentry.secret_key
end

bash "running db upgrade for sentry" do
  code "#{node.sentry.root}/bin/sentry --config=/etc/sentry.conf.py upgrade --noinput"
  user node.sentry.user
  group node.sentry.user
end

cookbook_file "/tmp/sentry-fixtures.json" do
  source node.sentry.fixturefile
end

bash "import sentry fixtures" do
  code "#{node.sentry.root}/bin/sentry --config=/etc/sentry.conf.py loaddata /tmp/sentry-fixtures.json"
  user node.sentry.user
  group node.sentry.user
end

node.sentry.superusers.each do | user |
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

supervisor_service 'sentry' do
  directory node['sentry']['root']
  command "#{node['sentry']['root']}/bin/sentry --config=/etc/sentry.conf.py run_gunicorn -b #{node['sentry']['host']}:#{node['sentry']['port']}"
  user node['sentry']['user']
end