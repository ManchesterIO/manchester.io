name 'manchesterio'
description 'manchester.io full stack'

default_attributes 'ssh_keys' => {'deploy' => %w(chris simon)},
                   'authorization' => {
                       'sudo' => {
                           'users' => ["deploy"],
                           'passwordless' => true
                       }
                   },
                   'nginx' => {'default_site_enabled' => false}

run_list 'recipe[manchesterio::nginx]',
         'recipe[manchesterio::manchesterio]'
