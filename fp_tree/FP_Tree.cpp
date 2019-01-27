#include <vector>
#include <sstream>
#include <string>
#include <fstream>
#include <map>
#include <iostream>
#include <algorithm>
#include "TreeNode.h"
using namespace std;

vector<string> transactions;
unsigned int minSupport;

struct HeaderTableValue {
    int itemCount;
    TreeNode *nodeLink;
};

map<string, HeaderTableValue> headerTable;

template <class K, class V>
void printMap(map<K, V> map) {
    typedef typename std::map<K, V>::iterator iterator;
    for(iterator p = map.begin(); p != map.end(); p++)
        cout << p->first << ": " << p->second << endl;
}

const map<string, unsigned int>* getFreqItems() {
    ifstream infile("input2.txt");
    map<string, unsigned int> itemsCount;
    map<string, unsigned int> *freqItems = new map<string, unsigned int>();
    string line;
    int lineCount = 0;
    while(getline(infile, line)) {
        if(lineCount == 0) {
            minSupport = line[0] - '0';
            lineCount++;
            continue;            
        }
        transactions.push_back(line);
        //vector<string> elems;
        //back_insert_iterator bi = back_inserter(elems);
        stringstream ss(line);
        string item;
        while(getline(ss, item, ' ')) {
            if(itemsCount.find(item) == itemsCount.end())
                itemsCount[item] = 1;
            else {
                itemsCount[item]++;
                if(itemsCount[item] >= minSupport) 
                    (*freqItems)[item] = itemsCount[item];
            }
            //*(bi++) = item;
        }        
    }
    infile.close();
    printMap(itemsCount);
    return freqItems;
}

void updateHeaderTable(TreeNode *node) {
    if(headerTable.count(node->getItemName()) == 0){
        // count should be 1
        int count = node->getCount();
        HeaderTableValue val = {count, node};
        headerTable[node->getItemName()] = val;
    }
    else {
        auto headerVal = headerTable[node->getItemName()];
        headerVal.itemCount = headerVal.itemCount++;
    }
}

void insertTree(vector<string>::iterator &it, vector<string>::iterator end, TreeNode *tree) {
    string currentItem = *it;
    vector<TreeNode *> children = tree->getChildren();
    // line below doesn't work
    auto childIt = find_if(children.begin(), children.end(), [&currentItem](const TreeNode& node) {return node.getItemName() == currentItem;});
    if(childIt != children.end()) {
        TreeNode *child = *childIt;
        int childCount = child->getCount();
        child->setCount(childCount++);
        updateHeaderTable(child);
    }
    else {
        TreeNode *newNode = new TreeNode();
        newNode->setCount(1);
        newNode->setItemName(currentItem);
        tree->appendChild(newNode);
        updateHeaderTable(newNode);
    }
    if(++it != end)
        insertTree(it, end, tree);
}

TreeNode* createFP_Tree(const vector<pair<string, unsigned int> >& freqItemTuples) {
    vector<string> freqItemsSorted;
    for(auto const& freqItem: freqItemTuples)
        freqItemsSorted.push_back(freqItem.first);
    TreeNode *root = new TreeNode();
    for(auto const& trans: transactions) {
        vector<string> freqItemsInTrans;
        for(auto const& freqItem: freqItemsSorted) 
            if (trans.find(freqItem) != string::npos)
                freqItemsInTrans.push_back(freqItem);
        vector<string>::iterator it = freqItemsInTrans.begin();
        insertTree(it, freqItemsInTrans.end(), root);
    }
    return root;
}

int main(int argc, char** argv) {
    const map<string, unsigned int> *freqItems = getFreqItems();
    // sort freq items map
    vector<pair<string, unsigned int> > *freqItemTuples = new vector<pair<string, unsigned int> >();
    freqItemTuples->assign(freqItems->begin(), freqItems->end());
    delete freqItems;
    sort(begin(*freqItemTuples), end(*freqItemTuples), [](auto const &p1, auto const &p2) {
        return p1.second > p2.second;
    });
    TreeNode *tree = createFP_Tree(*freqItemTuples);
    delete freqItemTuples;
    delete tree;
}