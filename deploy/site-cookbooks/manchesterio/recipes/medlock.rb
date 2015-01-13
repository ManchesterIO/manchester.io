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

%w(libgeos-c1 libgeos-dev).each { | package | package package }

python_pip "#{node.manchesterio.root}/medlock/requirements.txt" do
  options '-r'
  virtualenv "#{node.manchesterio.root}/bin/medlock"
end

template "#{node.manchesterio.root}/medlock.cfg" do
  source "medlock.cfg.erb"
  mode "0644"
  network_rail_creds = node.manchesterio.network_rail_credentials
  network_rail_creds = Chef::EncryptedDataBagItem.load('secrets', 'network_rail') if network_rail_creds.user.nil?
  sentry_dsn = node.manchesterio.sentry_dsn
  sentry_dsn = Chef::EncryptedDataBagItem.load('secrets', 'sentry')['api_dsn'] if sentry_dsn.nil?
  variables "network_rail" => network_rail_creds, 'sentry_dsn' => sentry_dsn
end

supervisor_service "medlock" do
  if node.manchesterio.debug
    command "#{node.manchesterio.root}/bin/medlock/bin/python #{node.manchesterio.root}/medlock/medlock/app.py -e CONFIG=#{node.manchesterio.root}/medlock.cfg"
  else
    command "#{node.manchesterio.root}/bin/medlock/bin/gunicorn medlock.app:app -b 127.0.0.1:8010"
  end
  user node.manchesterio.user
  environment "PYTHONPATH" => "#{node.manchesterio.root}/medlock", "CONFIG" => "#{node.manchesterio.root}/medlock.cfg"
end

supervisor_service "medlock_taskbeat" do
  command "#{node.manchesterio.root}/bin/medlock/bin/celery beat -A medlock.app:celery -S medlock.scheduler.Scheduler --pidfile=#{node.manchesterio.root}/data/celerybeat.pid"
  user node.manchesterio.user
  environment "PYTHONPATH" => "#{node.manchesterio.root}/medlock", "CONFIG" => "#{node.manchesterio.root}/medlock.cfg"
end

supervisor_service "medlock_taskworker" do
  command "#{node.manchesterio.root}/bin/medlock/bin/celery worker -A medlock.app:celery"
  user node.manchesterio.user
  environment "PYTHONPATH" => "#{node.manchesterio.root}/medlock", "CONFIG" => "#{node.manchesterio.root}/medlock.cfg"
end
