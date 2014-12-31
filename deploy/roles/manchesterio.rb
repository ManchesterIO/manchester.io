name 'manchesterio'
description 'manchester.io full stack'

default_attributes 'ssh_keys' => {'deploy' => %w(chris)},
                   'authorization' => {
                       'sudo' => {
                           'users' => ["deploy"],
                           'passwordless' => true
                       }
                   },
                   'graphite' => { 'uwsgi' => { 'workers' => '2 -C666' } },
                   'nginx' => {'default_site_enabled' => false},
                   'sentry' => {'fixturefile' => 'sentry-fixtures.json.erb'},
                   'statsd' => {'nodejs_bin' => '/usr/bin/node'}

run_list 'recipe[mongodb::10gen_repo]',
         'recipe[mongodb::default]',
         'recipe[statsd]',
         'recipe[graphite]',
         'recipe[graphite::web]',
         'recipe[graphite::uwsgi]',
         'recipe[manchesterio::graphite]',
         'recipe[manchesterio::sentry]',
         'recipe[manchesterio::nginx]',
         'recipe[rabbitmq]',
         'recipe[manchesterio::medlock]',
         'recipe[manchesterio::manchesterio]'
