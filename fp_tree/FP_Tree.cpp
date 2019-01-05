#include <vector>
#include <sstream>
#include <string>
#include <fstream>
#include <map>
#include <iostream>
#include "TreeNode.h"
using namespace std;

vector<string> transactions;
map<string, unsigned int> freqItems;
unsigned int minSupport;
vector<pair<string, unsigned int> > freqItemTuples;

template <class K, class V>
void printMap(map<K, V> map) {
    typedef typename std::map<K, V>::iterator iterator;
    for(iterator p = map.begin(); p != map.end(); p++)
        cout << p->first << ": " << p->second << endl;
}

void countWords() {
    ifstream infile("input2.txt");
    map<string, unsigned int> itemsCount;    
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
                    freqItems[item] = itemsCount[item];
            }
            //*(bi++) = item;
        }        
    }
    infile.close();
    printMap(itemsCount);
}

void createFP_Tree() {
    vector<string> freqItemsSorted;
    for(auto const& freqItem: freqItemTuples)
        freqItemsSorted.push_back(freqItem.first);
    TreeNode root = new TreeNode();
    for(auto const& trans: transactions) {

    }
}

int main(int argc, char** argv) {
    countWords();
    // sort freq items map
    freqItemTuples.assign(freqItems.begin(), freqItems.end());
    sort(begin(freqItemTuples), end(freqItemTuples), [](auto const &p1, auto const &p2) {
        return p1.second > p2.second;
    });
    createFP_Tree();
}