fptree: treenode.o fptree.o
	clang++ -std=c++17 -g -o fptree TreeNode.o FP_Tree.o -pthread

fptree.o: FP_Tree.cpp TreeNode.h
	clang++ -std=c++17 -g -c -pthread FP_Tree.cpp

treenode.o: TreeNode.h TreeNode.cpp
	clang++ -std=c++17 -g -c -pthread TreeNode.cpp