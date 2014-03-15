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
                        src: ['app/**', 'bootstrap/**', 'public/**', 'vendor/**'],
                        dest: 'deploy/site-cookbooks/manchesterio/files/default/app/',
                        expand: true
                    }
                ]
            }
        },

        phpunit: {
            classes: {
                dir: 'manchesterio/app/tests'
            },
            options: {
                configuration: 'manchesterio/app/tests/phpunit.xml',
                colors: true,
                bin: 'manchesterio/vendor/bin/phpunit'
            }
        },

        phpcs: {
            application: {
                dir: ['manchesterio/app/**/*.php']
            },
            options: {
                bin: 'manchesterio/vendor/bin/phpcs',
                standard: 'PSR2',
                ignore: 'views/*.php'
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

        watch: {
            composer: {
                files: 'manchesterio/composer.json',
                tasks: 'composer:update'
            },
            php: {
                files: 'manchesterio/app/**',
                tasks: ['phpunit', 'phpcs']
            },
            sass: {
                files: 'manchesterio/assets/scss/**',
                tasks: 'compass:dev'
            },
            js: {
                files: 'manchesterio/assets/js/**',
                tasks: ['requirejs:dev', 'jshint']
            }
        }
    });

    grunt.registerTask('dist', ['composer:install:no-dev:optimize-autoloader', 'copy:app', 'compass:dist', 'requirejs:dist']);
    grunt.registerTask('dev', ['composer:install', 'phpunit', 'phpcs', 'compass:dev', 'requirejs:dev', 'jshint']);

    grunt.loadNpmTasks('grunt-composer');
    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-requirejs');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-phpcs');
    grunt.loadNpmTasks('grunt-phpunit');

};