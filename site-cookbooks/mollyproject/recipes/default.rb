user node.mollyproject.user do
  home node.mollyproject.install_root
end

%w(build-essential libgeos-c1 libprotobuf-dev protobuf-compiler git-core).each { | package | package package }

python_virtualenv node.mollyproject.install_root do
  owner node.mollyproject.user
  group node.mollyproject.user
end

python_pip "git+https://github.com/ManchesterIO/mollyproject-next.git" do
  virtualenv node.mollyproject.install_root
  user node.mollyproject.user
  group node.mollyproject.user
  action :upgrade
end

supervisor_service "mollyrest" do
  command "#{node.mollyproject.install_root}/bin/mollyrest"
  user node.mollyproject.user
  environment "MOLLY_CONFIG" => node.mollyproject.config
end

supervisor_service "mollyui" do
  command "#{node.mollyproject.install_root}/bin/mollyui"
  user node.mollyproject.user
  environment "MOLLY_UI_SETTINGS" => node.mollyproject.ui.settings,
              "MOLLY_UI_MODULE" => node.mollyproject.ui.module
end

supervisor_service "mollytaskbeat" do
  command "#{node.mollyproject.install_root}/bin/mollyrest taskbeat"
  user node.mollyproject.user
  environment "MOLLY_CONFIG" => node.mollyproject.config
end

supervisor_service "mollytaskworker" do
  command "#{node.mollyproject.install_root}/bin/mollyrest taskworker"
  user node.mollyproject.user
  environment "MOLLY_CONFIG" => node.mollyproject.config
end
