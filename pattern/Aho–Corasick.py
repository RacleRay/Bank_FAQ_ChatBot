from collections import deque


class Node:
    def __init__(self, value='', finished=False):
        self.children = {}
        self.value = value
        self.fail = None
        self.key = ''
        self.finished = finished

    def child(self, value):
        '''get the child based on the value
        '''
        return self.children.get(value, None)



# 双数组trie树，比较适合中文的trie构建. 这里是普通trie
def build_trie(root, key_words):

    def add_word(root, word):
        for c in word:
            child = root.child(c)
            if not child:
                child = Node(value=c)
                root.children[c] = (child)
            root = child
        root.key = word
        root.finished = True

    for word in key_words:
        add_word(root,word)
    return root


# 采用BFS的方法，用父节点的fail来更新子节点的fail
def build_ac(root):
    q = deque()
    q.append(root)
    while q:
        node = q.popleft()
        for value, child in node.children.items():
            if node == root:
                child.fail = root
            else:
                fail_node = node.fail
                c = fail_node.child(value)  # 找到最近的后缀
                if c:
                    child.fail = c
                else:
                    child.fail = root
            q.append(child)
    return root


# 最后是查找的过程，从左到右查询query，
#   如果匹配的话就看看node节点之前有没有可以输出的节点
#   如果不匹配的话就找fail节点

def search(s, root):
    node = root
    def search(s, root):
    node = root
    for i,c in enumerate(s):
        while node and not node.child(c):
            node = node.fail
        if not node:
            node = root
            continue
        node = node.child(c)
        out = node
        while out:
            if out.finished:
                print(i, out.key)
            out = out.fail