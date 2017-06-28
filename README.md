manchester.io
=============

[![Build Status](https://travis-ci.org/ManchesterIO/manchester.io.svg?branch=master)](https://travis-ci.org/ManchesterIO/manchester.io)

This project allows you to deploy manchester.io.

Dependencies
------------

Install Chef, Vagrant and VirtualBox:

* [Chef](https://downloads.chef.io/chef-dk/)
* [Vagrant](http://vagrantup.com/)
* [VirtualBox](https://www.virtualbox.org/)

Now, you need to install the Berkshelf and Omnibus plugin for Vagrant:

    vagrant plugin install vagrant-berkshelf vagrant-omnibus

Running locally
---------------

Vagrant is used to manage pre-production environments. Simply install vagrant, and then use the following commands
to start up a local machine:

    vagrant up

Now, you need to start your dev server:

    vagrant ssh
    cd /srv/manchester.io
    yarn dev

You will then be able to access manchester.io via http://sandbox.manchester.io

Running tests
-------------

    vagrant ssh
    cd /srv/manchester.io
    yarn test

You can also start a test watcher:

    vagrant ssh
    cd /srv/manchester.io
    yarn test-watch

Deploying to production
-----------------------

Chef is used to deploy to the production server.

    vagrant ssh
    cd /srv/manchester.io
    yarn deploy

### Getting permission to deploy to production ###

Make a fork of the project and check it out, then run:

    bundle exec knife solo data bag create users <YourUsername>

And then create a JSON file in the format below:

    {
      "id": "myuser",
      "ssh_keys": "ssh-rsa AAAA... myuser@mymachine.example.com"
    }

Please note that to get permission to deploy you will need to show to the other developers that you are trustworthy.
This is normally achieved by making a number of high-quality commits and interacting with the developers directly. If
you do not become a core developer, then your SSH key may not be merged into master, but you will still be able to
deploy to your own staging servers.
