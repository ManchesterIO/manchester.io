Chris's Opinionated Build Pipeline
==================================

This project only focuses on building front end assets. It's nothing too fancy,
it just uses wires a bunch of tools together in a simple way. It specifically
doesn't do anything that assumes how your HTML will be generated, whether or
not that's by a server-side application, or static HTML.

Scripts
-------

* Production code goes in the assets/js folder
* Test code goes in the assets/js-test folder
* Plain old JavaScript
* Using [AMDs](https://github.com/amdjs/amdjs-api/blob/master/AMD.md) for your
  JavaScript modules, with require.js as a module loader
* [Jasmine](http://jasmine.github.io/) as a testing framework (run using Karma
  and PhantomJS). All files ending in Spec.js are run.
* [JSHint](http://www.jshint.com/) for quality control

Stylesheets
-----------

* [SCSS](http://sass-lang.com/) with [Compass](http://compass-style.org/)
* [scss-lint](https://github.com/causes/scss-lint) for quality control

Compass also gives us font and image spriting support for free. If you want
to handle your images in a different way, then edit the Gruntfile to make it
work for you!

Third-party dependencies are handled with Bower. This comes ready to run on
Travis CI.

Getting Started
---------------

* You'll need Ruby (with Rubygems and Bundler) and Node.JS (with NPM) installed
* Run `npm install`
* Run `grunt` to output full production artifacts (minimised, optimised, etc)
* Run `grunt dev` to output unminified artifacts (useful for dev). This also
  starts watching for changes and reruns jobs as appropriate.

To see the output files in action, you could create a simple HTML file such as
the one below as `dist/index.html`, and then open that in your browser:

    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Hello World</title>
        <link href="static/styles/project.css" rel="stylesheet">
    </head>
    <body>
        <script src="static/scripts/project.js"></script>
        <script>
            require(['project/main'], function(main) { main() });
        </script>
    </body>
    </html>

Customising your project
------------------------

You'll probably also want to change some of your filenames to reflect your
project - the default AMD module that's compiled is `project/main`. If you
rename the directory/file (and tests), then all you need to do is update the
`requirejs.options.name` setting in Gruntfile.js.

Any new dependencies installed in Bower aren't publicly accessible by default.
You should add paths to your require map in the Gruntfile for production code
and in testMain.js for your test codes. You can make these relative into
bower_components. Similarly for your CSS, you can @include them in your Sass
files.

The files in dist/static/ you'll want to configure to just be straightforwardly
served using whatever you're using to run your app. These can also go off to a
CDN (e.g., in a versioned directory).
