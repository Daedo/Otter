from typing import List
from functionUtil import bool_allocation, generate_function_from_truth_table, to_nr
import base64


class CEGNode:
    def __init__(self, is_or=False, **kwargs):
        self.incoming = []  # type: List[CEGArc]
        self.outgoing = []  # type: List[CEGArc]
        self.is_or = is_or
        self._positive_traces = None
        self._negative_traces = None
        self.tag = None
        if 'tag' in kwargs:
            self.tag = str(kwargs['tag'])

    def arc_to(self, to: 'CEGNode', negate: bool = False):
        arc = CEGArc(self, to, negate)
        self.outgoing.append(arc)
        to.incoming.append(arc)

    def is_cause(self):
        return len(self.incoming) == 0

    def is_effect(self):
        return len(self.outgoing) == 0

    def __repr__(self):
        if self.tag is None:
            return super.__repr__()
        return "Node \""+self.tag+"\""

    def get_child_functions(self):
        def negate(fun):
            def negated_fun(cause_values):
                return not fun(cause_values)
            return negated_fun

        result = []
        for incoming_arc in self.incoming:
            norm_fun = incoming_arc.start.get_boolean_function()
            if incoming_arc.is_negated:
                norm_fun = negate(norm_fun)
            result.append(norm_fun)
        return result

    def get_boolean_function(self):
        def cause_function(cause_values):
            if self not in cause_values:
                return False
            return cause_values[self]

        def and_function(cause_values):
            for fun in self.get_child_functions():
                if not fun(cause_values) :
                    return False
            return True

        def or_function(cause_values):
            for fun in self.get_child_functions():
                if fun(cause_values):
                    return True
            return False

        if self.is_cause():
            return cause_function
        if self.is_or:
            return or_function
        return and_function

    def get_causes(self):
        if self.is_cause():
            return set([self]), {self: set()}
        result = set()
        inner_nodes = {} # type: Dict[Set['CEGNode']]
        for incoming_arc in self.incoming:
            causes, inner = incoming_arc.start.get_causes()
            result |= causes
            for inner_node in inner:
                if inner_node in inner_nodes:
                    inner_nodes[inner_node] |= inner[inner_node]
                else:
                    inner_nodes[inner_node] = inner[inner_node]
        if not self.is_effect():
            for inner in inner_nodes:
                inner_nodes[inner].add(self)
        return result, inner_nodes

    def _get_traces(self, value):
        if self.is_cause():
            return [{self: value}]
        if self.is_or == value:
            # Any Match if we want a True OR-Node or a False AND-Node
            # Any of the parents must have the target value
            matched_traces = [{}]
            unmatched_traces = [{}]
            is_first_merge = True

            for arc in self.incoming:
                goal_value = value != arc.is_negated
                matched_arc_traces = arc.start.get_traces(goal_value)
                unmatched_arc_traces = arc.start.get_traces(not goal_value)
                new_matched_traces = merge_traces(matched_arc_traces, matched_traces)           # True or True
                new_matched_traces.extend(merge_traces(matched_arc_traces, unmatched_traces))   # True or False
                if not is_first_merge:
                    new_matched_traces.extend(merge_traces(unmatched_arc_traces, matched_traces))   # False or True

                matched_traces = new_matched_traces
                unmatched_traces = merge_traces(unmatched_arc_traces, unmatched_traces)         # False or False
                is_first_merge = False
        else:
            # All of the parents must have the target value
            matched_traces = [{}]
            for arc in self.incoming:
                goal_value = value != arc.is_negated
                matched_arc_traces = arc.start.get_traces(goal_value)
                matched_traces = merge_traces(matched_arc_traces, matched_traces)               # True and True
        return remove_duplicates(matched_traces)

    def get_traces(self, value):
        if value:
            if self._positive_traces is None:
                self._positive_traces = self._get_traces(value)
            return self._positive_traces
        else:
            if self._negative_traces is None:
                self._negative_traces = self._get_traces(value)
            return self._negative_traces

    def get_positive_traces(self):
        return self.get_traces(True)

    def get_negative_traces(self):
        return self.get_traces(False)

    def get_constrained_traces(self, cause):
        matched_traces = [{}]
        for arc in self.incoming:
            if arc.start == cause:
                continue
            # AND Node: All Nodes != cause are set to 1 (0 when negated)
            # OR Node: All Nodes != cause are set to 0 (1 when negated)
            goal_value = (not self.is_or) != arc.is_negated
            matched_arc_traces = arc.start.get_traces(goal_value)
            matched_traces = merge_traces(matched_arc_traces, matched_traces)  # True and True
        return matched_traces


class CEGArc:
    def __init__(self, start, end, negate=False):
        self.start = start  # type: CEGNode
        self.end = end  # type: CEGNode
        self.is_negated = negate  # type: bool


def merge_trace_pair(trace_a, trace_b):
    result = dict(trace_a)
    for elem in trace_b:
        if elem in trace_a and trace_a[elem] != trace_b[elem]:
            return None
        result[elem] = trace_b[elem]
    return result


def merge_traces(trace_list_a, trace_list_b):
    result = []
    for trace_a in trace_list_a:
        for trace_b in trace_list_b:
            merge = merge_trace_pair(trace_a, trace_b)
            if merge is not None:
                result.append(merge)
    return result


def remove_duplicates(lst):
    result = []
    for i in range(len(lst)):
        if lst[i] not in lst[i+1:]:
            result.append(lst[i])
    return result


def get_cause_function(effect_node: CEGNode):
    causes, _ = effect_node.get_causes()
    causes = list(causes)
    fun = effect_node.get_boolean_function()
    print("Causes:", len(causes))

    def cause_function(*args):
        mapped = {}
        for i in range(len(args)):
            mapped[causes[i]] = args[i]
        return fun(mapped)

    truth_table = set()
    id_vals = []
    for inp in bool_allocation(len(causes)):
        if cause_function(*inp):
            truth_table.add(inp)
            e = ''.join(map(str, to_nr(inp)))
            id_vals.append(e)
    fun_id = base64.b64encode(",".join(id_vals).encode('ascii'))
    return generate_function_from_truth_table(truth_table, len(causes)), fun_id
