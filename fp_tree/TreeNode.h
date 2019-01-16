#include <string>
#include <vector>

class TreeNode {
    private:
        std::string itemName;
        TreeNode *parent;
        std::vector<TreeNode *> children;
        int count;

    public:
        TreeNode();
        TreeNode(TreeNode *parent);
        void appendChild(TreeNode *child);
        void setParent(TreeNode *parent);
        std::string getItemName() const;
        int getCount() const;
        void setCount(int count);
        std::vector<TreeNode *> getChildren() const;
};