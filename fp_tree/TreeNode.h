#include <string>
#include <vector>
using namespace std;

class TreeNode {
    private:
        string itemName;
        TreeNode *parent;
        TreeNode *nodeLink;
        vector<TreeNode *> children;
        int count;

    public:
        TreeNode();
        ~TreeNode();
        TreeNode(TreeNode *parent);
        void appendChild(TreeNode *child);
        void setParent(TreeNode *parent);
        void setNodeLink(TreeNode *nodeLink);
        string getItemName() const;
        void setItemName(string name);
        int getCount() const;
        void setCount(int count);
        vector<TreeNode *> getChildren() const;
        void destroyRecursive(TreeNode *node);
};