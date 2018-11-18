from itertools import chain, combinations

class Node:
    def __init__(self, data):
        self.l = None
        self.r = None
        self.data = data
        self.class_label = None

class Split_Data:
    def __init__(self, data, attr, attr_vals_unique, class_dict, class_probs):
        self.data = data
        self.attr = attr
        self.attr_vals_unique = attr_vals_unique
        self.class_dict = class_dict
        self.class_probs = class_probs

def gini_index(class_probs):
    summation = 0
    for prob in class_probs.values():
        summation = summation + prob*prob
    return 1 - summation

# if subset is size 1 don't include in attr list
def create_split_data(table, subset, split_attr, class_dict):
    split_table = {}
    split_table_attr_unique_vals = {}
    new_class_dict = {}
    class_probs = {}
    class_counter = {}
    i = 1
    for tuple_num, v in table.items():
        # first split
        if v[attr] in subset:
            row = table[tuple_num]
            split_table[tuple_num] = row
            for row_attr, val in row.items():
                if row_attr not in split_table_attr_unique_vals:
                    val_set = set()
                    val_set.add(val)
                    split_table_attr_unique_vals[row_attr] = val_set
                else:
                    if val not in split_table_attr_unique_vals[row_attr]:
                        split_table_attr_unique_vals[val]
            class_label = class_dict[tuple_num]
            new_class_dict[tuple_num] = class_label
            if not class_counter[class_label]:
                class_counter[class_label] = 1
            else:
                class_counter[class_label] = class_counter[class_label] + 1
            class_probs[class_label] = class_counter[class_label] / i
            i = i + 1
        # second split
        else:
            
    if len(subset) == 1:
        # need to convert subset to correct type
        split_table_attr_unique_vals.pop(subset)
    return Split_Data(split_table, split_attr, split_table_attr_unique_vals, class_dict, class_probs)

def gini_index_attr(attr_val_table, attr_vals_unique, class_tuple_dict):
    total_count = len(attr_val_table.keys())
    min_attr_gini_index = None
    min_attr = None
    first_split= None
    second_split = None
    splitting_subset = None

    for item in attr_vals_unique.items():
        unique_vals = item[1]
        attr = item[0]
        subsets = chain.from_iterable(combinations(unique_vals, n) for n in range(1, len(unique_vals)//2))
        subset_gini_index_min = None
        attr_splitting_subset = None

        for subset in subsets:
            #first_split = {tuple_num: attr_val_table[tuple_num] for tuple_num, v in attr_val_table.items() if v[attr] in subset}
            #second_split = {k: attr_val_table[k] for k in attr_val_table.keys() ^ first_split.keys()}
            first_split_data = create_split_data(attr_val_table, subset, attr, class_tuple_dict)
            
                
            
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
                attr_splitting_subset = subset

        if not min_attr_gini_index or subset_gini_index_min < min_attr_gini_index:
            min_attr_gini_index = subset_gini_index_min
            min_attr = attr
            splitting_subset = attr_splitting_subset
    
    return min_attr, first_split, second_split, splitting_subset

def generate_decision_tree(table, attr_list, class_dict):
    node = Node(table)
    if len(class_dict.keys()) == 1:
        node.class_label = class_dict.keys()[0]
        return node

    majority_class = max(class_dict, key=len(class_dict.get))
    if not attr_list:        
        node.class_label = majority_class
        return node    

    attr_and_splits = gini_index_attr(table, attr_list, class_dict)
    yes_split = attr_and_splits[1]
    no_split = attr_and_splits[2]
    
    # could optimize to remove attr from attr_list if split is from subset of length 1, would be the yes_split, or no if length 2
    if not yes_split:
        leaf_node = Node(None)
        leaf_node.class_label = majority_class
        node.l = leaf_node
    else:
        # need to update attr_list and class_dict before call
        node.l = generate_decision_tree(yes_split, attr_list, class_dict)

    if not no_split:
        leaf_node = Node(None)
        leaf_node.class_label = majority_class
        node.r = leaf_node
    else:
        # need to update attr_list and class_dict before call
        node.r = generate_decision_tree(no_split, attr_list, class_dict)

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