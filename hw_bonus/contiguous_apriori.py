import itertools
import functools
from functools import total_ordering
import sys
import timeit

@total_ordering
class Item:
    def __init__(self, val, transaction, index):
        self.val = val
        self.locations = []
        self.locations.append(Location(transaction, index))

    def _is_valid_operand(self, other):
        return (hasattr(other, "val") and
                hasattr(other, "locations"))
    
    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.val == other.val

    def __lt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        else:
            self_locations_sorted = sorted(self.locations)
            other_locations_sorted = sorted(other.locations)
            return self_locations_sorted[0] < other_locations_sorted[0]

    def __hash__(self):
        return hash(self.val)

    def __str__(self):
        return self.val.__str__()

    def add_location(self, location):
        self.locations.append(location)

    def get_locations(self):
        return self.locations

@total_ordering
class Location:
    def __init__(self, transaction, index):
        self.transaction = transaction
        self.index = index

    def _is_valid_operand(self, other):
        return (hasattr(other, "transaction") and
                hasattr(other, "index"))

    def __key(self):
        return (self.transaction, self.index)
    
    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.__key() == other.__key()

    def __lt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        if self.transaction != other.transaction:
            return self.transaction < other.transaction
        else:
            return self.index < other.index

    def __hash__(self):
        return hash(self.__key())

    def __str__(self):
        return str(self.transaction) + str(' ' + self.index)


def apriori(transactions):
    item_objs = []
    freq_itemsets = set()
    freq_vals = set()
    transaction_freq_location_dict = {}
    trans_range = range(0,len(transactions))
    for i in trans_range:
        transaction_freq_location_dict[i] = {}
        t = transactions[i]
        vals = t.split(' ')
        index_range = range(0, len(vals))
        for j in index_range:
            val = vals[j]
            temp_item = Item((val,), i, j)
            update_set_and_location_dict(temp_item, item_objs, freq_itemsets, freq_vals, transaction_freq_location_dict)

    # begins with frequent 1-itemsets
    g_freq_itemsets = []
    loop_range = range(2, 6)
    for k in loop_range:
        k_freq_items, k_freq_vals, k_transaction_freq_location_dict = apriori_gen(transactions, freq_vals, transaction_freq_location_dict, k)
        transaction_freq_location_dict = k_transaction_freq_location_dict
        freq_vals = k_freq_vals
        freq_itemsets = k_freq_items
        g_freq_itemsets.extend(freq_itemsets)
    return g_freq_itemsets

# itemset is frequent list of Item objects
def apriori_gen(transactions, freq_vals, transaction_freq_location_dict, k):
    num_transactions = range(0, len(transactions))
    k_item_objs = []
    k_freq_vals = set()
    k_freq_items = set()
    k_transaction_freq_location_dict = {}
    for n in num_transactions:
        k_transaction_freq_location_dict[n] = {}
        locations_in_transaction_dict = transaction_freq_location_dict[n]
        sorted_locations = sorted(locations_in_transaction_dict.keys())
        i = 0
        for location in sorted_locations:
            try:
                next_location = sorted_locations[i + 1]
                i = i + 1
            except IndexError:
                break
            if location_adjacent(location, next_location, k-1):
                item = locations_in_transaction_dict[location]
                next_item = locations_in_transaction_dict[next_location]
                item_val_list = list(item)
                if k > 2:
                    item_val_list.extend(list(next_item)[k-2:])
                else:
                    item_val_list.extend(list(next_item))
                candidate_joined_val = tuple(item_val_list)                
                if has_infrequent_subset(candidate_joined_val, freq_vals, k):
                    continue
                temp_joined_item = Item(candidate_joined_val, n, location.index)
                update_set_and_location_dict(temp_joined_item, k_item_objs, k_freq_items, k_freq_vals, k_transaction_freq_location_dict)
    return k_freq_items, k_freq_vals, k_transaction_freq_location_dict

def update_set_and_location_dict(temp_item, item_list, freq_items, freq_vals, transaction_freq_location_dict):
    location = temp_item.locations[0]                    
    try:
        index = item_list.index(temp_item)
        list_item = item_list[index]
        list_item.add_location(location)
        if list_item not in freq_items:
            freq_items.add(list_item)
            freq_vals.add(list_item.val)
        else:
            freq_items.remove(list_item)
            freq_items.add(list_item)                
        item_locations = list_item.get_locations()
        if len(item_locations) == 2:
            for item_location in item_locations:
                transaction_freq_location_dict[item_location.transaction][item_location] = temp_item.val
        else:
            transaction_freq_location_dict[location.transaction][location] = temp_item.val
        #indexes = [k for k,item_obj in enumerate(item_objs) if item_obj == item]
    except ValueError:
        item_list.append(temp_item)

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

def location_adjacent(location, next_location, offset):
    if location.transaction == next_location.transaction:
        if location.index + offset >= next_location.index:
            return True
        else:
            return False
    else:
        return False

def sort_items(i1, i2):
    if len(i1.locations) < len(i2.locations):
        return 1
    elif len(i1.locations) == len(i2.locations):
        i1_str = ''.join(i1.val)
        i2_str = ''.join(i2.val)
        if i1_str > i2_str:
            return 1
        if i1_str < i2_str:
            return -1
        else:
            return 0
    else:
        return -1

def print_output(freq_patterns):
    for pattern in freq_patterns:
        disp = ' '.join(pattern.val)
        print('[' + str(len(pattern.locations)) + ', ' + "'" + disp + "'" + ']')

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
sorted_freq_itemsets = sorted(contiguous_freq_itemsets, key=functools.cmp_to_key(sort_items))
print_output(sorted_freq_itemsets[:20])