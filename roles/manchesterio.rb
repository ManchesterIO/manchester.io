name 'manchesterio'
description 'manchester.io full stack'

default_attributes 'ssh_keys' => {'manchesterio' => %w(chris)},
                   'authorization' => {
                       'sudo' => {
                           'users' => ["manchesterio"],
                           'passwordless' => true
                       }
                   },
                   'graphite' => {
                       'listen_port' => '8100',
                       'timezone' => 'Europe/London',
                       'uwsgi_socket' => '/opt/graphite/storage/uwsgi.sock',
                       'web_server' => 'nginx'
                   },
                   'nginx' => {'default_site_enabled' => false},
                   'mollyproject' => {
                       'config' => '/srv/manchester.io/conf/manchesterio.conf',
                       'ui' => {
                           'settings' => '/srv/manchester.io/conf/uisettings.py'
                       }
                   },
                   'rabbitmq' => {'local_erl_networking' => true}

run_list 'recipe[mongodb::10gen_repo]',
         'recipe[mongodb::default]',
         'recipe[memcached]',
         'recipe[statsd]',
         'recipe[graphite]',
         'recipe[manchesterio::nginx]',
         'recipe[rabbitmq]',
         'recipe[manchesterio::molly]'
