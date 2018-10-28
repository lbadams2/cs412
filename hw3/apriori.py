import itertools
import functools

def apriori(min_sup, transactions):
    counter = {}
    for t in transactions:
        items = t.split(' ')
        for item in items:
            if item not in counter:
                counter[item] = 1
            else:
                counter[item] = counter[item] + 1

    # begins with frequent 1-itemsets
    freq_itemsets = {k: v for k,v in counter.items() if v >= min_sup}
    g_freq_itemsets = freq_itemsets
    loop_range = range(2, len(freq_itemsets))
    for k in loop_range:
        itemsets = list(freq_itemsets.keys())
        sorted_itemsets = sorted(itemsets)
        candidate_k_itemsets = apriori_gen(sorted_itemsets)
        counter = {}
        for t in transactions:
            t = t.split(' ')
            sorted_t = sorted([*t])
            # need to order each subset alphabetically
            k_subsets_of_t = set(itertools.combinations(sorted_t, k))
            candidates_in_t = list(set(candidate_k_itemsets) & k_subsets_of_t)
            for c in candidates_in_t:
                if c not in counter:
                    counter[c] = 1
                else:
                    counter[c] = counter[c] + 1
        freq_itemsets = {k: v for k,v in counter.items() if v >= min_sup}
        g_freq_itemsets.update(freq_itemsets)
    return g_freq_itemsets

def apriori_gen(itemset):
    candidate_itemsets = []
    if isinstance(itemset[0], str):
        k = 1
        return list(itertools.combinations(itemset, 2))
    else:
        k = len(itemset[0])        
    loop_range = range(0, len(itemset) - 1)
    for i in loop_range:
        item = itemset[i]
        join_slice = itemset[i+1:]
        for join_item in join_slice:
            # join k-itemsets
            # need to check if first k-2 elements of itemsets are equal
            elem_range = range(k-1)
            joinable = None
            # compare elements of ith and (i+1)th itemset
            for elem_index in elem_range:
                if item[elem_index] == join_item[elem_index]:
                    joinable = True
                else:
                    joinable = None
            if joinable:
                candidate_itemset = list(item)
                candidate_itemset.append(join_item[k-1])
                if has_infrequent_subset(candidate_itemset, itemset):
                    continue
                else:
                    candidate_itemsets.append(tuple(candidate_itemset))
    return candidate_itemsets

def has_infrequent_subset(candidate_itemset, itemsets):
    k_minus = len(itemsets[0])
    for subset in itertools.combinations(candidate_itemset, k_minus):
        if subset not in itemsets:
            return True
    return False

# a pattern is closed if it is frequent and there is no super pattern with the same support
# a pattern is a max pattern if it is frequent and there is no frequent super pattern
def get_closed_or_max_patterns(freq_patterns, isClosed):
    k = 1
    k_patterns = [t for t in freq_patterns.keys() if isinstance(t, str)]
    closed_patterns = list(k_patterns)
    while k_patterns:        
        k = k + 1
        next_patterns = [t for t in freq_patterns.keys() if len(t) == k]
        for pattern in k_patterns:
            for next_pattern in next_patterns:
                if isinstance(pattern, str):
                    set_pattern = set()
                    set_pattern.add(pattern)
                else:
                    set_pattern = set(pattern)
                set_next_pattern = set(next_pattern)
                if isClosed:
                    if set_pattern.issubset(set_next_pattern) and freq_patterns[pattern] == freq_patterns[next_pattern]:                    
                        closed_patterns.remove(pattern)
                        break
                else:
                    if set_pattern.issubset(set_next_pattern):
                        closed_patterns.remove(pattern)
                        break
        k_patterns = [t for t in freq_patterns.keys() if len(t) == k]        
        closed_patterns.extend(k_patterns)
    return closed_patterns

def sort_patterns(a, b):    
    if a[1] > b[1]:
        return -1
    elif a[1] == b[1]:
        a_str = ''.join(a[0])
        b_str = ''.join(b[0])
        if a_str < b_str:
            return -1
        elif a_str > b_str:
            return 1
        else:
            return 0
    else:
        return 1

def print_output(freq_patterns, closed_patterns, max_patterns):
    sorted_patterns = sorted(freq_patterns.items(), key=functools.cmp_to_key(sort_patterns))
    for pattern in sorted_patterns:
        disp = pattern[0]
        if isinstance(pattern[0], tuple):
            disp = ' '.join(pattern[0])
        print(pattern[1], '[' + disp + ']')

f = open('input1.txt', 'r')
lines = f.read().splitlines()
f.close()

min_sup = int(lines[0])
transactions = lines[1:]
freq_itemsets = None
freq_itemsets = apriori(min_sup, transactions)
closed_patterns = get_closed_or_max_patterns(freq_itemsets, True)
max_patterns = get_closed_or_max_patterns(freq_itemsets, False)
print_output(freq_itemsets, closed_patterns, max_patterns)