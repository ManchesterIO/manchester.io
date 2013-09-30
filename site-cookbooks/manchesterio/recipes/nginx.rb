%w(beta.manchester.io api.beta.manchester.io).each do | site_name |
  template "#{node.nginx.dir}/sites-available/#{site_name}" do
    source "#{site_name}.erb"
    mode "0644"
    variables "root" => node.manchesterio.root
  end

  nginx_site site_name
end