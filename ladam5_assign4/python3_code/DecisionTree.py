from itertools import chain, combinations
import sys
from random import randint
from timeit import default_timer as timer

class Node:
    def __init__(self, data):
        self.l = None
        self.r = None
        self.data = data
        self.class_label = None
        self.split_attr = None
        self.left_split_vals = None
        self.right_split_vals = None

class Full_Node:
    def __init__(self, data):
        self.children = []
        self.data = data
        self.split_attr = None
        self.val = None
        self.child_vals = set()
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
    for prob in class_probs:
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

def gini_index_attr_full(attr_val_table, attr_vals_unique):
    # maybe optimize to not call len()
    total_count = len(attr_val_table.keys())
    min_attr_gini_index = None
    no_unique_vals = False

    split_tables = {}
    class_counts = {}
    split_counts = {}
    split_class_probs = {}
    split_attr_vals_unique = {}

    for tuple_num, v in attr_val_table.items():
        for attr, val in v.items():
            # don't split on attributes already split on or with only one value
            if attr not in attr_vals_unique:
                continue
            if attr not in split_tables:
                split_tables[attr] = {}
                split_tables[attr][val] = {}
                split_tables[attr][val][tuple_num] = {}
                split_tables[attr][val][tuple_num] = v
                class_counts[attr] = {}
                class_counts[attr][val] = {}
                class_counts[attr][val][v['class']] = 1
                split_counts[attr] = {}
                split_counts[attr][val] = 1
                split_class_probs[attr] = {}
                split_class_probs[attr][val] = {}
                split_class_probs[attr][val][v['class']] = 0
                split_attr_vals_unique[attr] = {}
                split_attr_vals_unique[attr][val] = {}
            elif val not in split_tables[attr]:
                split_tables[attr][val] = {}
                split_tables[attr][val][tuple_num] = {}
                split_tables[attr][val][tuple_num] = v
                class_counts[attr][val] = {}
                class_counts[attr][val][v['class']] = 1
                split_counts[attr][val] = 1
                split_class_probs[attr][val] = {}
                split_class_probs[attr][val][v['class']] = 0
                split_attr_vals_unique[attr][val] = {}
            elif tuple_num not in split_tables[attr][val]:
                split_tables[attr][val][tuple_num] = {}
                split_tables[attr][val][tuple_num] = v
                if v['class'] not in class_counts[attr][val]:
                    class_counts[attr][val][v['class']] = 1
                else:
                    class_counts[attr][val][v['class']] = class_counts[attr][val][v['class']] + 1
                split_counts[attr][val] = split_counts[attr][val] + 1
                split_class_probs[attr][val][v['class']] = 0
        
            for other_attr, other_val in v.items():
                if other_attr == 'class':
                    continue
                if other_attr != attr:
                    if other_attr not in split_attr_vals_unique[attr][val]:
                        split_attr_vals_unique[attr][val][other_attr] = set()
                        split_attr_vals_unique[attr][val][other_attr].add(other_val)
                    else:
                        if other_val not in split_attr_vals_unique[attr][val][other_attr]:
                            split_attr_vals_unique[attr][val][other_attr].add(other_val)    
    
    for class_count_attr, class_count_attr_val_dict in class_counts.items():
        for class_count_attr_val, class_count_dict in class_count_attr_val_dict.items():
            for class_label, class_count_num in class_count_dict.items():
                #class_count = class_counts[class_count_attr][class_count_attr_val][class_label]
                split_count = split_counts[class_count_attr][class_count_attr_val]
                split_class_probs[class_count_attr][class_count_attr_val][class_label] = class_count_num / split_count

    '''
    for class_count_attr in class_counts:
        for class_count_attr_val in class_count_attr:
            for class_count_class_val in class_count_attr_val:
                class_count = class_counts[class_count_attr][class_count_attr_val][class_count_class_val]
                split_count = split_counts[class_count_attr][class_count_attr_val]
                split_class_probs[class_count_attr][class_count_attr_val][class_count_class_val] = class_count / split_count
    '''

    # delete unique vals of length 1
    for outer_vals in split_attr_vals_unique.values():
        for unique_val_dicts in outer_vals.values():
            temp_dict = unique_val_dicts.copy()
            for unique_attr, unique_vals in temp_dict.items():                 
                if len(unique_vals) < 2:
                    del unique_val_dicts[unique_attr]

    attr_gini_indexes = {}
    min_attr = None
    min_attr_gini_index = -1
    for attr, vals in attr_vals_unique.items():
        for val in vals:
            probs = []
            for prob in split_class_probs[attr][val].values():
                probs.append(prob)
            gini_index_val = gini_index(probs)
            split_ratio = split_counts[attr][val] / total_count
            split_gini_index = split_ratio * gini_index_val
            if attr not in attr_gini_indexes:
                attr_gini_indexes[attr] = split_gini_index
            else:
                attr_gini_indexes[attr] = attr_gini_indexes[attr] + split_gini_index
            
            if not min_attr:
                min_attr = attr
                min_attr_gini_index = attr_gini_indexes[attr]
            else:
                if attr_gini_indexes[attr] < min_attr_gini_index:
                    min_attr = attr
                    min_attr_gini_index = attr_gini_indexes[attr]
    
    splits = split_tables[min_attr]
    split_data_list = []
    for val, table in splits.items():
        split_data = Split_Data(table, min_attr, split_attr_vals_unique[min_attr][val], split_class_probs[min_attr][val], set(val), False)
        split_data_list.append(split_data)

    return split_data_list

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
            subset_gini_index = first_split_ratio * gini_index(first_split_data.class_probs.values()) + second_split_ratio * gini_index(second_split_data.class_probs.values())

            if not subset_gini_index_min or subset_gini_index < subset_gini_index_min:
                subset_gini_index_min = subset_gini_index
                best_attr_split = split_data

        if not min_attr_gini_index or subset_gini_index_min < min_attr_gini_index:
            min_attr_gini_index = subset_gini_index_min
            best_split = best_attr_split
    
    return best_split, no_unique_vals

