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