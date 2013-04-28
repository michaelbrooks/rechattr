import web

profile_stats = []

def sql(app):
    print "Loading sqltap SQL profiler"
    import sqltap

    # A controller to serve sql profiler results
    class sql_profiler_report:
        def GET(self, queryPath=None):
            global profile_stats

            input = web.input()

            if queryPath:
                def path_filter(qstats):
                    # check the path for this stats object
                    return qstats.user_context[0] == queryPath

                print "Showing statistics for path: %s" %(queryPath)
                stats = filter(path_filter, profile_stats)
            else:
                print "Showing all statistics"
                stats = profile_stats

            if 'clear' in input:
                profile_stats = [x for x in profile_stats if x not in stats]
                return 'Statistics cleared!'

            # save the stacks because sqltap clobbers them - we might want them again later
            for qs in stats:
                qs._stack = qs.stack

            report = sqltap.report(stats)

            # restore the stacks
            for qs in stats:
                qs.stack = qs._stack

            return report

    app.add_mapping('/~sql_profiler(.*)', sql_profiler_report)

    # the context function for stats
    def sqltap_context(*args):
        return (web.ctx.path, web.ctx.query)

    # start the profiler
    sqltap.start(user_context_fn=sqltap_context)

    def process_sql_profiler(handler):
        try:
            return handler()
        finally:

            collectible = not web.ctx.path.startswith(('/~sql_profiler', '/favicon.ico'))
            # save the statistics
            stats = sqltap.collect()
            if collectible:
                print "Profiler recording statistics for: %s" %(web.ctx.path)
                profile_stats.extend(stats)

    app.add_processor(process_sql_profiler)