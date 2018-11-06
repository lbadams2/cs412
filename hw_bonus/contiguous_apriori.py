import itertools
from functools import total_ordering
import sys

@total_ordering
class Item:
    def __init__(self, val, transaction, index):
        self.val = val
        self.transaction = transaction
        self.index = index

    def _is_valid_operand(self, other):
        return (hasattr(other, "val") and
                hasattr(other, "transaction") and
                hasattr(other, "index"))
    
    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return self.val == other.val

    def __lt__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        if self.transaction != other.transaction:
            return self.transaction < other.transaction
        else:
            return self.index < other.index

    def __hash__(self):
        return hash(self.val)

    def __str__(self):
        return self.val.__str__()
        

def apriori(transactions):
    counter = {}
    trans_range = range(0,len(transactions) - 1)
    for i in trans_range:
        t = transactions[i]
        items = t.split(' ')
        items_range = range(0, len(items) - 1)
        for j in items_range:
            item = items[j]
            item = Item((item,), i, j)
            if item not in counter:
                counter[item] = 1
            else:
                counter[item] = counter[item] + 1

    # begins with frequent 1-itemsets
    freq_itemsets = {k: v for k,v in counter.items() if v >= 2}
    g_freq_itemsets = freq_itemsets
    loop_range = range(2, 5)
    for k in loop_range:
        itemsets = list(freq_itemsets.keys())
        sorted_itemsets = sorted(itemsets)
        candidate_k_itemsets = apriori_gen(transactions, sorted_itemsets, k)
        freq_itemsets = {k: v for k,v in candidate_k_itemsets.items() if v >= 2}
        g_freq_itemsets.update(freq_itemsets)
    return g_freq_itemsets

def apriori_gen(transactions, itemset, k):
    num_transactions = range(0, len(transactions))
    k_itemset_counter = {}
    for n in num_transactions:
        freq_items_in_transaction = [i for i in itemset if i.transaction == n]
        sorted_freq_items = sorted(freq_items_in_transaction)
        item_range = range(0, len(sorted_freq_items))
        for i in item_range:
            item = sorted_freq_items[i]
            join_items = sorted_freq_items[i+1:i+k]
            offset = 1
            joinable = False
            for join_item in join_items:
                if item.index == join_item.index + offset:
                    joinable = True
                else:
                    joinable = False
                    break
                offset = offset + 1
            if joinable:
                item_list = list(item)
                item_list.extend(join_items)
                candidate_joined_item = tuple(item_list)
                if has_infrequent_subset(candidate_joined_item, itemset):
                    continue
                if candidate_joined_item not in k_itemset_counter:
                    k_itemset_counter[candidate_joined_item] = 1
                else:
                    k_itemset_counter[candidate_joined_item] = k_itemset_counter[candidate_joined_item] + 1
    return k_itemset_counter

def has_infrequent_subset(candidate_itemset, itemsets):
    k_minus = len(itemsets[0])
    for subset in itertools.combinations(candidate_itemset, k_minus):
        if subset not in itemsets:
            return True
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