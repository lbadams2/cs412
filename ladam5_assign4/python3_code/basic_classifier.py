from itertools import chain, combinations, count

def gini_index(class_probs):
    summation = 0
    for prob in class_probs.values():
        summation = summation + prob*prob
    return 1 - summation

# https://stackoverflow.com/questions/176918/finding-the-index-of-an-item-given-a-list-containing-it-in-python
def gini_index_attr(attr_val_table, attr_vals_unique, class_probs):
    for item in attr_vals_unique.items():
        unique_vals = item[1]
        attr = item[0]
        subsets = chain.from_iterable(combinations(unique_vals, n) for n in range(1, len(unique_vals)//2))
        for subset in subsets:
            #all_vals = attr_vals_all[attr]
            # split into 2 tables, one with rows having attribute values in the subset
            first_split = {
                tuple_num: {
                    attr: val
                    for inner_attr, inner_val in row.items()
                }
                for tuple_num, row in attr_val_table.items()
                if row[attr] in subset
            }
            second_split_tuple_nums = attr_val_table.keys() ^ first_split.keys()
            second_split = {tuple_num: attr_val_table[tuple_num] for tuple_num in second_split_tuple_nums}
            #index_val_dict = [i for i, j in zip(count(), all_vals) if j in subset]


# https://stackoverflow.com/questions/12229064/mapping-over-values-in-a-python-dictionary
# https://stackoverflow.com/questions/374626/how-can-i-find-all-the-subsets-of-a-set-with-exactly-n-elements
with open('../ladam5_assign4/data/toy.train', 'r') as f:
    class_counter = {}
    class_tuple_dict = {}
    class_probs = {}
    attr_vals_unique = {}
    #attr_vals_full = {}
    attr_vals_table = {}
    i = 1
    for line in f:
        
        elems = line.split(' ')
        class_label = elems[0]
        class_tuple_dict[i] = class_label
        if class_label in class_counter:
            class_counter[class_label] = class_counter[class_label] + 1
        else:
            class_counter[class_label] = 1
        class_probs[class_label] = class_counter[class_label]/i
        #kv_pairs = (kv.split(':') for kv in elems[1:])
        #row = {k: v for k, v in kv_pairs}
        attr_vals_table[i] = {}
        for attr_val in elems[1:]:
            attr_vals = attr_val.split(':')
            attr = attr_vals[0]
            val = attr_vals[1]
            attr_vals_table[i][attr] = val
            key = str(i) + '_' + attr            
            if attr not in attr_vals_unique:
                val_set = set()
                val_set.add(val)
                attr_vals_unique[attr] = val_set
                val_list = []
                val_list.append(val)
                #attr_vals_full[key] = val_list
            else:
                if val not in attr_vals_unique[attr]:
                    attr_vals_unique[attr].add(val)
                #attr_vals_full[key].append(val)
        i = i + 1

    gini_index_attr(attr_vals_table, attr_vals_unique, class_probs)
    
