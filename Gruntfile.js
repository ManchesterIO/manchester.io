var shelljs = require('shelljs');

module.exports = function(grunt) {
    grunt.initConfig({
        compass: {
            compile: { },
            dev: {
                options: {
                    outputStyle: 'expanded'
                }
            },
            options: {
                bundleExec: true,
                config: 'assets/scss/compass_config.rb'
            }
        },
        jshint: {
            all: ['assets/js/**/*.js', 'assets/js-test/**/*.js']
        },
        karma: {
            unit: {
                configFile: 'assets/js-test/karma.conf.js'
            }
        },
        requirejs: {
            compile: {
                options: {
                    optimize: 'uglify2',
                    generateSourceMaps: true,
                    preserveLicenseComments: false
                }
            },
            dev: {
                options: {
                    optimize: 'none'
                }
            },
            options: {
                baseUrl: 'assets/js/',
                name: 'project/main',
                out: 'deploy/site-cookbooks/manchesterio/files/default/static/scripts/project.js',
                paths: {
                    requireLib: '../../bower_components/requirejs/require'
                },
                include: ['requireLib']
            }
        },
        scsslint: {
            all: ['assets/scss/**/*.scss'],
            options: {
                bundleExec: true
            }
        },
        watch: {
            grunt: {
                files: ['Gruntfile.js'],
                options: { reload: true }
            },
            gemfile: {
                files: ['Gemfile'],
                tasks: ['boostrap-compass']
            },
            bower: {
                files: ['bower.json'],
                tasks: ['bower']
            },
            scripts: {
                files: ['assets/js/**/*.js', 'assets/js-test/**/*.js'],
                tasks: ['scripts-dev']
            },
            styles: {
                files: ['assets/scss/compass_config.rb', 'assets/scss/**/*.scss'],
                tasks: ['styles-dev']
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-requirejs');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-karma');
    grunt.loadNpmTasks('grunt-scss-lint');

    grunt.registerTask('bower', function() {
        shelljs.exec('node_modules/bower/bin/bower install');
    });

    grunt.registerTask('bootstrap-compass', function() {
        shelljs.exec('bundle install');
    });

    grunt.registerTask('default', ['bower', 'bootstrap-compass', 'styles', 'scripts']);
    grunt.registerTask('dev', ['bower', 'bootstrap-compass', 'styles-dev', 'scripts-dev', 'watch']);

    grunt.registerTask('scripts', ['karma:unit', 'requirejs:compile', 'jshint:all']);
    grunt.registerTask('scripts-dev', ['karma:unit', 'requirejs:dev', 'jshint:all']);

    grunt.registerTask('styles', ['compass:compile', 'scsslint:all']);
    grunt.registerTask('styles-dev', ['compass:dev', 'scsslint:all']);

};
