VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "ubuntu/xenial64"
  config.ssh.forward_agent = true

  config.vm.network :private_network, ip: "192.168.33.12"

  config.vm.provider "virtualbox" do | vm |
    vm.memory = 2048
    vm.cpus = 2
    vm.customize ['modifyvm', :id, '--natpf2', 'tcp9229,tcp,127.0.0.1,9229,192.168.193.12,9229'] # Debugging Node apps on the sandbox
  end

  config.berkshelf.enabled = true
  config.berkshelf.berksfile_path = "deploy/Berksfile"
  config.omnibus.chef_version = :latest

  config.vm.provision :chef_solo do | chef |
    chef.node_name = 'sandbox.manchester.io'
    chef.cookbooks_path = "deploy/site-cookbooks"
    chef.data_bags_path = "deploy/data_bags"
    chef.roles_path = "deploy/roles"
    chef.add_role "manchesterio"

    chef.json = {
        "manchesterio" => {
            'hostname' => 'sandbox.manchester.io',
            'debug' => true,
            'vagrant' => true,
        },
    }
  end

  config.vm.synced_folder ".", "/srv/manchester.io"
  config.vm.synced_folder "deploy/site-cookbooks/manchesterio/files/default/static", "/srv/manchester.io/static"

  config.vm.provision 'shell', :inline => 'apt-get install ruby-bundler ruby-dev build-essential'

end
