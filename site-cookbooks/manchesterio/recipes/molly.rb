include_recipe "mollyproject::install_git_master"

directory node.manchesterio.root
directory "#{node.manchesterio.root}/conf"
directory "#{node.manchesterio.root}/compiled_media" do
  user node.mollyproject.user
  group node.mollyproject.user
end

%w(Flask-StatsD raven[flask]).each do | python_package |
  python_pip python_package do
    virtualenv node.mollyproject.install_root
    user node.mollyproject.user
    group node.mollyproject.user
  end
end

%w(manchesterio.conf uisettings.py).each do | config_file |
  template "#{node.manchesterio.root}/conf/#{config_file}" do
    source "#{config_file}.erb"
    mode 0644
    config = node.manchesterio.to_hash
    config['molly_root'] = node.mollyproject.install_root
    config['sentry_dsn'] = Chef::EncryptedDataBagItem.load('secrets', 'sentry')['api_dsn'] if config['sentry_dsn'].nil?
    config['ui_sentry_dsn'] = Chef::EncryptedDataBagItem.load('secrets', 'sentry')['ui_dsn'] if config['ui_sentry_dsn'].nil?
    variables config
  end
end

include_recipe "mollyproject"
