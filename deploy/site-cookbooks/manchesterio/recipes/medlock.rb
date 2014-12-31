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

supervisor_service "medlock" do
  if node.manchesterio.debug
    command "#{node.manchesterio.root}/bin/medlock/bin/python #{node.manchesterio.root}/medlock/medlock/app.py"
  else
    command "#{node.manchesterio.root}/bin/medlock/bin/gunicorn medlock.app:app -b 127.0.0.1:8010 -e SENTRY_DSN=#{node.manchesterio.sentry_dsn}"
  end
  user node.manchesterio.user
  environment "PYTHONPATH" => "#{node.manchesterio.root}/medlock",
              "SENTRY_DSN" => node.manchesterio.sentry_dsn
end

supervisor_service "medlock_taskbeat" do
  command "#{node.manchesterio.root}/medlock/taskbeat.py"
  user node.manchesterio.user
  environment "PYTHONPATH" => "#{node.manchesterio.root}/medlock",
              "DEBUG" => node.manchesterio.debug,
              "SENTRY_DSN" => node.manchesterio.sentry_dsn
end

supervisor_service "medlock_taskworker" do
  command "#{node.manchesterio.root}/medlock/taskworker.py"
  user node.manchesterio.user
  environment "PYTHONPATH" => "#{node.manchesterio.root}/medlock",
              "DEBUG" => node.manchesterio.debug,
              "SENTRY_DSN" => node.manchesterio.sentry_dsn
end
