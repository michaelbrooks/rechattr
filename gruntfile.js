module.exports = function (grunt) {

    // Configuration goes here
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),

        clean: {
            dist: ['dist']
        },

        // Configure the copy task to move files from the development to production folders
        copy: {
            dist: {
                files: [{
                    expand: true,
                    cwd: 'static/',
                    src: ['favicon.png', 'img/**'],
                    dest: 'dist/'
                }]
            }
        },

        imagemin: {
            options: {
                optimizationLevel: 1
            },
            dist: {
                files: [{
                    expand: true,
                    cwd: 'static/',
                    src: ['favicon.png', 'img/**'],
                    dest: 'dist/'
                }]
            }
        },

        csslint: {
            options: {
                import: 0
            },
            dist: {
                files: {
                    src: ['static/css/**.css', '!static/css/vendor/**.css']
                }
            }
        },

        cssmin: {
            options: {
                root: 'static/css',
                keepBreaks: true
            },
            dist: {
                files: [
                    {
                        expand: true,
                        cwd: 'static/css/',
                        src: ['*.css'],
                        dest: 'dist/css'
                    }
                ]
            }
        },

        jshint: {

            // Some typical JSHint options and globals
            options: {
                curly: true,
                eqeqeq: true,
                immed: true,
                latedef: true,
                newcap: true,
                noarg: true,
                sub: true,
                undef: true,
                boss: true,
                eqnull: true,
                browser: true
            },

            gruntfile: {
                options: {
                    globals: {
                        'module': true
                    }
                },
                src: 'gruntfile.js'
            },

            dist: {
                options: {
                    globals: {
                        browser: true,
                        define: true
                    }
                },
                src: [
                    'static/js/**.js',
                    '!static/js/vendor/**.js'
                ]
            }
        },

        requirejs: {
            options: {
                baseUrl: "static/js",
                mainConfigFile: "static/js/require-config.js",
                optimize: "uglify",

                //All the built layers will use almond.
                name: 'vendor/almond'
            },
            poll: {
                options: {
                    include: ['poll'],
                    exclude: ['jquery', 'config'],
                    out: 'dist/js/poll.js'
                }
            },
            edit: {
                options: {
                    include: ['edit'],
                    exclude: ['jquery', 'config'],
                    out: 'dist/js/edit.js'
                }
            },
            create: {
                options: {
                    include: ['create'],
                    exclude: ['jquery', 'config'],
                    out: 'dist/js/create.js'
                }
            }
        },

        cachebuster: {
            options: {
                format: 'json',
                basedir: 'dist/',
                banner: "map = ",
                formatter: function(hashes, banner) {
                    return banner + JSON.stringify(hashes, null, 2);
                },
                complete: function(hashes) {
                    //Unixize the paths
                    var result = {};
                    for (path in hashes) {
                        result[path.replace(/\\/g,'/')] = hashes[path];
                    }
                    return result;
                }
            },
            dist: {
                src: ['dist/**'],
                dest: ['static_map.py']
            }
        },

        watch: {
            options: {
                interrupt: true
            },
            scripts: {
                files: ['gruntfile.js', 'static/js/**.js', '!static/js/vendor/**.js'],
                tasks: ['jshint', 'requirejs']
            },
            styles: {
                files: ['static/css/**.css', '!static/css/vendor/**.css'],
                tasks: ['csslint', 'cssmin']
            }
        }
    });

    // Load plugins here
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-copy');

    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-csslint');

    grunt.loadNpmTasks('grunt-contrib-requirejs');
    grunt.loadNpmTasks('grunt-contrib-cssmin');
    grunt.loadNpmTasks('grunt-contrib-imagemin');

    grunt.loadNpmTasks('grunt-cachebuster');

    // Define your tasks here
    grunt.registerTask('default', ['clean', 'jshint', 'csslint', 'requirejs', 'cssmin', 'copy', 'imagemin', 'cachebuster']);
};