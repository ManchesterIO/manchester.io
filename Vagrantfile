# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "precise32"
  config.vm.box_url = "http://files.vagrantup.com/precise32.box"

  config.vm.network :private_network, ip: "192.168.33.12"

  config.vm.provision :shell, :inline => "gem install chef --version 11.6.0 --no-rdoc --no-ri --conservative"

  config.vm.provision :chef_solo do |chef|
    chef.node_name = 'sandbox.manchester.io'
    chef.cookbooks_path = "site-cookbooks"
    chef.roles_path = "roles"
    chef.add_role "manchesterio"

    chef.json = {
        "mollyproject" => {
            "debug" => true
        },
        "manchesterio" => {
            'ui_hostname' => 'www.sandbox.manchester.io',
            'api_hostname' => 'api.sandbox.manchester.io',
            'graphite_hostname' => 'graphite.sandbox.manchester.io',
            'sentry_dsn' => 'http://4b91300f9bde4fccacac0971f2ec6eda:486cd1193e554d42b2164044b49d6922@localhost:9000/3',
            'ui_sentry_dsn' => 'http://3f76c69909cb4191a5fc02cc32d283e6:770bfa446b59413da819804958a60448@localhost:9000/2'
        },
        "sentry" => {
            'fixturefile' => 'sentry-fixtures-sandbox.json',
            'hostname' => 'sentry.sandbox.manchester.io',
            'superusers' => [{'username' => 'sandbox', 'password' => 'sandbox'}]
        }
    }
  end

end
