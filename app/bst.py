from binarytree import Node, bst
from app.version import getversion

class BST:
    """generate a BST and insert nodes into it.
    Traversal outputs are generated.
    """
    def __init__(self, balanced=False, node=None):
        self.balancedbst = False
        if balanced: 
            self.root = bst(height=4, is_perfect=True)
            self.balancedbst = True
        else:
            self.root = node
        
        self.set_banner_info()

    def set_banner_info(self): 
        versioninfo = getversion()
        self.banner = str("BST Visualizer - " + versioninfo + "\n") 
        
    def binary_insert(self, num, node=None):
        if node is None:
            if self.root is None:
                self.root = Node(num)
                return
            else:
                node = self.root
        if node.value >= num:
            if node.left is not None:
                self.binary_insert(num, node.left)
            else:
                node.left = Node(num)
        if node.value < num:
            if node.right is not None:
                self.binary_insert(num, node.right)
            else:
                node.right = Node(num)

    def inorder(self, ans_list, node=None):
        if node is None:
            node = self.root
        if node.left is not None:
            ans_list = self.inorder(ans_list, node.left)
        ans_list += [node.value]
        if node.right is not None:
            ans_list = self.inorder(ans_list, node.right)

        return ans_list

    def preorder(self, ans_list, node=None):
        if node is None:
            node = self.root
        ans_list += [node.value]
        if node.left is not None:
            ans_list = self.preorder(ans_list, node.left)
        if node.right is not None:
            ans_list = self.preorder(ans_list, node.right)

        return ans_list

    def postorder(self, ans_list, node=None):
        if node is None:
            node = self.root
        if node.left is not None:
            ans_list = self.postorder(ans_list, node.left)
        if node.right is not None:
            ans_list = self.postorder(ans_list, node.right)
        ans_list += [node.value]
        return ans_list

    def get_output(self):
        output = self.banner
        if self.balancedbst: 
            output += 'Balanced BST\n'
        output += str(self.root)
        output += '\n\nPREORDER\t' + str(self.preorder([]))
        output += '\nINORDER\t\t' + str(self.inorder([]))
        output += '\nPOSTORDER\t' + str(self.postorder([]))
        return output


# sample output which gets displayed on local console
bsttest = BST()
bsttest.binary_insert(10)
bsttest.binary_insert(7)
bsttest.binary_insert(11)
bsttest.binary_insert(6)
bsttest.binary_insert(8)
bsttest.binary_insert(20)
bsttest.binary_insert(1)
bsttest.binary_insert(9)
bsttest.binary_insert(14)
bsttest.binary_insert(22)
print(bsttest.root)

balancedbst = bst(height=3, is_perfect=True)
print(balancedbst)
#print(bbst.inorder)
#print(type(bbst).__name__)


def sortedArrayToBST(arr):
    '''take a sorted array and return a balanced binary tree out of it'''
    if not arr:
        return None

    # find middle index
    mid = len(arr) // 2
	
    # make the middle element the root
    root = Node(arr[mid])
	
    # left subtree of root has all
    # values <arr[mid]
    root.left = sortedArrayToBST(arr[:mid])
	
    # right subtree of root has all
    # values >arr[mid]
    root.right = sortedArrayToBST(arr[mid+1:])
    return root
