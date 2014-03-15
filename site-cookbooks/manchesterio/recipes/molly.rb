include_recipe "mollyproject::install_git_master"

directory node.manchesterio.root
directory "#{node.manchesterio.root}/conf"

%w(Flask-StatsD raven[flask]).each do | python_package |
  python_pip python_package do
    virtualenv node.mollyproject.install_root
    user node.mollyproject.user
    group node.mollyproject.user
  end
end

template "#{node.manchesterio.root}/conf/manchesterio.conf" do
  source "manchesterio.conf.erb"
  mode 0644
  config = node.manchesterio.to_hash
  config['molly_root'] = node.mollyproject.install_root
  config['sentry_dsn'] = Chef::EncryptedDataBagItem.load('secrets', 'sentry')['api_dsn'] if config['sentry_dsn'].nil?
  variables config
end

include_recipe "mollyproject"
