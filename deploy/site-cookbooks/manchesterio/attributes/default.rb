default['manchesterio']['root'] = '/srv/manchester.io'
default['manchesterio']['user'] = 'manchesterio'
default['manchesterio']['ui_hostname'] = 'manchester.io'
default['manchesterio']['api_hostname'] = 'api.manchester.io'
default['manchesterio']['graphite_hostname'] = 'graphite.manchester.io'
default['manchesterio']['sentry_dsn'] = nil
default['manchesterio']['ui_sentry_dsn'] = nil
default['manchesterio']['vagrant'] = false
default['manchesterio']['debug'] = false
default['manchesterio']['network_rail_credentials'] = { 'user' => nil, 'pass' => nil }
default['manchesterio']['network_rail_consumer_id'] = 'manchester.io'

default['sentry']['root'] = '/opt/sentry'
default['sentry']['secret_key'] = nil
default['sentry']['db_file'] = '/opt/sentry/sentry.db'
default['sentry']['hostname'] = 'sentry.manchester.io'
default['sentry']['host'] = '127.0.0.1'
default['sentry']['port'] = '9000'
default['sentry']['email'] = 'sentry@manchester.io'
default['sentry']['user'] = 'sentry'
default['sentry']['superusers'] = []
