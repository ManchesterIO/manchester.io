include_recipe "nginx"

%w(api-server graphite-server sentry-server).each do | server_config |
  template "#{node.nginx.dir}/sites-available/#{server_config}" do
    source "#{server_config}.erb"
    mode "0644"
    variables "root" => node.manchesterio.root,
              "api_hostname" => node.manchesterio.api_hostname,
              "graphite_hostname" => node.manchesterio.graphite_hostname,
              "sentry_hostname" => node.sentry.hostname,
              "graphite_sock" => node.graphite.uwsgi_socket
    notifies :reload, "service[nginx]"
  end

  nginx_site server_config
end