# -*- mode: ruby -*-
# vi: set ft=ruby :

require 'socket'

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.network :private_network, ip: "192.168.33.12"

  config.vm.provider "virtualbox" do | vm |
    vm.memory = 2048
  end

  config.berkshelf.berksfile_path = "deploy/Berksfile"

  config.vm.provision :chef_solo do | chef |
    chef.node_name = 'sandbox.manchester.io'
    chef.cookbooks_path = "deploy/site-cookbooks"
    chef.data_bags_path = "deploy/data_bags"
    chef.encrypted_data_bag_secret_key_path = 'deploy/encrypted_data_bag_secret'
    chef.roles_path = "deploy/roles"
    chef.add_role "manchesterio"

    chef.json = {
        "manchesterio" => {
            'ui_hostname' => 'www.sandbox.manchester.io',
            'api_hostname' => 'api.sandbox.manchester.io',
            'graphite_hostname' => 'graphite.sandbox.manchester.io',
            'sentry_dsn' => 'http://3f76c69909cb4191a5fc02cc32d283e6:770bfa446b59413da819804958a60448@localhost:9000/3',
            'ui_sentry_dsn' => 'http://4b91300f9bde4fccacac0971f2ec6eda:486cd1193e554d42b2164044b49d6922@localhost:9000/2',
            'debug' => true,
            'vagrant' => true,
            'national_rail_consumer_id' => Socket.gethostname
        },
        "sentry" => {
            'hostname' => 'sentry.sandbox.manchester.io',
            'secret_key' => 'UgXYwX5NEMDtyIIHGVjM7oeSJzG7PSeFyyipEu2CUJUJDCQb17W1zA==',
            'superusers' => [{'username' => 'sandbox', 'password' => 'sandbox'}]
        }
    }
  end

  config.vm.synced_folder "deploy/site-cookbooks/manchesterio/files/default/static", "/srv/manchester.io/static"
  config.vm.synced_folder "manchesterio", "/srv/manchester.io/manchesterio"
  config.vm.synced_folder "medlock", "/srv/manchester.io/medlock"

end
