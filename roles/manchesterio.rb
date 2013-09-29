name "manchesterio"
description "manchester.io servers"

default_attributes "ssh_keys" => { "manchesterio" => ["chris"] }
default_attributes "authorization" => {
        "sudo" => {
            "users" => ["manchesterio"],
            "passwordless" => true
        }
    }

run_list "recipe[sudo]",
         "recipe[ssh-keys]",
         "recipe[mongodb::10gen_repo]",
         "recipe[mongodb::default]",
         "recipe[memcached]",
         "recipe[python]",
         "recipe[firewall]",
         "recipe[manchesterio::firewall]"