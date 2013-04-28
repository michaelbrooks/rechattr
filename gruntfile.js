module.exports = function (grunt) {

    var taskConfig = {
        pkg: grunt.file.readJSON('package.json'),
        dirs: {
            src: "static/",
            src_js: "static/js/",
            src_css: "static/css/",
            dist: "dist/",
            dist_js: "dist/js",
            dist_css: "dist/css"
        },

        clean: {
            dist: ['<%=dirs.dist%>']
        },

        // Configure the copy task to move files from the development to production folders
        copy: {
            dist: {
                files: [
                    {
                        expand: true,
                        cwd: '<%=dirs.src%>',
                        src: ['favicon.png', 'img/**'],
                        dest: '<%=dirs.dist%>/'
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
                    src: ['<%=dirs.src_css%>/**.css', '!<%=dirs.src_css%>/vendor/**.css']
                }
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
                    '<%=dirs.src_js%>/**.js',
                    '!<%=dirs.src_js%>/vendor/**.js'
                ]
            }
        },

        //This is sort-of like a regular requirejs config, but it is expanded
        //into valid configuration by a function below
        requirejs: {
            js: {
                options: {
                    baseUrl: "<%=dirs.src_js%>",
                    mainConfigFile: "<%=dirs.src_js%>/require-config.js",

                    //Compress the js files
                    optimize: "uglify",

                    //All the built layers will use almond.
                    name: 'vendor/almond',

                    //Exclude jquery and the dummy config file
                    exclude: ['jquery', 'config']
                },
                modules: ['poll', 'edit', 'create']
            },
            css: {
                options: {
                    optimizeCss: 'standard'
                },
                modules: ['create', 'edit', 'main', 'myevents', 'poll', 'welcome']
            }
        },

        cachebuster: {
            options: {
                format: 'json',
                basedir: '<%=dirs.dist%>',
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
                src: ['<%=dirs.dist%>/**'],
                dest: 'static_map.py'
            }
        },

        watch: {
            options: {
                interrupt: true
            },
            gruntfile: {
                files: ['<%= jshint.gruntfile.src %>'],
                tasks: ['jshint:gruntfile']
            },
            scripts: {
                files: ['<%= jshint.dist.src %>'],
                tasks: ['jshint:dist', 'buildjs']
            },
            styles: {
                files: ['<%= csslint.dist.src %>'],
                tasks: ['csslint', 'buildcss']
            }
        }
    };


    function buildRequireJSConfig() {
        var _ = require('underscore');

        var from = taskConfig.requirejs;
        var result = {};

        //Register the shorthand tasks
        _.each(from, function(config, key) {
            grunt.registerTask('build' + key, config.modules.map(function(name) {
                return 'requirejs:' + key + '-' + name;
            }));
        });

        //Go through the JS modules
        from.js.modules.forEach(function(name) {
            result['js-' + name] = {
                options: _.defaults({
                    include: [name],
                    out: '<%= dirs.dist_js %>/' + name + '.js'
                }, from.js.options)
            }
        });

        //Go through the CSS modules
        from.css.modules.forEach(function(name) {
            result['css-' + name] = {
                options: _.defaults({
                    cssIn: '<%=dirs.src_css%>/' + name + '.css',
                    out: '<%=dirs.dist_css%>/' + name + '.css'
                }, from.css.options)
            };
        });

        taskConfig.requirejs = result;
    }

    buildRequireJSConfig();

    grunt.initConfig(taskConfig);


    // Load plugins here
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-copy');

    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-csslint');

    grunt.loadNpmTasks('grunt-contrib-requirejs');

    grunt.loadNpmTasks('grunt-cachebuster');

    // Define your tasks here
    grunt.registerTask('dist', ['clean', 'buildjs', 'buildcss', 'copy', 'cachebuster']);
    grunt.registerTask('default', ['clean', 'jshint', 'csslint', 'buildjs', 'buildcss', 'copy', 'cachebuster']);
};
