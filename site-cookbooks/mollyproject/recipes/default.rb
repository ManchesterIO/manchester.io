user node.mollyproject.user do
  home node.mollyproject.install_root
end

%w(build-essential libgeos-c1 libprotobuf-dev protobuf-compiler git-core).each { | package | package package }

python_virtualenv node.mollyproject.install_root do
  owner node.mollyproject.user
  group node.mollyproject.user
  action :create
end

%w(run log).each do | subdir |
  directory "#{node.mollyproject.install_root}/#{subdir}" do
    owner node.mollyproject.user
    group node.mollyproject.user
  end
end

python_pip "git+https://github.com/ManchesterIO/mollyproject-next.git" do
  virtualenv node.mollyproject.install_root
  user node.mollyproject.user
  group node.mollyproject.user
  action :upgrade
end

template "/etc/init.d/#{node.mollyproject.service_name}" do
  source "init-script.erb"
  variables "root" => node.mollyproject.install_root, "service_name" => node.mollyproject.service_name
  mode "0755"
end

service node['mollyproject']['service_name'] do
  start_command "/etc/init.d/#{node.mollyproject.service_name} start"
  stop_command "/etc/init.d/#{node.mollyproject.service_name} stop"
  restart_command "/etc/init.d/#{node.mollyproject.service_name} restart"
  supports :restart => true
  action [ :enable, :restart ]
end