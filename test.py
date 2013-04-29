import doctest


def test_all(group, moduleNames):
    print "Beginning tests for '%s'" % (group)

    fail, tests = 0, 0
    for m in moduleNames:
        module = (__import__(m, fromlist=['this is a hack!']))
        f, t = doctest.testmod(module, report=True)
        print "  %s out of %s tests passed in '%s'" % (t - f, t, module.__name__)
        fail += f
        tests += t

    print "Summary for '%s': Passed %s out of %s tests\n" % (group, tests - fail, tests)

# Run model tests
test_all('model', [
    'model',
    'model.question',
    'model.tweet',
    'model.poll',
    'model.response',
    'model.session',
    'model.user',
    'model.visit'
])

# Run utils tests
test_all('utils', [
    'utils',
    'utils.alchemystore',
    'utils.auth',
    'utils.csrf',
    'utils.dtutils',
    'utils.flash',
    'utils.inputs',
    'utils.logger',
    'utils.profiler',
    'utils.twttr'
])
