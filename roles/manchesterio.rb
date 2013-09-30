name 'manchesterio'
description 'manchester.io full stack'

default_attributes 'ssh_keys' => { 'manchesterio' => %w(chris)},
 'authorization' => {
        'sudo' => {
            'users' => ["manchesterio"],
            'passwordless' => true
        }
    },
 'nginx' => { 'default_site_enabled' => false }

run_list 'recipe[sudo]',
         'recipe[ssh-keys]',
         'recipe[firewall]',
         'recipe[manchesterio::firewall]',
         'recipe[mongodb::10gen_repo]',
         'recipe[mongodb::default]',
         'recipe[memcached]',
         'recipe[python]',
         'recipe[manchesterio::nginx]',
         'recipe[nginx]',
         'recipe[rabbitmq]',
         'recipe[manchesterio::molly]',
         'recipe[mollyproject]'
