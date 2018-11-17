from itertools import chain, combinations, count

def gini_index(class_probs):
    summation = 0
    for prob in class_probs.values():
        summation = summation + prob*prob
    return 1 - summation

# https://stackoverflow.com/questions/176918/finding-the-index-of-an-item-given-a-list-containing-it-in-python
def gini_index_attr(attr_val_table, attr_vals_unique, class_tuple_dict):
    total_count = len(attr_val_table.keys())
    min_attr_gini_index = None
    min_attr_subset = None
    min_attr = None
    for item in attr_vals_unique.items():
        unique_vals = item[1]
        attr = item[0]
        subsets = chain.from_iterable(combinations(unique_vals, n) for n in range(1, len(unique_vals)//2))
        subset_gini_index_min = None
        min_subset = None
        for subset in subsets:
            #first_split_tuple_nums = {tuple_num for tuple_num, v in attr_val_table.items() if v[attr] in subset}
            #first_split = {k: attr_val_table[k] for k in first_split_tuple_nums}
            first_split = {tuple_num: attr_val_table[tuple_num] for tuple_num, v in attr_val_table.items() if v[attr] in subset}
            second_split = {k: attr_val_table[k] for k in attr_val_table.keys() ^ first_split.keys()}
            first_split_class_probs = {}
            second_split_class_probs = {}
            for k in class_tuple_dict.keys():
                first_split_class_probs[k] = len(first_split.keys() & class_tuple_dict[k])/len(class_tuple_dict[k])
                second_split_class_probs[k] = len(second_split.keys() & class_tuple_dict[k])/len(class_tuple_dict[k])
            first_split_ratio = len(first_split.keys())/total_count
            second_split_ratio = len(second_split.keys())/total_count
            subset_gini_index = first_split_ratio * gini_index(first_split_class_probs) + second_split_ratio * gini_index(second_split_class_probs)
            if not subset_gini_index_min or subset_gini_index < subset_gini_index_min:
                subset_gini_index_min = subset_gini_index
                min_subset = subset
        if not min_attr_gini_index or subset_gini_index_min < min_attr_gini_index:
            min_attr_gini_index = subset_gini_index_min
            min_attr_subset = min_subset
            min_attr = attr
    return min_attr, min_attr_subset



# https://stackoverflow.com/questions/12229064/mapping-over-values-in-a-python-dictionary
# https://stackoverflow.com/questions/374626/how-can-i-find-all-the-subsets-of-a-set-with-exactly-n-elements
with open('../ladam5_assign4/data/toy.train', 'r') as f:
    #class_counter = {}
    class_tuple_dict = {}
    #class_probs = {}
    attr_vals_unique = {}
    #attr_vals_full = {}
    attr_vals_table = {}
    i = 1
    for line in f:
        line = line.strip()       
        elems = line.split(' ')
        class_label = elems[0]
        if class_label not in class_tuple_dict:
            class_tuple_dict[class_label] = set()
            class_tuple_dict[class_label].add(i)
        else:
            class_tuple_dict[class_label].add(i)
        #if class_label in class_counter:
        #    class_counter[class_label] = class_counter[class_label] + 1
        #else:
        #    class_counter[class_label] = 1
        #class_probs[class_label] = class_counter[class_label]/i
        #kv_pairs = (kv.split(':') for kv in elems[1:])
        #row = {k: v for k, v in kv_pairs}
        attr_vals_table[i] = {}
        for attr_val in elems[1:]:
            attr_vals = attr_val.split(':')
            attr = attr_vals[0]
            val = attr_vals[1]
            attr_vals_table[i][attr] = val
            if attr not in attr_vals_unique:
                val_set = set()
                val_set.add(val)
                attr_vals_unique[attr] = val_set
                #val_list = []
                #val_list.append(val)
                #attr_vals_full[key] = val_list
            else:
                if val not in attr_vals_unique[attr]:
                    attr_vals_unique[attr].add(val)
                #attr_vals_full[key].append(val)
        i = i + 1

    attr_and_split = gini_index_attr(attr_vals_table, attr_vals_unique, class_tuple_dict)
    
