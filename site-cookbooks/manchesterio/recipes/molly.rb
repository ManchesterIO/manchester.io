include_recipe "mollyproject::install_git_master"

directory node.manchesterio.root
directory "#{node.manchesterio.root}/conf"
directory "#{node.manchesterio.root}/compiled_media" do
  user node.mollyproject.user
  group node.mollyproject.user
end

%w(manchesterio.conf uisettings.py).each do | config_file |
  template "#{node.manchesterio.root}/conf/#{config_file}" do
    source "#{config_file}.erb"
    mode 0644
    variables node.manchesterio
  end
end

include_recipe "mollyproject"
