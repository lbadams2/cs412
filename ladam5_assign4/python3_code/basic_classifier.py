def gini_index(tuples, attribute_list):
    

with open('balance.scale.train', 'r') as f:
    lines = []
    class_counter = {}
    i = 0
    for line in f:
        i = i + 1
        elems = line.split(' ')
        class_label = elems[0]
        if class_label in class_counter:
            class_counter[class_label] = class_counter[class_label] + 1
        else:
            class_counter[class_label] = 1
    class_prob = {}
    for k in class_counter.keys():
        class_prob[k] = class_counter[k]/i
    
