import itertools
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
            if item not in item_objs:
                item_objs.append(item)
            else:
                ######### change to return first index #####################
                indexes = [k for k,item_obj in enumerate(item_objs) if item_obj == item]
                item_objs[indexes[0]].add_location(i, j)

    # begins with frequent 1-itemsets
    freq_itemsets = [i for i in item_objs if len(i.locations) >= 2]
    g_freq_itemsets = freq_itemsets
    loop_range = range(2, 5)
    for k in loop_range:
        #itemsets = list(freq_itemsets.keys())
        #sorted_itemsets = sorted(freq_itemsets)
        candidate_k_itemsets = apriori_gen(transactions, freq_itemsets, k)
        freq_itemsets = {k: v for k,v in candidate_k_itemsets.items() if v >= 2}
        g_freq_itemsets.update(freq_itemsets)
    return g_freq_itemsets

# itemset is frequent list of Item objects
def apriori_gen(transactions, itemset, k):
    num_transactions = range(0, len(transactions))
    k_itemset_counter = {}
    for n in num_transactions:
        ################ optimization return dict for all transactions #####################
        locations_in_transaction_dict = create_location_dict(itemset, n)
        sorted_locations = sorted(locations_in_transaction_dict.keys())
        #freq_items_in_transaction = [ for i in itemset if i.transaction == n]
        #freq_items_in_transaction = {k:v for k,v in itemset if v.transaction == n}
        # stop at second to last for join checking
        location_range = range(0, len(sorted_locations) - 1)
        for i in location_range:
            location = sorted_locations[i]
            next_location = sorted_locations[i + 1]
            if location_adjacent(location, next_location, k-1):
                item = locations_in_transaction_dict[location]
                next_item = locations_in_transaction_dict[next_location]
                item_val_list = list(item.val)
                item_val_list.extend(list(next_item.val))
                candidate_joined_val = tuple(item_val_list)                
                if has_infrequent_subset(candidate_joined_val, itemset, k):
                    continue
                joined_item = Item(candidate_joined_val, i, n)
                if joined_item not in k_itemset_counter:
                    k_itemset_counter[joined_item] = 1
                else:
                    k_itemset_counter[joined_item] = k_itemset_counter[joined_item] + 1
    return k_itemset_counter

def has_infrequent_subset(candidate_itemset, itemsets, k):
    ########## could optimize to not create this list #############
    freq_tuples = [i.val for i in itemsets]
    k_minus = k - 1
    for subset in itertools.combinations(candidate_itemset, k_minus):
        if subset not in freq_tuples:
            return True
    return False

def create_location_dict(items, transaction_num):
    location_dict = {}
    for item in items:
        for location in item.locations:
            if location.transaction == transaction_num:
                location_dict[location] = item
    return location_dict

def location_adjacent(location, next_location, offset):
    if location.transaction == next_location.transaction:
        if location.index + offset == next_location.index:
            return True
        else:
            return False
    else:
        return False

def print_output(freq_patterns):
    for pattern in freq_patterns:
        disp = ' '.join(pattern.val)
        print(freq_patterns[pattern], '[' + disp + ']')

f = open('/Users/liamadams/Documents/school/CS412/hw_bonus/input.txt', 'r')
lines = f.read().splitlines()
f.close()
contiguous_freq_itemsets = apriori(lines)
print_output(contiguous_freq_itemsets)