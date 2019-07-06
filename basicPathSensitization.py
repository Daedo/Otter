from ceg import CEGNode, merge_traces, remove_duplicates
from typing import List


def get_testcases(CEG: List[CEGNode]):
    # 1. Get all Causes for each Effect & Get all inner Node from Cause to Effect
    effects = list(filter(lambda x: x.is_effect(), CEG))  # type: List[CEGNode]
    inner_node_list = []
    cause_list = []
    for effect in effects:
        cause, inner = effect.get_causes()
        cause_list.append(cause)
        inner_node_list.append(inner)

    tests = []
    for i in range(len(effects)):
        effect = effects[i]
        causes = cause_list[i]
        inner_nodes = inner_node_list[i]
        for cause in causes:
            inner = inner_nodes[cause]
            traces = trace_from_cause_to_effect(cause, effect, inner)
            if len(traces) > 0:
                min_trace = traces[0]
                min_true = count_trues(traces[0])
                max_trace = traces[0]
                max_true = min_true
                for trace in traces:
                    count = count_trues(trace)
                    if count < min_true:
                        min_true = count
                        min_trace = trace
                    if count > max_true:
                        max_true = count
                        max_trace = trace
                # TODO: In Theory we would have to check whether the path following the trace is negated or not
                # and then set the values to that instead of true/false
                min_trace = dict(min_trace)
                max_trace = dict(max_trace)
                min_trace[cause] = True
                max_trace[cause] = False
                tests.append(min_trace)
                tests.append(max_trace)

    full_cause = list(filter(lambda x: x.is_cause(), CEG)) # type: List[CEGNode]
    full_true = {}
    full_false = {}
    for cause in full_cause:
        full_false[cause] = False
        full_true[cause] = True
    tests.append(full_true)
    tests.append(full_false)
    # 3. Add the (1,...,1), (0,...,0) Testcase to the set
    # Remove Duplicates
    return remove_duplicates(tests)


def count_trues(trace):
    result = 0
    for cause in trace:
        if trace[cause]:
            result += 1
    return result


def trace_from_cause_to_effect(cause: CEGNode, effect: CEGNode, inner_nodes: List[CEGNode]):
    if cause == effect:
        return [{}]
    result = []
    for arc in cause.outgoing:
        if arc.end in inner_nodes or arc.end == effect:
            const_traces = arc.end.get_constrained_traces(arc.start)
            sub_traces = trace_from_cause_to_effect(arc.end, effect, inner_nodes)
            result.extend(merge_traces(const_traces, sub_traces))
            # Merge classes
    return result
