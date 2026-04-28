# editdistance.py - 纯 Python 替代方案，绕过 C++ 编译
def eval(a, b):
    if a == b: return 0
    if len(a) < len(b): a, b = b, a
    if not b: return len(a)
    previous_row = range(len(b) + 1)
    for i, c1 in enumerate(a):
        current_row = [i + 1]
        for j, c2 in enumerate(b):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def distance(a, b):
    return eval(a, b)
