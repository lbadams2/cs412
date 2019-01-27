#include "TreeNode.h"

TreeNode::TreeNode() {
    parent = NULL;
};

TreeNode::TreeNode(TreeNode *theParent) {
    parent = theParent;
};

void TreeNode::appendChild(TreeNode *child) {
    child->setParent(this);
    children.push_back(child);
}

void TreeNode::setParent(TreeNode *theParent) {
    parent = theParent;
}

void TreeNode::setNodeLink(TreeNode *theLink) {
    this->nodeLink = theLink;
}

int TreeNode::getCount() const{
    return this->count;
}

void TreeNode::setCount(int theCount) {
    this->count = theCount;
}

vector<TreeNode *> TreeNode::getChildren() const {
    return this->children;
}

string TreeNode::getItemName() const {
    return this->itemName;
}

void TreeNode::setItemName(string name) {
    this->itemName = name;
}

void TreeNode::destroyRecursive(TreeNode *node) {
    if(node) {
        for(auto child: children) {
            destroyRecursive(child);
            delete node;
        }
    }
}

TreeNode::~TreeNode() {
    destroyRecursive(this);
}