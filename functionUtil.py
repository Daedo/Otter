from inspect import signature
import itertools
import base64
import random


def get_nr_of_parameters(f):
    return len(signature(f).parameters)


def bool_allocation(n):
    return itertools.product([False, True], repeat=n)


def print_truth_table(f):
    n = get_nr_of_parameters(f)
    letters = map(lambda x: chr( ord('A')+x), range(n))
    print(*letters,"|", "f(...)")
    print("-"*(n+1)*3)
    for a in bool_allocation(n):
        print(*to_nr(a), "|", f(*a))


def to_bool(t):
    def gt_zero(x):
        return x > 0
    return list(map(gt_zero, t))


def to_nr(t):
    out = []
    for i in t:
        if i is False or i == 0:
            out.append("0")
        elif i is True or i == 1:
            out.append("1")
        else:
            out.append("*")
    return tuple(out)


def generate_random_function(parameter_count):
    true_vals = set()
    id_vals = []
    for entry in bool_allocation(parameter_count):

        if int(random.getrandbits(1)) == 0:
            true_vals.add(entry)

            e = ''.join(map(str, to_nr(entry)))
            id_vals.append(e)

    fun_id = base64.b64encode(",".join(id_vals).encode('ascii'))
    fun = generate_function_from_truth_table(true_vals, parameter_count)
    return fun, fun_id


def generate_function_from_fun_id(fun_id, encoded = True):
    if encoded:
        fun_id = base64.b64decode(fun_id)
        fun_id = str(fun_id)[2:-1]
    fun_id = str(fun_id)
    true_strings = list(fun_id.split(","))
    nr_of_parameters = len(true_strings[0])

    true_vals = set()
    for string in true_strings:
        val = []
        for e in string:
            if e == "0":
                val.append(False)
            else:
                val.append(True)
        true_vals.add(tuple(val))
    return generate_function_from_truth_table(true_vals, nr_of_parameters)


def generate_function_from_truth_table(true_vals, nr_of_parameters):
    def gen_fun(*args):
        return args in true_vals
    return wrap_function(gen_fun, nr_of_parameters)


def wrap_function(fun, nr_of_parameters):
    arglist = ["a" * (i + 1) for i in range(nr_of_parameters)]
    argstr = ", ".join(arglist)
    fakefunc = "def fakeGenFun(%s):\n    return gen_fun(%s)\n" % (argstr, argstr)
    fakefunc_code = compile(fakefunc, "fakesource", "exec")
    fakeglobals = {}
    eval(fakefunc_code, {"gen_fun": fun}, fakeglobals)
    return fakeglobals["fakeGenFun"]