from covering import *
import itertools


class ProblemInstance:
    def __init__(self):
        self.class_encoding = {}
        self.test_encoding = {}
        self.inverse_test_encoding = {}
        self.X = {}
        self.Y = {}

    def add_constraint(self, test_class: TestClass, uniques: List[Set[Any]]):
        c_encoding = "c"+str(len(self.class_encoding))
        self.class_encoding[c_encoding] = test_class
        self.X[c_encoding] = set()
        for unique in uniques:
            if unique not in self.inverse_test_encoding:
                t_encoding = "t"+str(len(self.test_encoding))
                self.test_encoding[t_encoding] = unique
                self.inverse_test_encoding[unique] = t_encoding
                self.Y[t_encoding] = set()
            t_encoding = self.inverse_test_encoding[unique]
            self.X[c_encoding].add(t_encoding)
            self.Y[t_encoding].add(c_encoding)

    def add_constraints(self, class_set: ClassSet):
        uniques = class_set.uniques
        for i, u_set in enumerate(uniques):
            if len(u_set) > 0:
                self.add_constraint(class_set.classes[i], u_set)

    def compress(self):
        compX = {}
        closed = set()
        remKey = set()

        for key in self.X:
            valRep = tuple(sorted(self.X[key]))
            if valRep not in closed:
                compX[key] = self.X[key]
                closed.add(valRep)
            else:
                remKey.add(key)
        self.X = compX
        for rKey in remKey:
            del self.class_encoding[rKey]
        for key in self.Y:
            self.Y[key] -= remKey

    def solve(self):
        # 1. If a class only contains a single testcase, select it.
        work_x = dict(self.X)
        work_y = dict(self.Y)

        solution = set()
        for c in work_x:
            if len(work_x[c]) == 1:
                solution.add(next(iter(work_x[c])))
        # 2. Remove the selected testcases and all classes that contain it
        for test in solution:
            for c in work_y[test]:
                if c in work_x:
                    del work_x[c]
            del work_y[test]

        if len(work_x) == 0:
            return self.decode_solution(solution)

        # 3. Bruteforce
        subsets = work_y.keys()
        full = set(work_x.keys())
        for n in range(1, len(work_y)):
            found = False
            for combination in itertools.combinations(subsets, n):
                u = set().union(*map(lambda x: work_y[x], combination))
                if full == u:
                    solution.update(combination)
                    found = True
                    break
            if found:
                break

        return self.decode_solution(solution)

    def decode_solution(self, solution):
        return list(map(lambda x: self.test_encoding[x], solution))

    def __repr__(self):
        out = "Set Cover Problem:\n"
        out += "Class Encoding:\n"
        for key in self.class_encoding:
            out += "\t" + str(key) + " - " + str(self.class_encoding[key]) + "\n"
        out += "\nTest Encoding:\n"
        for key in self.test_encoding:
            out += "\t" + str(key) + " - " + testclass_to_string(self.test_encoding[key]) + "\n"
        out += "\n X: \n"
        for key in self.X:
            out += "\t" + str(key) + " - " + str(self.X[key]) + "\n"
        out += "\n Y:"
        for key in self.Y:
            out += "\n\t" + str(key) + " - " + str(self.Y[key])
        return out


def get_test_cases(representatives: List[Covering]):
    pos_problem = ProblemInstance()
    neg_problem = ProblemInstance()

    for rep in representatives:
        for class_set in rep.class_sets:
            pos_problem.add_constraints(class_set.pos_class)
            neg_problem.add_constraints(class_set.neg_class)
    pos_problem.compress()
    pos_problem.compress()
    pos_solve = pos_problem.solve()
    neg_solve = neg_problem.solve()
    return pos_solve, neg_solve


def testclass_to_string(tClass, outcome = None):
    def repMapper(x):
        if x==True:
            return 1
        elif x==False:
            return 0
        else:
            return x

    classString = str(tuple(map(repMapper, tClass)))
    if outcome is not None:
        return "%s => %s" % (classString, repMapper(outcome))
    else:
        return classString