module.exports = function(grunt) {

    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        composer: {
            options: {
                cwd: 'manchesterio'
            }
        },

        copy: {
            app: {
                files: [
                    {
                        cwd: 'manchesterio',
                        src: ['public/**', 'src/**', 'vendor/**', 'views/**'],
                        dest: 'deploy/site-cookbooks/manchesterio/files/default/app/',
                        expand: true
                    }
                ]
            }
        },

        phpunit: {
            classes: {
                dir: 'manchesterio/tests'
            },
            options: {
                configuration: 'manchesterio/tests/phpunit.xml',
                colors: true,
                bin: 'manchesterio/vendor/bin/phpunit'
            }
        },

        phpcs: {
            application: {
                dir: ['manchesterio/src/**/*.php', 'manchesterio/tests/**/*.php']
            },
            options: {
                bin: 'manchesterio/vendor/bin/phpcs',
                standard: 'PSR2'
            }
        },

        compass: {
            dist: {
                options: {
                    config: 'manchesterio/assets/config.rb',
                    outputStyle: 'compressed',
                    bundleExec: true
                }
            },
            dev: {
                options: {
                    config: 'manchesterio/assets/config.rb',
                    bundleExec: true
                }
            }
        },

        requirejs: {
            options: {
                baseUrl: "manchesterio/assets/js",
                keepBuildDir: true,
                name: "manchesterio/main",
                out: "deploy/site-cookbooks/manchesterio/files/default/static/js/manchesterio.js",
                paths: {
                    requireLib: 'vendors/require'
                },
                include: ['requireLib']
            },
            dist: {},
            dev: {
                options: {
                    optimize: "none"
                }
            }
        },

        jshint: {
            all: ['manchesterio/assets/js/manchesterio/**']
        },

        karma: {
            dev: {
                options: {
                    configFile: 'manchesterio/assets/js-test/karma.conf.js',
                    browsers: ['PhantomJS'],
                    singleRun: true
                }
            }
        },

        watch: {
            composer: {
                files: 'manchesterio/composer.json',
                tasks: 'composer:update'
            },
            php: {
                files: ['manchesterio/src/**/*.php', 'manchesterio/tests/**/*.php'],
                tasks: ['phpunit', 'phpcs']
            },
            sass: {
                files: 'manchesterio/assets/scss/**',
                tasks: 'compass:dev'
            },
            js: {
                files: ['manchesterio/assets/js/**', 'manchesterio/assets/js-test/**'],
                tasks: ['requirejs:dev', 'karma:dev', 'jshint']
            }
        }
    });

    grunt.registerTask('dist', ['composer:install:no-dev:optimize-autoloader', 'copy:app', 'compass:dist', 'requirejs:dist']);
    grunt.registerTask('dev', ['composer:install', 'phpunit', 'phpcs', 'compass:dev', 'requirejs:dev', 'karma:dev', 'jshint']);

    grunt.loadNpmTasks('grunt-composer');
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-requirejs');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-karma');
    grunt.loadNpmTasks('grunt-phpcs');
    grunt.loadNpmTasks('grunt-phpunit');

};