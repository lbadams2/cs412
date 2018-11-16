from itertools import chain, combinations, count

def gini_index(class_probs):
    summation = 0
    for prob in class_probs.values():
        summation = summation + prob*prob
    return 1 - summation

# https://stackoverflow.com/questions/176918/finding-the-index-of-an-item-given-a-list-containing-it-in-python
def gini_index_attr(attr_vals_all, attr_vals_unique, class_probs):
    for item in attr_vals_unique.items():
        unique_vals = item[1]
        attr = item[0]
        subsets = chain.from_iterable(combinations(unique_vals, n) for n in range(1, len(unique_vals)))
        for subset in subsets:
            all_vals = attr_vals_all[attr]
            index_val_dict = [i for i, j in zip(count(), all_vals) if j in subset]


# https://stackoverflow.com/questions/12229064/mapping-over-values-in-a-python-dictionary
# https://stackoverflow.com/questions/374626/how-can-i-find-all-the-subsets-of-a-set-with-exactly-n-elements
with open('balance.scale.train', 'r') as f:
    class_counter = {}
    class_probs = {}
    attr_vals_unique = {}
    attr_vals_full = {}
    i = 0
    for line in f:
        i = i + 1
        elems = line.split(' ')
        class_label = elems[0]
        if class_label in class_counter:
            class_counter[class_label] = class_counter[class_label] + 1
        else:
            class_counter[class_label] = 1
        class_probs[class_label] = class_counter[class_label]/i
        for attr_val in elems[1:]:
            attr_vals = attr_val.split(':')
            attr = attr_vals[0]
            val = attr_vals[2]
            if attr not in attr_vals_unique:
                val_set = set()
                val_set.add(val)
                attr_vals_unique[attr] = val_set
                val_list = []
                val_list.append(val)
                attr_vals_full[attr] = val_list
            else:
                if val not in attr_vals_unique[attr]:
                    attr_vals_unique[attr].add(val)
                attr_vals_full[attr].append(val)

    gini_index_attr(attr_vals_full, attr_vals_unique, class_probs)
    
