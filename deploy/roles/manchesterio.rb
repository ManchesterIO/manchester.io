name 'manchesterio'
description 'manchester.io full stack'

default_attributes 'ssh_keys' => {'deploy' => %w(chris)},
                   'authorization' => {
                       'sudo' => {
                           'users' => ["deploy"],
                           'passwordless' => true
                       }
                   },
                   'graphite' => {
                       'group-account' => 'www-data',
                       'listen_port' => '8100',
                       'timezone' => 'Europe/London',
                       'user_account' => 'www-data',
                       'uwsgi' => { 'socket' => '/opt/graphite/storage/uwsgi.sock' },
                       'web_server' => 'uwsgi'
                   },
                   'nginx' => {'default_site_enabled' => false},
                   'sentry' => {'fixturefile' => 'sentry-fixtures.json.erb'},
                   'statsd' => {'nodejs_bin' => '/usr/bin/node'}

run_list 'recipe[mongodb::10gen_repo]',
         'recipe[mongodb::default]',
         'recipe[statsd]',
         'recipe[graphite]',
         'recipe[manchesterio::sentry]',
         'recipe[manchesterio::nginx]',
         'recipe[rabbitmq]',
         'recipe[manchesterio::medlock]',
         'recipe[manchesterio::manchesterio]'
