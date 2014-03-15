include_recipe "nginx"

apt_repository "ondrej-php5" do
  uri "http://ppa.launchpad.net/ondrej/php5/ubuntu"
  distribution node['lsb']['codename']
  components ["main"]
  keyserver "keyserver.ubuntu.com"
  key "4F4EA0AAE5267A6C"
end

cookbook_file "php.ini" do
  path "/etc/php5/fpm/conf.d/manchesterio.ini"
end

%w(php5-fpm php5-json php5-mcrypt).each { | package | package package }

%w(api-server ui-server graphite-server sentry-server).each do | server_config |
  template "#{node.nginx.dir}/sites-available/#{server_config}" do
    source "#{server_config}.erb"
    mode "0644"
    variables "root" => node.manchesterio.root,
              "api_hostname" => node.manchesterio.api_hostname,
              "ui_hostname" => node.manchesterio.ui_hostname,
              "graphite_hostname" => node.manchesterio.graphite_hostname,
              "sentry_hostname" => node.sentry.hostname,
              "graphite_sock" => node.graphite.uwsgi_socket
    notifies :reload, "service[nginx]"
  end

  nginx_site server_config
end