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
        }
    });

    grunt.registerTask('dist', ['composer:install:no-dev:optimize-autoloader', 'copy:app']);
    grunt.registerTask('dev', ['composer:install', 'phpunit', 'phpcs']);

    grunt.loadNpmTasks('grunt-composer');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-phpcs');
    grunt.loadNpmTasks('grunt-phpunit');

};