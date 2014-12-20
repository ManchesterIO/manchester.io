manchester.io
=============

This project allows you to deploy manchester.io.

Dependencies
------------

* [Chef](https://downloads.chef.io/chef-dk/)
* [NodeJS](http://nodejs.org/)
* [RVM](https://rvm.io/)
* [Vagrant](http://vagrantup.com/)

Prepping
--------

manchester.io uses Grunt/Compass to manage building of the static assets:

    npm install
    npm install -g grunt-cli

This will set up an environment ready for local development.

Deployment is done using Knife Solo:

    cd deploy
    bundle install

Building assets
---------------

### On the sandbox ###

In order to build the development version of the assets, and then automatically recompile them on change, run:

    grunt dev

In order to build production-ready versions of the assets, then run:

    grunt

Deploying to sandbox
--------------------

Vagrant is used to manage pre-production environments. Simply install vagrant, and then use the following commands
to start up a local machine:

    vagrant plugin install vagrant-berkshelf # Only needed on first run
    vagrant up

You will then be able to access manchester.io via the URLs: http://api.sandbox.manchester.io and http://www.sandbox.manchester.io

### Sentry/Graphite on the sandbox ###

The sandbox should be configured to fully replicate a production environment. You can visit Sentry at
http://sentry.sandbox.manchester.io and your sandbox should be configured to send events to it. Graphite is available at
http://graphite.sandbox.manchester.io

Deploying to production
-----------------------

Well manchester.io hasn't quite reached production yet, but you can deploy to the beta server (if you have permission):

    cd deploy
    knife solo cook beta.manchester.io
    ssh manchesterio@beta.manchester.io sudo supervisorctl restart all

### Getting permission to deploy to production ###

Make a fork of the project and check it out, then run:

    knife solo data bag create users <YourUsername>

And then create a JSON file in the format below:

    {
      "id": "myuser",
      "ssh_keys": "ssh-rsa AAAA... myuser@mymachine.example.com"
    }

You will also need a copy of the data bag secret and put it in the "encrypted_data_bag_secret" folder. An existing
developer will be able to share this with you.

Please note that to get permission to deploy you will need to show to the other developers that you are trustworthy.
This is normally achieved by making a number of high-quality commits and interacting with the developers directly. If
you do not become a core developer, then your SSH key may not be merged into master, but you will still be able to
deploy to your own staging servers.

### Accessing Sentry/Graphite on production ###

Create a databag for a password:

    knife solo data bag create sentry_users <YourUsername>

And then create a JSON file like so:

    {
      "id": "myuser",
      "username": "myuser",
      "password": "password"
    }

You should then be able to http://sentry.manchester.io and http://graphite.manchester.io using that username and
password once it's been deployed.
