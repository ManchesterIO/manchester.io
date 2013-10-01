default['mollyproject']['user'] = 'molly'
default['mollyproject']['install_root'] = '/opt/molly'
default['mollyproject']['config'] = "#{default['mollyproject']['install_root']}/conf/default.conf"
default['mollyproject']['ui']['settings'] = "#{default['mollyproject']['install_root']}/conf/ui.py"
default['mollyproject']['ui']['module'] = 'molly.ui.html5.server:flask_app'