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
        }
    });

    grunt.registerTask('dist', ['composer:install:no-dev:optimize-autoloader', 'copy:app']);
    grunt.registerTask('dev', []);

    grunt.loadNpmTasks('grunt-composer');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-watch');

};