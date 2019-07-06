from typing import Set, List, Any
from testclass import *
import operator


class ClassSet:
    def __init__(self, classes: List[TestClass]=[]):
        self._classes = classes  # type: List[TestClass]
        # Cache Unique Elements
        self._uniques = None # type: List[Set[Any]]
        self._level = None
        self._domain = None

    def get_classes(self):
        return self._classes

    def set_classes(self, classes):
        self._classes = classes
        self._uniques = None  # type: List[Set[Any]]
        self._level = None
        self._domain = None

    classes = property(get_classes, set_classes)

    def get_unique_elements(self) -> List[Set[any]]:
        # assume the classes are subsetfree
        if self._uniques is None:
            self._uniques = []  # type: list[set[tuple[bool]]]
            for elem in self.classes:
                self._uniques.append(set(elem.domain))

            for index_a in range(len(self.classes)):
                for index_b in range(index_a+1, len(self.classes)):
                    self._uniques[index_a] -= self.classes[index_b].domain
                    self._uniques[index_b] -= self.classes[index_a].domain
        return self._uniques

    uniques = property(get_unique_elements)

    def split(self, index: int) -> 'ClassSet,ClassSet':
        positive = []
        negative = []

        for test_class in self.classes:
            if test_class.tup[index] == 0:
                negative.append(test_class)
            elif test_class.tup[index] == 1:
                positive.append(test_class)
            else:
                pos, neg = test_class.split(index)
                positive.append(pos)
                negative.append(neg)

        pos = ClassSet(positive)
        pos._clean_split()
        neg = ClassSet(negative)
        neg._clean_split()
        return pos,neg

    def get_level_of_uniqueness(self) -> int:
        if self._level is None:
            # Compute Unique Elements
            self._level = 0
            for unique_set in self.uniques:
                if len(unique_set) > 0:
                    self._level += 1
        return self._level

    level_of_uniqueness = property(get_level_of_uniqueness)

    def get_domain(self) -> Set[any]:
        if self._domain is None:
            result = set()
            for dom_class in self.classes:
                result |= dom_class.domain
            self._domain = result
        return self._domain

    domain = property(get_domain)

    def _clean_split(self):
        self._filter_subsets()
        keep = []
        part_domain = set()
        for index, unique in enumerate(self.uniques):
            if len(unique) > 0:
                keep.append(self.classes[index])
                part_domain |= self.classes[index].domain

        if part_domain == self.domain:
            self.classes = keep
            return
        missing = self.domain - part_domain
        for index, miss_class in enumerate(self.classes):
            if not miss_class.domain.isdisjoint(missing):
                keep.append(self.classes[index])
        self.classes = keep

    def _filter_subsets(self):
        rem = set()
        for i, class_a in enumerate(self.classes):
            if class_a in rem:
                continue

            for j, class_b in enumerate(self.classes):
                if i == j:
                    continue
                if class_a.is_subset(class_b):
                    rem.add(class_a)
                    break
        for rem_class in rem:
            self._classes.remove(rem_class)

    def __len__(self):
        return len(self._classes)


class SplitClassSet:
    def __init__(self, positive: ClassSet, negative: ClassSet):
        self.pos_class = positive
        self.neg_class = negative

        len_pos = len(self.pos_class)
        len_neg = len(self.neg_class)
        self.total_len = len_neg + len_pos
        self. pure = (len_pos == 0 or len_neg == 0 or (len_pos == 1 and len_neg == 1))
        self._level = None

    def level_of_uniqueness(self) -> int:
        if self._level is None:
            self._level = self.pos_class.level_of_uniqueness
            self._level += self.neg_class.level_of_uniqueness
        return self._level

    def split(self, index):
        pos_left, pos_right = self.pos_class.split(index)
        neg_left, neg_right = self.neg_class.split(index)
        return SplitClassSet(pos_left, neg_left), SplitClassSet(pos_right, neg_right)

    def is_pure(self):
        return self.pure

    def __repr__(self):
        out = "Pos:\n"
        for cl in self.pos_class.classes:
            out += str(cl) + "=> 1\n"
        out += "Neg:\n"
        for cl in self.neg_class.classes:
            out += str(cl) + "=> 0\n"
        return out

    def __len__(self):
        return self.total_len

    def get_heuristic_counts(self):
        star_count = None
        one_count = None
        zero_count = None

        classes = set(self.pos_class.classes) | set(self.neg_class.classes)
        for t_class in classes:
            tup = t_class.tup
            if star_count is None:
                star_count = [0] * len(tup)
                one_count = [0] * len(tup)
                zero_count = [0] * len(tup)
            for i in range(len(tup)):
                if tup[i] is True:
                    one_count[i] += 1
                elif tup[i] is False:
                    zero_count[i] += 1
                else:
                    star_count[i] += 1
        return list(zip(zero_count, one_count, star_count))

    def get_split_order(self):
        count = self.get_heuristic_counts()
        # Add index
        order = list(map(lambda x: [x[0]] + list(x[1]), list(enumerate(count))))
        # Remove all entries that have no stars or that are pure
        order = list(filter(lambda x: x[3] != 0 or (x[2] != 0 and x[1] != 0), order))
        order.sort(key=operator.itemgetter(3))
        return list(map(lambda x: x[0], order))


def get_split_class_set(positive: List[TestClass], negative: List[TestClass]):
    return SplitClassSet(ClassSet(positive), ClassSet(negative))