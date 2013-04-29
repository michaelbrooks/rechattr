from __future__ import print_function
import doctest

def test_all(group, moduleNames):
    output = ["Beginning tests for '%s'" % (group)]

    fail, tests = 0, 0
    for m in moduleNames:
        module = (__import__(m, fromlist=['this is a hack!']))
        f, t = doctest.testmod(module, report=True)
        output.append("  %s out of %s tests passed in '%s'" % (t - f, t, module.__name__))
        fail += f
        tests += t

    output.append("Summary for '%s': Passed %s out of %s tests: %d failures" % (group, tests - fail, tests, fail))

    print()
    map(print, output)

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
