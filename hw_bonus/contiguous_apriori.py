import itertools
import functools
import sys
import timeit

def apriori(transactions):
    ####### maybe try comprehensions if still doesn't work #######
    all_items = {}
    freq_itemsets = {}
    transaction_freq_location_dict = {}
    trans_range = range(0,len(transactions))
    for i in trans_range:
        transaction_freq_location_dict[i] = {}
        t = transactions[i]
        vals = t.split(' ')
        index_range = range(0, len(vals))
        for j in index_range:
            val = vals[j]
            temp_item = (val,)
            if temp_item not in all_items:
                locations = []
                locations.append((i, j))
                all_items[temp_item] = locations
            else:
                all_items[temp_item].append((i, j)) 
            update_set_and_location_dict(temp_item, all_items, freq_itemsets, transaction_freq_location_dict)

    # begins with frequent 1-itemsets
    g_freq_itemsets = {}
    loop_range = range(2, 6)
    for k in loop_range:
        k_freq_items, k_transaction_freq_location_dict = apriori_gen(transactions, freq_itemsets, transaction_freq_location_dict, k)
        transaction_freq_location_dict = k_transaction_freq_location_dict
        freq_itemsets = k_freq_items
        g_freq_itemsets.update(freq_itemsets)
    return g_freq_itemsets

# itemset is frequent list of Item objects
def apriori_gen(transactions, freq_items, transaction_freq_location_dict, k):
    num_transactions = range(0, len(transactions))
    k_all_items = {}
    k_freq_items = {}
    k_transaction_freq_location_dict = {}
    for n in num_transactions:
        k_transaction_freq_location_dict[n] = {}
        locations_in_transaction_dict = transaction_freq_location_dict[n]
        sorted_indices = sorted(locations_in_transaction_dict.keys())
        i = 0
        for index in sorted_indices:
            try:
                next_index = sorted_indices[i + 1]
                i = i + 1
            except IndexError:
                break
            offset = k - 1
            if index + offset >= next_index:
                item = locations_in_transaction_dict[index]
                next_item = locations_in_transaction_dict[next_index]
                item_val_list = list(item)
                if k > 2:
                    item_val_list.extend(list(next_item)[k-2:])
                else:
                    item_val_list.extend(list(next_item))
                candidate_joined_val = tuple(item_val_list)                
                if offset == 1 and has_infrequent_subset(candidate_joined_val, freq_items, k):
                    continue
                if candidate_joined_val not in k_all_items:
                    locations = []
                    locations.append((n, index))
                    k_all_items[candidate_joined_val] = locations
                else:
                    k_all_items[candidate_joined_val].append((n, index))
                update_set_and_location_dict(candidate_joined_val, k_all_items, k_freq_items, k_transaction_freq_location_dict)
    return k_freq_items, k_transaction_freq_location_dict

def update_set_and_location_dict(temp_item, all_items, freq_items, transaction_freq_location_dict):
    item_locations = all_items[temp_item]
    if len(item_locations) == 2:
        freq_items[temp_item] = 2 
        ########## optimization try not to do this loop #################
        for item_location in item_locations:
            transaction_freq_location_dict[item_location[0]][item_location[1]] = temp_item
    elif len(item_locations) > 2:
        item_location = item_locations[-1]
        freq_items[temp_item] = freq_items[temp_item] + 1
        transaction_freq_location_dict[item_location[0]][item_location[1]] = temp_item
    else:
        return
    #indexes = [k for k,item_obj in enumerate(item_objs) if item_obj == item]

def has_infrequent_subset(candidate_itemset, freq_tuples, k):
    k_minus = k - 1
    ## Don't get all subsets, has to be adjacent
    if k_minus == 1:
        for subset in itertools.combinations(candidate_itemset, k_minus):
            if subset not in freq_tuples:
                return True
    else:
        for i, j in itertools.combinations(range(len(candidate_itemset) + 1), 2):
             if j - i == k_minus and candidate_itemset[i:j] not in freq_tuples:
                return True
    return False

def sort_items(a, b):    
    if a[1] < b[1]:
        return 1
    elif a[1] == b[1]:
        a_str = ''.join(a[0])
        b_str = ''.join(b[0])
        if a_str > b_str:
            return 1
        elif a_str < b_str:
            return -1
        else:
            return 0
    else:
        return -1

def print_output(freq_patterns):
    for pattern in freq_patterns:
        disp = ' '.join(pattern[0])
        print('[' + str(pattern[1]) + ', ' + "'" + disp + "'" + ']')

lines = []
for line in sys.stdin:
    lines.append(line.strip())

#f = open('../hw_bonus/input.txt', 'r')
#lines = f.read().splitlines()
#f.close()

#start = timeit.default_timer()
contiguous_freq_itemsets = apriori(lines)
#stop = timeit.default_timer()
#print('Time: ', stop - start)
sorted_freq_itemsets = sorted(contiguous_freq_itemsets.items(), key=functools.cmp_to_key(sort_items))
print_output(sorted_freq_itemsets[:20])