def generate_full_decision_tree(table, attr_list, class_probs, val):
    node = Full_Node(table)
    node.val = val
    if len(class_probs.keys()) == 1:
        node.class_label = list(class_probs.keys())[0]
        return node

    # how to break tie
    majority_class = max(class_probs, key=class_probs.get)
    if not attr_list:        
        node.class_label = majority_class
        return node

    split_data_list = gini_index_attr_full(table, attr_list)
    split_attr = split_data_list[0].attr
    node.split_attr = split_attr
    for split_data in split_data_list:
        node.child_vals.update(split_data.subset)
        if not split_data.data:
            leaf_node = Full_Node(None)
            leaf_node.class_label = majority_class
            leaf_node.split_attr = split_data.attr
            leaf_node.val = split_data.subset
            node.children.append(leaf_node)
        else:
            split_val = split_data.subset.pop()
            split_data.subset.add(split_val)
            node.children.append(generate_full_decision_tree(split_data.data, split_data.attr_vals_unique, split_data.class_probs, split_val))
    
    return node


def generate_binary_decision_tree(table, attr_list, class_probs):
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
    node.split_attr = yes_split.attr
    node.left_split_vals = yes_split.subset
    node.right_split_vals = no_split.subset
    
    # combine split data and node classes
    if not yes_split.data:
        leaf_node = Node(None)
        leaf_node.class_label = majority_class
        node.l = leaf_node
    else:
        node.l = generate_binary_decision_tree(yes_split.data, yes_split.attr_vals_unique, yes_split.class_probs)

    if not no_split.data:
        leaf_node = Node(None)
        leaf_node.class_label = majority_class
        node.r = leaf_node
    else:
        node.r = generate_binary_decision_tree(no_split.data, no_split.attr_vals_unique, no_split.class_probs)

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


