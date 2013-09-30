template "/etc/default/mollyd" do
  source "env-vars.erb"
  variables "root" => node.manchesterio.root
end

directory node.manchesterio.root
directory "#{node.manchesterio.root}/conf"

%w(manchesterio.conf uisettings.py).each do | config_file |
  cookbook_file "#{node.manchesterio.root}/conf/#{config_file}" do
    source config_file
  end
end