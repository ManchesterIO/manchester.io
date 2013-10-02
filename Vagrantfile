# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "precise32"
  config.vm.box_url = "http://files.vagrantup.com/precise32.box"

  config.vm.network :private_network, ip: "192.168.33.12"

  config.vm.provision :chef_solo do |chef|
     chef.cookbooks_path = "site-cookbooks"
     chef.roles_path = "roles"
     chef.add_role "manchesterio"

     chef.json = {
       "mollyproject" => {
         "debug" => true
       },
       "manchesterio" => {
           'ui_hostname' => 'www.sandbox.manchester.io',
           'api_hostname' => 'api.sandbox.manchester.io'
       }
     }
  end

end
