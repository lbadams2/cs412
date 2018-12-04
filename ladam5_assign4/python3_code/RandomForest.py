from itertools import chain, combinations
import sys
from random import randint
from random import choice as random_choice
from timeit import default_timer as timer
from collections import Counter

class Node:
    def __init__(self, data):
        self.l = None
        self.r = None
        self.data = data
        self.class_label = None
        self.split_attr = None
        self.left_split_vals = None
        self.right_split_vals = None
        self.depth = 0

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

def gini_index_attr(attr_val_table, attr_vals_unique):
    # maybe optimize to not call len()
    total_count = len(attr_val_table.keys())
    min_attr_gini_index = None
    best_split = None
    no_unique_vals = False
    random_attr_vals_unique = {}
    current_attr_num = len(attr_vals_unique)
    num_attributes = 0

    if 'synthetic' in training_file:
        num_attributes = 40
    elif 'led' in training_file:
        num_attributes = 3
    elif 'nursery' in training_file:
        num_attributes = 4
    elif 'balance' in training_file:
        num_attributes = 2
    
    if num_attributes > current_attr_num:
        return best_split, True
    else:
        key_list = list(attr_vals_unique.keys())
        random_attrs = set()
        while len(random_attrs) < num_attributes:
            random_attr = random_choice(key_list)
            if random_attr not in random_attr_vals_unique:
                random_attr_vals_unique[random_attr] = attr_vals_unique[random_attr]
                random_attrs.add(random_attr)
        attr_vals_unique = random_attr_vals_unique

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

def generate_binary_decision_tree(table, attr_list, class_probs, depth):
    node = Node(table)
    node.depth = depth
    print('node depth: ' + str(depth))
    next_depth = depth + 1
    if len(class_probs.keys()) == 1:
        node.class_label = list(class_probs.keys())[0]
        return node

    # how to break tie
    majority_class = max(class_probs, key=class_probs.get)
    if not attr_list:        
        node.class_label = majority_class
        return node    

    # 6 is 166 seconds accuracy .48
    # 4 is 122 seconds accuracy .46
    #if depth > 4 and 'synthetic' in training_file:
    #    node.class_label = majority_class
    #    return node

    gini_results = gini_index_attr(table, attr_list)
    best_split = gini_results[0]
    # rows in table are identical
    if not best_split and gini_results[1]:
        node.class_label = majority_class
        return node
    if not best_split:
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
        leaf_node.depth = next_depth
        node.l = leaf_node
    else:
        node.l = generate_binary_decision_tree(yes_split.data, yes_split.attr_vals_unique, yes_split.class_probs, next_depth)

    if not no_split.data:
        leaf_node = Node(None)
        leaf_node.class_label = majority_class
        leaf_node.depth = next_depth
        node.r = leaf_node
    else:
        node.r = generate_binary_decision_tree(no_split.data, no_split.attr_vals_unique, no_split.class_probs,next_depth)

    return node

def process_training_file(training_file):
    attr_vals_table = {}
    with open(training_file, 'r') as f:
        i = 0
        for line in f:
            i = i + 1
            line = line.strip()       
            elems = line.split(' ')
            class_label = elems[0]

            attr_vals_table[i] = {}
            attr_vals_table[i]['class'] = class_label

            for attr_val in elems[1:]:
                attr_vals = attr_val.split(':')
                attr = attr_vals[0]
                val = attr_vals[1]
                attr_vals_table[i][attr] = val

    return attr_vals_table

