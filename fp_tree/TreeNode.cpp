#include "TreeNode.h"
#include <string>
#include <vector>

TreeNode::TreeNode() {};

void TreeNode::appendChild(TreeNode *child) {
    child->setParent(this);
    children.push_back(child);
}

void TreeNode::setParent(TreeNode *theParent) {
    parent = theParent;
}