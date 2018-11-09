import itertools
import functools
from functools import total_ordering
import sys

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

    def add_location(self, transaction, index):
        self.locations.append(Location(transaction, index))

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
    trans_range = range(0,len(transactions))
    for i in trans_range:
        t = transactions[i]
        vals = t.split(' ')
        index_range = range(0, len(vals))
        for j in index_range:
            val = vals[j]
            item = Item((val,), i, j)        
            try:
                index = item_objs.index(item)
                item_objs[index].add_location(i, j)
                #indexes = [k for k,item_obj in enumerate(item_objs) if item_obj == item]
            except ValueError:
                item_objs.append(item)

    # begins with frequent 1-itemsets
    freq_itemsets = [i for i in item_objs if len(i.locations) >= 2]
    g_freq_itemsets = []
    loop_range = range(2, 6)
    for k in loop_range:
        candidate_k_itemsets = apriori_gen(transactions, freq_itemsets, k)
        freq_itemsets = [i for i in candidate_k_itemsets if len(i.locations) >= 2]
        g_freq_itemsets.extend(freq_itemsets)
    return g_freq_itemsets

# itemset is frequent list of Item objects
def apriori_gen(transactions, itemset, k):
    num_transactions = range(0, len(transactions))
    k_item_objs = []
    for n in num_transactions:
        ################ optimization return dict for all transactions #####################
        locations_in_transaction_dict = create_location_dict(itemset, n)
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
                item_val_list = list(item.val)
                if k > 2:
                    item_val_list.extend(list(next_item.val)[k-2:])
                else:
                    item_val_list.extend(list(next_item.val))
                candidate_joined_val = tuple(item_val_list)                
                if has_infrequent_subset(candidate_joined_val, itemset, k):
                    continue
                joined_item = Item(candidate_joined_val, n, location.index)
                try:
                    item_index = k_item_objs.index(joined_item)
                    k_item_objs[item_index].add_location(n, location.index)
                except ValueError:
                    k_item_objs.append(joined_item)
    return k_item_objs

def has_infrequent_subset(candidate_itemset, itemsets, k):
    ########## could optimize to not create this list #############
    freq_tuples = [i.val for i in itemsets]
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

######## optimization put this inside for loop in apriori method ####################
def create_location_dict(items, transaction_num):
    location_dict = {}
    for item in items:
        for location in item.locations:
            if location.transaction == transaction_num:
                location_dict[location] = item
    return location_dict

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

#f = open('hw_bonus/input.txt', 'r')
#lines = f.read().splitlines()
#f.close()

contiguous_freq_itemsets = apriori(lines)
sorted_freq_itemsets = sorted(contiguous_freq_itemsets, key=functools.cmp_to_key(sort_items))
print_output(sorted_freq_itemsets[:20])