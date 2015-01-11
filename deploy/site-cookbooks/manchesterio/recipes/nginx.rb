include_recipe "nginx"

%w(api-server ui-server graphite-server sentry-server).each do | server_config |
  template "#{node.nginx.dir}/sites-available/#{server_config}" do
    source "#{server_config}.erb"
    mode "0644"
    notifies :reload, "service[nginx]"
  end

  nginx_site server_config
end