def classify_test_file_full(decision_tree, test_file):
    confusion_matrix = {}
    with open(test_file, 'r') as f:
        for line in f:
            temp_tree = decision_tree
            line = line.strip()       
            elems = line.split(' ')
            class_label = elems[0]
            tuple_dict = {}
            for elem in elems[1:]:
                kv = elem.split(':')
                tuple_dict[kv[0]] = kv[1]
            while not temp_tree.class_label:
                tuple_val = tuple_dict[temp_tree.split_attr]
                if tuple_val in temp_tree.child_vals:
                    for node in temp_tree.children:
                        if tuple_val == node.val:
                            temp_tree = node
                            break
                else:
                    num = randint(0, len(temp_tree.children) - 1)
                    temp_tree = temp_tree.children[num]
            
            predicted_class = temp_tree.class_label
            if class_label not in confusion_matrix:
                confusion_matrix[class_label] = {}
            if predicted_class not in confusion_matrix[class_label]:
                confusion_matrix[class_label][predicted_class] = 1
            else:
                confusion_matrix[class_label][predicted_class] = confusion_matrix[class_label][predicted_class] + 1

    actual_labels = confusion_matrix.keys()
    for actual_label in actual_labels:
        predicted_labels = confusion_matrix[actual_label].keys()
        diff = actual_labels ^ predicted_labels
        for missing_label in diff:
            confusion_matrix[actual_label][missing_label] = 0
        
    return confusion_matrix
    

def classify_test_file_binary(decision_tree, test_file):
    confusion_matrix = {}
    with open(test_file, 'r') as f:
        for line in f:
            temp_tree = decision_tree
            line = line.strip()       
            elems = line.split(' ')
            class_label = elems[0]
            tuple_dict = {}
            for elem in elems[1:]:
                kv = elem.split(':')
                tuple_dict[kv[0]] = kv[1]
            while not temp_tree.class_label:
                tuple_val = tuple_dict[temp_tree.split_attr]
                if tuple_val in temp_tree.left_split_vals:
                    temp_tree = temp_tree.l
                    continue
                elif tuple_val in temp_tree.right_split_vals:
                    temp_tree = temp_tree.r
                    continue
                else:
                    num = randint(0, 1)
                    if num == 0:
                        temp_tree = temp_tree.l
                    elif num == 1:
                        temp_tree = temp_tree.r
                    else:
                        raise ValueError('Neither child has appropriate values')
            
            predicted_class = temp_tree.class_label
            if class_label not in confusion_matrix:
                confusion_matrix[class_label] = {}
            if predicted_class not in confusion_matrix[class_label]:
                confusion_matrix[class_label][predicted_class] = 1
            else:
                confusion_matrix[class_label][predicted_class] = confusion_matrix[class_label][predicted_class] + 1
    
    actual_labels = confusion_matrix.keys()
    for actual_label in actual_labels:
        predicted_labels = confusion_matrix[actual_label].keys()
        diff = actual_labels ^ predicted_labels
        for missing_label in diff:
            confusion_matrix[actual_label][missing_label] = 0
        
    return confusion_matrix

def print_output(confusion_matrix):
    sorted_class_labels = sorted(confusion_matrix.keys())
    i = 0
    for label in sorted_class_labels:
        if i > 0:
            print('')
        sorted_predicted_labels = sorted(confusion_matrix[label].keys())
        for predicted_label in sorted_predicted_labels:
            print(confusion_matrix[label][predicted_label], end = ' ')
        i = i + 1
    print('')

#training_file = sys.argv[1]
#test_file = sys.argv[2]
training_file = '../ladam5_assign4/data/nursery.train'
test_file = '../ladam5_assign4/data/nursery.test'
processed_data = process_training_file(training_file)
processed_table = processed_data[0]
processed_unique_vals = processed_data[1]
processed_class_probs = processed_data[2]
matrix = None
start = timer()
if 'balance' in training_file or 'synthetic' in training_file or 'led' in training_file or 'nursery' in training_file:
    tree = generate_full_decision_tree(processed_table, processed_unique_vals, processed_class_probs, None)
    matrix = classify_test_file_full(tree, test_file)
#elif 'led' in training_file or 'nursery' in training_file:
#    tree = generate_binary_decision_tree(processed_table, processed_unique_vals, processed_class_probs)
#    matrix = classify_test_file_binary(tree, test_file)
end = timer()
print(end-start)
print_output(matrix)