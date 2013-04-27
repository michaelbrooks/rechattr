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
                files: [
                    {
                        expand: true,
                        cwd: 'static/',
                        src: ['favicon.png', 'img/**'],
                        dest: 'dist/'
                    }
                ]
            }
        },

        imagemin: {
            options: {
                optimizationLevel: 1
            },
            dist: {
                files: [
                    {
                        expand: true,
                        cwd: 'static/',
                        src: ['favicon.png', 'img/**'],
                        dest: 'dist/'
                    }
                ]
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

        enhancecss: {
            options: {
                root: 'dist/css/',
                stamp: true
            },
            dist: {
                files: [ {
                    expand: true,
                    cwd: 'dist/css/',
                    src: ['*.css'],
                    dest: 'dist/css/'
                }]
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
                        cwd: 'static/css',
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
                formatter: function (hashes, banner) {
                    return banner + JSON.stringify(hashes, null, 2);
                },
                complete: function (hashes) {
                    //Unixize the paths
                    var result = {};
                    for (path in hashes) {
                        result[path.replace(/\\/g, '/')] = hashes[path];
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

    (function () {
        var fs = require('fs');
        var path = require('path');
        var util = require('util');
        var EnhanceCSS = require('enhance-css');

        var enhancer = function (source, argv, callback) {
            var options = {
                source: null,
                rootPath: null,
                assetHosts: null,
                pregzip: false,
                noEmbed: false,
                cryptedStamp: false,
                stamp: false
            };

            if (!source) {
                throw "Source required";
            }

            if (argv.noEmbed)
                options.noEmbed = argv.noEmbed;
            if (argv.assetHosts)
                options.assetHosts = argv.assetHosts;
            if (argv.pregzip)
                options.pregzip = argv.pregzip;
            if (argv.cryptedStamp)
                options.cryptedStamp = argv.cryptedStamp;
            if (argv.stamp)
                options.stamp = argv.stamp;

            options.rootPath = argv.root || process.cwd();

            var e = new EnhanceCSS({ rootPath: options.rootPath,
                assetHosts: options.assetHosts,
                noEmbedVersion: options.noEmbed,
                cryptedStamp: options.cryptedStamp,
                pregzip: options.pregzip,
                stamp: options.stamp
            });

            e.process(source, function (error, data) {
                if (error)
                    throw error;

                var result;
                if (options.noEmbed) {
                    result = data.notEmbedded;
                }
                else {
                    result = data.embedded;
                }

                if (options.pregzip) {
                    callback(result.compresed);
                } else {
                    callback(result.plain);
                }
            });
        }


        var helper = require('grunt-lib-contrib').init(grunt);

        grunt.registerMultiTask('enhancecss', 'Enhance CSS files.', function () {
            var options = this.options({
                report: false
            });

            this.files.forEach(function (f) {
                var source = f.src.filter(function (filepath) {
                    // Warn on and remove invalid source files (if nonull was set).
                    if (!grunt.file.exists(filepath)) {
                        grunt.log.warn('Source file "' + filepath + '" not found.');
                        return false;
                    } else {
                        return true;
                    }
                })
                    .map(grunt.file.read)
                    .join(grunt.util.normalizelf(grunt.util.linefeed));

                try {
                    enhancer(source, options, function (data) {

                        if (data.length < 1) {
                            grunt.log.warn('Destination not written because enhanced CSS was empty.');
                        } else {
                            if (options.banner) {
                                data = options.banner + grunt.util.linefeed + data;
                            }

                            grunt.file.write(f.dest, data);
                            grunt.log.writeln('File ' + f.dest + ' created.');
                            if (options.report) {
                                helper.minMaxInfo(data, source, options.report);
                            }
                        }
                    });
                } catch (e) {
                    grunt.log.error(e);
                    grunt.fail.warn('css enhancement failed.');
                }
            });

        });
    })();

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