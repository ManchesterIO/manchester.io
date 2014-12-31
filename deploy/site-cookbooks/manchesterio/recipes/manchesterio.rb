include_recipe "python"
include_recipe "supervisor"
include_recipe "manchesterio::system"

unless node.manchesterio.vagrant

  remote_directory "#{node.manchesterio.root}/manchesterio" do
    source "manchesterio"
  end

  remote_directory "/srv/manchester.io/static" do
    source "static"
  end

end

python_virtualenv "#{node.manchesterio.root}/bin/manchesterio" do
  owner node.manchesterio.user
  group node.manchesterio.user
end

python_pip "#{node.manchesterio.root}/manchesterio/requirements.txt" do
  options '-r'
  virtualenv "#{node.manchesterio.root}/bin/manchesterio"
end

supervisor_service "manchesterio" do
  user node.manchesterio.user
  if node.manchesterio.debug
    command "#{node.manchesterio.root}/bin/manchesterio/bin/python #{node.manchesterio.root}/manchesterio/manchesterio/app.py"
  else
    command "#{node.manchesterio.root}/bin/manchesterio/bin/gunicorn manchesterio.app:app -b 127.0.0.1:8000 -e API_BASE_URL=#{node.manchesterio.api_hostname} -e SENTRY_DSN=#{node.manchesterio.ui_sentry_dsn}"
  end
  environment "PYTHONPATH" => "#{node.manchesterio.root}/manchesterio", 'API_BASE_URL' => node.manchesterio.api_hostname, 'SENTRY_DSN' => node.manchesterio.ui_sentry_dsn
end
