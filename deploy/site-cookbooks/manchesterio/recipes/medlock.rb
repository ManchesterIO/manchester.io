include_recipe "python"
include_recipe "supervisor"
include_recipe "manchesterio::system"

unless node.manchesterio.vagrant

  remote_directory "#{node.manchesterio.root}/medlock" do
    source "medlock"
  end

end

python_virtualenv "#{node.manchesterio.root}/bin/medlock" do
  owner node.manchesterio.user
  group node.manchesterio.user
end

python_pip "#{node.manchesterio.root}/medlock/requirements.txt" do
  options '-r'
  virtualenv "#{node.manchesterio.root}/bin/medlock"
end

supervisor_service "medlock" do
  extra_args = "--reload" if node.manchesterio.debug
  command "#{node.manchesterio.root}/bin/medlock/bin/gunicorn medlock:app -b 127.0.0.1:8010 -e DEBUG=#{node.manchesterio.debug} #{extra_args}"
  user node.manchesterio.user
  environment "PYTHONPATH" => "#{node.manchesterio.root}/medlock"
end
