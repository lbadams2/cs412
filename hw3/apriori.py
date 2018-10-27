import itertools

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
    loop_range = range(2, len(freq_itemsets))
    for k in loop_range:
        itemsets = list(freq_itemsets.keys())
        k_minus_one_itemsets = [item for item in itemsets if len(item) == k-1]
        k_minus_one_itemsets = sorted(k_minus_one_itemsets)
        candidate_k_itemsets = apriori_gen(k_minus_one_itemsets)
        for t in transactions:
            sorted_t = sorted([*t.replace(" ", "")])
            # need to order each subset alphabetically
            k_subsets_of_t = set(itertools.combinations(sorted_t, k))
            candidates_in_t = list(set(candidate_k_itemsets) & k_subsets_of_t)
            for c in candidates_in_t:
                if c not in counter:
                    counter[c] = 1
                else:
                    counter[c] = counter[c] + 1
        freq_itemsets = {k: v for k,v in counter.items() if v >= min_sup}
    return freq_itemsets

def apriori_gen(itemset):
    candidate_itemsets = []
    k = len(itemset[0])
    if k == 1:
        return list(itertools.combinations(itemset, 2))
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


f = open('input2.txt', 'r')
lines = f.read().splitlines()
f.close()

min_sup = int(lines[0])
transactions = lines[1:]
freq_itemsets = None
freq_itemsets = apriori(min_sup, transactions)
print(freq_itemsets)