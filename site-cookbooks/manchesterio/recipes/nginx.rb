include_recipe "nginx"

%w(ui-server api-server).each do | server_config |
  template "#{node.nginx.dir}/sites-available/#{server_config}" do
    source "#{server_config}.erb"
    mode "0644"
    variables "root" => node.manchesterio.root,
              "api_hostname" => node.manchesterio.api_hostname,
              "ui_hostname" => node.manchesterio.ui_hostname
  end

  nginx_site server_config
end