from classset import *
from testclass import *
from functionUtil import *


class Covering:
    def __init__(self, class_sets : Set[SplitClassSet] = []):
        self._class_sets = class_sets
        self._level_of_uniqueness = None
        self._len = None

    def get_class_sets(self):
        return self._class_sets

    def set_class_sets(self, class_sets):
        self._class_sets = class_sets
        self._level_of_uniqueness = None
        self._len = None

    class_sets = property(get_class_sets, set_class_sets)

    def __repr__(self):
        out = "<"
        for cSet in self.class_sets:
            out += "\n"+str(cSet)
        return out + ">"

    def get_level_of_uniqueness(self):
        if self._level_of_uniqueness is None:
            self._level_of_uniqueness = 0
            for class_set in self.class_sets:
                self._level_of_uniqueness += class_set.level_of_uniqueness()
        return self._level_of_uniqueness

    level_of_uniqueness = property(get_level_of_uniqueness)

    def is_tree_covering(self) -> bool:
        for class_set in self.class_sets:
            if not class_set.is_pure():
                return False
        return True

    def __len__(self):
        if self._len is None:
            self._len = 0
            for class_set in self.class_sets:
                self._len += len(class_set)
        return self._len

    def __eq__(self, other):
        return self._class_sets == other._class_sets

    def __lt__(self, other):
        return False  # len(self.class_sets) < len(other.class_sets)

    def __hash__(self):
        return tuple(self.class_sets).__hash__()

    def is_goal(self):
        return self.is_tree_covering() or self._len == self.level_of_uniqueness


def split_input(function):
    n = get_nr_of_parameters(function)
    pos = []
    neg = []
    for x in bool_allocation(n):
        if function(*x):
            pos.append(x)
        else:
            neg.append(x)
    return pos, neg


def combine(x,y):
    """
    Combines Testclasses X and Y
    Returns (NewElement or None, Delete X from Worklist, Delete Y from Worklist)
    Any Class that replaces an essential class is itself essential.
    """
    deleteX = True
    deleteY = True
    merge = False
    workout = []
    for i in range(len(x)):
        if x[i] != y[i]:
            if x[i] == '*':
                workout.append(y[i])
                deleteX = False
            elif y[i] == '*':
                workout.append(x[i])
                deleteY = False
            elif not merge:
                merge = True
                workout.append('*')
            else:
                #The two inputs are too different
                return (None,False,False)
        else:
            workout.append(x[i])
    workout = tuple(workout)

    if merge:
        if deleteX and deleteY:
            return (workout,True,True) # Merge
        elif deleteX or deleteY:
            return (workout,deleteX,deleteY) # Promote X/Y
        else:
            return (workout,False,False) # Generate Z
    else:
        if deleteX and deleteY:
            # We ignore redundancies
            return (None, False, False)
        else:
            # Delete X or Y
            return (None, deleteX, deleteY)


def minimize(tuple_list: List[Tuple[Any]]):
    current = set()
    new = list(tuple_list)
    remove = set()
    while len(new) > 0:
        nextNew = set()

        #Current x New
        for class_x in current:
            if class_x in remove:
                    continue
            for class_y in new:
                if class_y in remove:
                    continue
                class_z, delete_x, delete_y = combine(class_x, class_y)
                if class_z is not None and class_z not in current and class_z not in remove:
                    nextNew.add(class_z)
                if delete_y:
                    remove.add(class_y)
                if delete_x:
                    remove.add(class_x)
                    break

        #New x New
        for index_x, class_x in enumerate(new):
            if class_x in remove:
                    continue
            for class_y in new[index_x+1:]:
                if class_y in remove:
                    continue
                class_z, delete_x, delete_y = combine(class_x, class_y)
                if class_z is not None and class_z not in current and class_z not in remove:
                    nextNew.add(class_z)
                if delete_x:
                    remove.add(class_x)
                if delete_y:
                    remove.add(class_y)
        #Update
        current = (current|set(new))-remove
        new = list(nextNew)
    return list(current)


def generate_covering(pos: List[Tuple[Any]], neg: List[Tuple[Any]]):
    pos_classes = list(map(TestClass, pos))
    neg_classes = list(map(TestClass, neg))
    split_class = get_split_class_set(pos_classes, neg_classes)
    return Covering(set([split_class]))


def get_general_covering(function) -> Covering:
    # If we had more information about f we could prune the coverings
    pos, neg = split_input(function)
    pos = minimize(pos)
    neg = minimize(neg)
    return generate_covering(pos,neg)
