class FP_Tree(object):
    "https://stackoverflow.com/questions/2358045/how-can-i-implement-a-tree-in-python-are-there-any-built-in-data-structures-in"
    def __init__(self, name='null', children=None):
        self.name = name
        self.children = []
        self.count = 0
        if children is not None:
            for child in children:
                self.add_child(child)
    def __repr__(self):
        return self.name
    def add_child(self, node):
        assert isinstance(node, FP_Tree)
        self.children.append(node)
    def add_transaction(self, transaction):
        #for item in transaction:
        # traverse tree to find common prefix or add entire branch and increment counts
        # create header table pointing to locations of each item in the tree
    def inorder(self):
        assert isinstance(node, FP_Tree)
        print(self.name)
        for child in node.children:
            child.inorder()



def create_fp_tree(data):
    # create counts of each item
    counter = {}
    for value in data.values():
        for item in value.split(','):
            if item in counter:
                counter[item] = counter[item] + 1
            else:
                counter[item] = 1
    # for each transaction, sort it, then add to tree
    fp_tree = FP_Tree()
    for transaction in data.values():
        items = transaction.split(',')
        transaction_dict = {item:counter[item] for item in items if item in counter}
        sorted_transaction_tuple = sorted(transaction_dict.items(), key=lambda kv: kv[1], reverse=True)
        fp_tree.add_transaction(sorted_transaction_tuple)
        print(sorted_transaction_tuple)

def mine_fp_tree(tree):
    # get frequent 1 itemsets
    counter = {}
    # iterate counter in reverse order
    # use header table to find occurrences of the item and the branches it is located in
    # get the item's prefix paths - the items preceding it in a branch - each of these paths form the conditional pattern base
    # use the conditional pattern base to build a conditional fp tree for the current item, merge the bases if they share a prefix
    # only include the frequent patterns in the conditional fp tree
    # the tree will generate frequent patterns for the suffix item, all combinations from the conditional fp tree

data = {}
with open('table.dat', 'r') as f:
    data = dict(line.strip().split(':') for line in f)

create_fp_tree(data)