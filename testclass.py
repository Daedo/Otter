import itertools
from typing import Set, Tuple, Any


class TestClass:
    def __init__(self, tup: tuple, domain: set = None):
        self.tup = tup
        self._domain = domain

    def get_domain(self) -> Set[Any]:
        if self._domain is None:
            domain_template = []
            for elem in self.tup:
                if elem == '*':
                    domain_template.append([True,False])
                else:
                    domain_template.append([elem])
            self._domain = set(itertools.product(*domain_template))
        return self._domain

    domain = property(get_domain)

    def is_subset(self, other: 'TestClass') -> bool:
        return self.domain.issubset(other.domain)

    def split(self, index) -> ('TestClass', 'TestClass'):
        assert self.tup[index] == '*'

        pos = list(self.tup)
        neg = list(self.tup)
        pos[index] = True
        neg[index] = False

        pos_domain = set()
        neg_domain = set()
        for element in self.domain:
            if element[index] is True:
                pos_domain.add(element)
            else:
                neg_domain.add(element)
        return TestClass(pos, pos_domain), TestClass(neg, neg_domain)

    def __repr__(self):
        def rep_mapper(x):
            if x is True:
                return 1
            elif x is False:
                return 0
            else:
                return x

        return str(tuple(map(rep_mapper, self.tup)))

def get_trivial_class(tup: Tuple[Any]):
    dom = set([tuple])
    return TestClass(tup, dom)