from testcases import *
from representatives import *
import cProfile


def test_function(a, b, c):
    return (a != b) or (b != c)


def run_pipeline(function):
    print("Requirement Function")
    print_truth_table(function)
    print()

    covering = get_general_covering(function)
    print("General Covering")
    print(covering)
    print()

    representatives = get_representatives(covering)
    print("Found %i Representatives" % len(representatives))
    rep = list(representatives)
    for i in range(min(3, len(rep))):
        print(rep[i])
    print()

    representatives = [Covering(representatives)]

    pos_tests, neg_tests = get_test_cases(representatives)
    print("Found %i Testclasses" % (len(pos_tests)+len(neg_tests)))

    for posTest in pos_tests:
        print(testclass_to_string(posTest, 1))
    for negTest in neg_tests:
        print(testclass_to_string(negTest, 0))


def profile_pipeline(function):
    local_vars = {'debug_pipeline': run_pipeline,'function': function}
    global_vars = {}
    cProfile.runctx('debug_pipeline(function)', local_vars, global_vars)
    print("Done")


if __name__ == "__main__":
    run_pipeline(test_function)
