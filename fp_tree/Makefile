#CXX = /usr/local/Cellar/gcc/8.2.0/bin/g++-8
CXX = clang++

fptree: treenode.o fptree.o
	$(CXX) -std=c++17 -g -o fptree.out TreeNode.o FP_Tree.o -pthread

fptree.o: FP_Tree.cpp TreeNode.h
	$(CXX) -std=c++17 -g -c -pthread FP_Tree.cpp

treenode.o: TreeNode.h TreeNode.cpp
	$(CXX) -std=c++17 -g -c -pthread TreeNode.cpp

clean:
	rm *.o *.out