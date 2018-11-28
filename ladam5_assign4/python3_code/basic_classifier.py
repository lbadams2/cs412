from itertools import chain, combinations
import sys

class Node:
    def __init__(self, data):
        self.l = None
        self.r = None
        self.data = data
        self.class_label = None

class Split_Data:
    def __init__(self, data, attr, attr_vals_unique, class_probs, val_subset, is_positive):
        self.data = data
        self.attr = attr
        self.attr_vals_unique = attr_vals_unique
        self.class_probs = class_probs
        self.subset = val_subset
        self.is_positive_branch = is_positive

def gini_index(class_probs):
    summation = 0
    for prob in class_probs.values():
        summation = summation + prob*prob
    return 1 - summation

def add_split_data(row, tuple_num, split_table, unique_vals, class_counter):
    split_table[tuple_num] = row
    for row_attr, val in row.items():
        if row_attr == 'class':
            continue
        if row_attr not in unique_vals:
            val_set = set()
            val_set.add(val)
            unique_vals[row_attr] = val_set
        else:
            if val not in unique_vals[row_attr]:
                unique_vals[row_attr].add(val)
    class_label = row['class']
    if class_label not in class_counter:
        class_counter[class_label] = 1
    else:
        class_counter[class_label] = class_counter[class_label] + 1

def create_split_data(table, subset, second_subset, split_attr):
    first_split_table = {}
    second_split_table = {}

    first_split_attr_unique_vals = {}
    second_split_attr_unique_vals = {}

    first_class_counter = {}
    second_class_counter = {}

    first_split_count = 0
    second_split_count = 0
    for tuple_num, v in table.items():
        # first split
        if v[split_attr] in subset:
            add_split_data(v, tuple_num, first_split_table, first_split_attr_unique_vals, first_class_counter)
            first_split_count = first_split_count + 1
        # second split
        else:
            add_split_data(v, tuple_num, second_split_table, second_split_attr_unique_vals, second_class_counter)
            second_split_count = second_split_count + 1

    # all tuples have same value for split_attr if subset is size 1
    # won't be able to split on that attr subsequently, remove split_attr from unique vals table
    if len(subset) == 1:
        first_split_attr_unique_vals.pop(split_attr)
    if len(second_subset) == 1:
        second_split_attr_unique_vals.pop(split_attr)

    first_class_probs = {k: v/first_split_count for k, v in first_class_counter.items()}
    second_class_probs = {k: v/second_split_count for k, v in second_class_counter.items()}
    
    first_split_data = Split_Data(first_split_table, split_attr, first_split_attr_unique_vals, first_class_probs, subset, True)
    second_split_data = Split_Data(second_split_table, split_attr, second_split_attr_unique_vals, second_class_probs, second_subset, False)
    return first_split_data, second_split_data

def gini_index_attr(attr_val_table, attr_vals_unique):
    # maybe optimize to not call len()
    total_count = len(attr_val_table.keys())
    min_attr_gini_index = None
    best_split = None
    no_unique_vals = False

    for attr, unique_vals in attr_vals_unique.items():
        subsets = None
        # can't split table on attr if it has same value for all tuples
        if len(unique_vals) == 1:
            no_unique_vals = True
            continue
        elif len(unique_vals) == 2 or len(unique_vals) == 3:
            subsets = unique_vals
        else:
            subsets = chain.from_iterable(combinations(unique_vals, n) for n in range(1, len(unique_vals)//2))
        subset_gini_index_min = None
        best_attr_split = None

        for subset in subsets:
            #first_split = {tuple_num: attr_val_table[tuple_num] for tuple_num, v in attr_val_table.items() if v[attr] in subset}
            #second_split = {k: attr_val_table[k] for k in attr_val_table.keys() ^ first_split.keys()}
            subset = set(subset)
            second_subset = subset ^ unique_vals
            split_data = create_split_data(attr_val_table, subset, second_subset, attr)
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
    
    return best_split, no_unique_vals

def generate_decision_tree(table, attr_list, class_probs):
    node = Node(table)
    if len(class_probs.keys()) == 1:
        node.class_label = list(class_probs.keys())[0]
        return node

    # how to break tie
    majority_class = max(class_probs, key=class_probs.get)
    if not attr_list:        
        node.class_label = majority_class
        return node    

    gini_results = gini_index_attr(table, attr_list)
    best_split = gini_results[0]
    # rows in table are identical
    if not best_split and gini_results[1]:
        node.class_label = majority_class
        return node

    yes_split = best_split[0]
    no_split = best_split[1]
    
    # combine split data and node classes
    if not yes_split.data:
        leaf_node = Node(None)
        leaf_node.class_label = majority_class
        node.l = leaf_node
    else:
        node.l = generate_decision_tree(yes_split.data, yes_split.attr_vals_unique, yes_split.class_probs)

    if not no_split.data:
        leaf_node = Node(None)
        leaf_node.class_label = majority_class
        node.r = leaf_node
    else:
        node.r = generate_decision_tree(no_split.data, no_split.attr_vals_unique, no_split.class_probs)

    return node


def process_training_file(training_file):
    total_class_probs = {}
    attr_vals_unique = {}
    attr_vals_table = {}
    with open(training_file, 'r') as f:
        total_class_counter = {}
        i = 0
        for line in f:
            i = i + 1
            line = line.strip()       
            elems = line.split(' ')
            class_label = elems[0]

            if class_label not in total_class_counter:
                total_class_counter[class_label] = 1
            else:
                total_class_counter[class_label] = total_class_counter[class_label] + 1
            #total_class_probs[class_label] = total_class_counter[class_label] / i

            attr_vals_table[i] = {}
            attr_vals_table[i]['class'] = class_label

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
            
        total_class_probs = {k: v/i for k, v in total_class_counter.items()}

    return attr_vals_table, attr_vals_unique, total_class_probs


def classify_test_file(decision_tree, test_file):
    with open(test_file, 'r') as f:
        for line in f:
            temp_tree = decision_tree
            line = line.strip()       
            elems = line.split(' ')
            class_label = elems[0]
            # need to combine node and split data classes
            #split_attr = temp_tree.data.


# 'ladam5_assign4/data/nursery.train'
training_file = sys.argv[1]
test_file = sys.argv[2]
processed_data = process_training_file(training_file)
processed_table = processed_data[0]
processed_unique_vals = processed_data[1]
processed_class_probs = processed_data[2]
tree = generate_decision_tree(processed_table, processed_unique_vals, processed_class_probs)
classify_test_file(tree, test_file)