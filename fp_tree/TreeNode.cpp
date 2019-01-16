#include "TreeNode.h"
#include <string>
#include <vector>

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

int TreeNode::getCount() const{
    return this->count;
}

void TreeNode::setCount(int theCount) {
    this->count = theCount;
}

std::vector<TreeNode *> TreeNode::getChildren() const {
    return this->children;
}

std::string TreeNode::getItemName() const {
    return this->itemName;
}