def classify_test_file_binary(decision_trees, test_file):
    confusion_matrix = {}    
    correct_predictions = 0
    lines = []
    with open(test_file, 'r') as f:
        lines = f.read().splitlines()
    
    actual_predicted_class_dict = {}
    for decision_tree in decision_trees:
        num_lines = 0
        for line in lines:
            num_lines = num_lines + 1            
            temp_tree = decision_tree
            line = line.strip()       
            elems = line.split(' ')
            class_label = elems[0]
            if num_lines not in actual_predicted_class_dict:
                actual_predicted_class_dict[num_lines] = {}
                actual_predicted_class_dict[num_lines][class_label] = []
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
            actual_predicted_class_dict[num_lines][class_label].append(predicted_class)
    
    for test_tuple, actual_predicted_dict in actual_predicted_class_dict.items():
        if len(actual_predicted_dict.keys()) != 1:
            raise ValueError('Something went wrong in classifier')
        class_label = list(actual_predicted_dict.keys())[0]
        predicted_classes = actual_predicted_dict[class_label]
        predicted_class_counter = {}
        for predicted_class in predicted_classes:
            if predicted_class in predicted_class_counter:
                predicted_class_counter[predicted_class] += 1
            else:
                predicted_class_counter[predicted_class] = 1
        popular_classes = sorted(predicted_class_counter, key = predicted_class_counter.get, reverse = True)
        predicted_class = popular_classes[0]
        if predicted_class == class_label:
            correct_predictions = correct_predictions + 1
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
    
    print('Accuracy: ' + str(correct_predictions/num_lines))
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

def get_sample_table_data(data_set_dict):
    data_set_size = len(data_set_dict)
    sample_table = {}
    attr_vals_unique = {}
    total_class_probs = {}
    total_class_counter = {}
    key_list = list(data_set_dict.keys())
    for sample_num in range(0, data_set_size):
        random_tuple_key = random_choice(key_list)
        random_tuple_val = data_set_dict[random_tuple_key]
        if random_tuple_key in sample_table:
            dup_count = 2
            modified_key = random_tuple_key
            while modified_key in sample_table:
                modified_key = str(random_tuple_key) + '_' + str(dup_count)
                dup_count = dup_count + 1
            sample_table[modified_key] = random_tuple_val
        else:
            sample_table[random_tuple_key] = random_tuple_val

        for attr, val in random_tuple_val.items():
            if attr == 'class':
                continue
            if attr not in attr_vals_unique:
                val_set = set()
                val_set.add(val)
                attr_vals_unique[attr] = val_set
            else:
                if val not in attr_vals_unique[attr]:
                    attr_vals_unique[attr].add(val)

        class_label = random_tuple_val['class']
        if class_label not in total_class_counter:
                total_class_counter[class_label] = 1
        else:
            total_class_counter[class_label] = total_class_counter[class_label] + 1

    total_class_probs = {k: v/data_set_size for k, v in total_class_counter.items()}
    return sample_table, attr_vals_unique, total_class_probs

start = timer()
#training_file = sys.argv[1]
#test_file = sys.argv[2]
training_file = '../ladam5_assign4/data/synthetic.social.train'
test_file = '../ladam5_assign4/data/synthetic.social.test'
processed_table = process_training_file(training_file)
matrix = None
num_trees = 0
if 'balance' in training_file:
    num_trees = 30
elif 'led' in training_file:
    num_trees = 30
elif 'nursery' in training_file:
    num_trees = 30
elif 'synthetic' in training_file:
    num_trees = 10
trees = []
'''
if 'balance' in training_file or 'synthetic' in training_file or 'led' in training_file or 'nursery' in training_file:
    tree = generate_full_decision_tree(processed_table, processed_unique_vals, processed_class_probs, None, 0)
    matrix = classify_test_file_full(tree, test_file)
'''
if 'balance' in training_file or 'synthetic' in training_file or 'led' in training_file or 'nursery' in training_file:
    for num_tree in range(0, num_trees):
        processed_data = get_sample_table_data(processed_table)
        sample_table = processed_data[0]
        sample_attr_vals_unique = processed_data[1]
        sample_class_probs = processed_data[2]
        tree = generate_binary_decision_tree(sample_table, sample_attr_vals_unique, sample_class_probs, 0)
        trees.append(tree)
    matrix = classify_test_file_binary(trees, test_file)
end = timer()
print('Runtime: ' + str(end-start))
print_output(matrix)