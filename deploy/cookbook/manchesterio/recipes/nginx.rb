include_recipe "chef_nginx::default"

template "#{node['nginx']['dir']}/sites-available/manchesterio" do
  source "manchesterio.erb"
  mode "0644"
  notifies :reload, "service[nginx]"
end

nginx_site 'manchesterio'
