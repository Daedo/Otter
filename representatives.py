from covering import *
import math


def get_representatives(covering: Covering) -> List[SplitClassSet]:
    return explore(covering.class_sets.__iter__().__next__(), math.inf)[0]


def explore(class_set: SplitClassSet, cutoff: int) -> Tuple[List[SplitClassSet], int]:
    if cutoff <= 0:
        return ()
    level = class_set.level_of_uniqueness()
    if cutoff < level:
        return ()
    if class_set.is_pure():
        return [class_set], level

    result = []
    for index in class_set.get_split_order():
        class_a, class_b = class_set.split(index)
        level_b = class_b.level_of_uniqueness()
        res_a = explore(class_a, cutoff - level_b)
        if len(res_a) > 0:
            level_a = res_a[1]
            res_b = explore(class_b, cutoff - level_a)
            if len(res_b) > 0:
                level_b = res_b[1]
                new_level = level_a + level_b
                if new_level < cutoff:
                    cutoff = new_level
                    result = []
                result.extend(res_a[0])
                result.extend(res_b[0])
    if len(result) > 0 and cutoff == level:
        result = [class_set]
    return result, cutoff
