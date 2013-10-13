include_recipe "nginx"

%w(ui-server api-server graphite-server).each do | server_config |
  template "#{node.nginx.dir}/sites-available/#{server_config}" do
    source "#{server_config}.erb"
    mode "0644"
    variables "root" => node.manchesterio.root,
              "api_hostname" => node.manchesterio.api_hostname,
              "ui_hostname" => node.manchesterio.ui_hostname,
              "graphite_hostname" => node.manchesterio.graphite_hostname,
              "graphite_sock" => node.graphite.uwsgi_socket
  end

  nginx_site server_config
end