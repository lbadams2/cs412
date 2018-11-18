from itertools import chain, combinations

class Node:
    def __init__(self, data):
        self.l = None
        self.r = None
        self.data = data
        self.class_label = None

class Split_Data:
    def __init__(self, data, attr, attr_vals_unique, class_dict, class_probs, val_subset, is_positive):
        self.data = data
        self.attr = attr
        self.attr_vals_unique = attr_vals_unique
        self.class_dict = class_dict
        self.class_probs = class_probs
        self.subset = val_subset
        self.is_positive_branch = is_positive

def gini_index(class_probs):
    summation = 0
    for prob in class_probs.values():
        summation = summation + prob*prob
    return 1 - summation

def add_split_data(parent_table, tuple_num, split_table, unique_vals, class_dict, class_probs, class_counter):
    row = parent_table[tuple_num]
    split_table[tuple_num] = row
    for row_attr, val in row.items():
        if row_attr not in unique_vals:
            val_set = set()
            val_set.add(val)
            unique_vals[row_attr] = val_set
        else:
            if val not in unique_vals[row_attr]:
                unique_vals[val]
    class_label = class_dict[tuple_num]
    class_dict[tuple_num] = class_label
    if not class_counter[class_label]:
        class_counter[class_label] = 1
    else:
        class_counter[class_label] = class_counter[class_label] + 1
    class_probs[class_label] = class_counter[class_label] / len(class_counter.values())

def create_split_data(table, subset, second_subset, split_attr, class_dict):
    first_split_table = {}
    second_split_table = {}

    first_split_attr_unique_vals = {}
    second_split_attr_unique_vals = {}

    first_new_class_dict = {}
    second_new_class_dict = {}

    first_class_probs = {}
    second_class_probs = {}

    first_class_counter = {}
    second_class_counter = {}

    for tuple_num, v in table.items():
        # first split
        if v[attr] in subset:
            add_split_data(table, tuple_num, first_split_table, first_split_attr_unique_vals, first_new_class_dict, first_class_probs, first_class_counter)
        # second split
        else:
            add_split_data(table, tuple_num, second_split_table, second_split_attr_unique_vals, second_new_class_dict, second_class_probs, second_class_counter)

    if len(subset) == 1:
        # need to convert subset to correct type
        first_split_attr_unique_vals.pop(subset)
    if len(second_subset) == 1:
        second_split_attr_unique_vals.pop(second_subset)
    
    first_split_data = Split_Data(first_split_table, attr, first_split_attr_unique_vals, first_new_class_dict, first_class_probs, subset, True)
    second_split_data = Split_Data(second_split_table, attr, second_split_attr_unique_vals, second_new_class_dict, second_class_probs, second_subset, False)
    return first_split_data, second_split_data

def gini_index_attr(attr_val_table, attr_vals_unique, class_tuple_dict):
    total_count = len(attr_val_table.keys())
    min_attr_gini_index = None
    best_split = None

    for item in attr_vals_unique.items():
        unique_vals = item[1]
        attr = item[0]
        subsets = chain.from_iterable(combinations(unique_vals, n) for n in range(1, len(unique_vals)//2))
        subset_gini_index_min = None
        best_attr_split = None

        for subset in subsets:
            #first_split = {tuple_num: attr_val_table[tuple_num] for tuple_num, v in attr_val_table.items() if v[attr] in subset}
            #second_split = {k: attr_val_table[k] for k in attr_val_table.keys() ^ first_split.keys()}
            second_subset = subset ^ unique_vals
            split_data = create_split_data(attr_val_table, subset, second_subset, attr, class_tuple_dict)
            first_split_data = split_data[0]
            second_split_data = split_data[1]

            first_split_ratio = len(first_split_data.data.keys())/total_count
            second_split_ratio = len(second_split_data.data.keys())/total_count
            subset_gini_index = first_split_ratio * gini_index(first_split_data.class_probs) + second_split_ratio * gini_index(second_split_data.class_probs)

            if not subset_gini_index_min or subset_gini_index < subset_gini_index_min:
                subset_gini_index_min = subset_gini_index
                best_attr_split = split_data

        if not min_attr_gini_index or subset_gini_index_min < min_attr_gini_index:
            min_attr_gini_index = subset_gini_index_min
            best_split = best_attr_split
    
    return best_split

def generate_decision_tree(table, attr_list, class_dict):
    node = Node(table)
    if len(class_dict.keys()) == 1:
        node.class_label = class_dict.keys()[0]
        return node

    majority_class = max(class_dict, key=len(class_dict.get))
    if not attr_list:        
        node.class_label = majority_class
        return node    

    best_split = gini_index_attr(table, attr_list, class_dict)
    yes_split = best_split[0]
    no_split = best_split[1]
    
    # combine split data and node classes
    if not yes_split.data:
        leaf_node = Node(None)
        leaf_node.class_label = majority_class
        node.l = leaf_node
    else:
        node.l = generate_decision_tree(yes_split.data, yes_split.attr_vals_unique, yes_split.class_dict)

    if not no_split.data:
        leaf_node = Node(None)
        leaf_node.class_label = majority_class
        node.r = leaf_node
    else:
        node.r = generate_decision_tree(no_split.data, no_split.attr_vals_unique, no_split.class_dict)

    return node


class_tuple_dict = {}
attr_vals_unique = {}
attr_vals_table = {}
with open('../ladam5_assign4/data/toy.train', 'r') as f:
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
            else:
                if val not in attr_vals_unique[attr]:
                    attr_vals_unique[attr].add(val)
        i = i + 1

tree = generate_decision_tree(attr_vals_table, attr_vals_unique, class_tuple_dict)