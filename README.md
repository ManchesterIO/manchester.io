manchester.io
=============

This project allows you to deploy manchester.io.

Dependencies
------------

* [RVM](https://rvm.io/)

Prepping
--------

manchester.io uses Chef to manage deployments. If you've got RVM installed, then you should be able to go into the
folder and run:

    bundle

This will set up an environment ready for deployment

Deploying to sandbox
--------------------

Vagrant is used to manage pre-production environments. Simply install vagrant, and then use the following commands
to start up a local machine:

    vagrant up

On first install you will need to run:

    vagrant plugin install vagrant-berkshelf

You will then be able to access manchester.io via the URLs: api.sandbox.manchester.io and www.sandbox.manchester.io

Deploying to production
-----------------------

Well manchester.io hasn't quite reached production yet, but you can deploy to the beta server (if you have permission):

    knife solo cook beta.manchester.io

### Getting permission to deploy to production ###

Make a fork of the project and check it out, then run:

    knife solo data bag create users <YourUsername>

And then create a JSON file in the format below:

    {
      "id": "myuser",
      "ssh_keys": "ssh-rsa AAAA... myuser@mymachine@example.com"
    }

Please note that to get permission to deploy you will need to show to the other developers that you are trustworthy.
This is normally achieved by making a number of high-quality commits and interacting with the developers directly. If
you do not become a core developer, then your SSH key may not be merged into master, but you will still be able to
deploy to your own staging servers.
