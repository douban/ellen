#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pygit2 import GIT_OBJ_BLOB
from pygit2 import GIT_FILEMODE_BLOB
from pygit2 import GIT_FILEMODE_TREE


# used in ellen.commit
class TreeNode(object):

    def __init__(self, parent, path, type, action='insert'):
        self.path = path
        self.name = path
        self.children = []
        self.type = type
        self.parent = parent
        self.index = {}
        self.id = None
        self.action = action
        self.builder = None
        self.content = None

    def operating_file(self, operation, pathname, content):
        if pathname.startswith('/'):
            pathname = pathname[1:]
        paths = pathname.split('/')
        length = len(paths)
        if length == 1:
            node = getattr(self, operation)(pathname)
            node.content = content
            return node
        root = self
        for i, path in enumerate(paths):
            node = root.index.get(path, None)
            if not node:
                if i == length - 1:
                    node = getattr(root, operation)(path)
                    node.content = content
                else:
                    node = root.add_tree(path)
            root = node
            if i >= 1:
                node.path = '/'.join(paths[:i])
                node.path = '/'.join([node.path, path])
                self.index[node.path] = node
        return node

    def add_file(self, pathname, content=None):
        return self.operating_file('add_blob', pathname, content)

    def del_file(self, pathname, content=None):
        return self.operating_file('del_blob', pathname, content)

    def action_tree_or_blob(self, path, type, action='insert'):
        if path.startswith('/'):
            path = path[1:]
        node = TreeNode(self, path, type, action=action)
        self.index[path] = node
        self.children.append(node)
        return node

    def add_tree(self, path):
        return self.action_tree_or_blob(path, 'tree')

    def add_blob(self, path):
        return self.action_tree_or_blob(path, 'blob')

    def del_blob(self, path):
        return self.action_tree_or_blob(path, 'blob', action='remove')

    def walk(self):
        queue = [i for i in self.children] + [self]
        last_node = None
        while queue:
            if queue[0].type == 'tree' and last_node == queue[0].children[-1]:
                yield queue[0]
                last_node = queue[0]
                queue = queue[1:]
            elif queue[0].type == 'blob':
                yield queue[0]
                last_node = queue[0]
                queue = queue[1:]
            else:
                expansion = [i for i in queue[0].children]
                queue = expansion + queue

    def __getitem__(self, key):
        if key != '/' and key.endswith('/'):
            key = key[:-1]
        return self.index[key]

    def write(self, repository, commit):
        if self.type == 'tree':
            write_tree(repository, commit, self)
        else:
            write_blob(repository, self)


def get_treebuilder(repository, commit, node):
    new = None
    if commit:
        try:
            if node.path:
                new = commit.tree[node.path]
            else:
                new = commit.tree
        except KeyError:
            pass
    if new:
        tree = repository[new.id]
        tb = repository.TreeBuilder(tree)
    else:
        tb = repository.TreeBuilder()
    return tb


def write_tree(repository, commit, node):
    if node.type != "tree":
        return None
    if node.id:
        return None
    if not node.builder:
        node.builder = get_treebuilder(repository, commit, node)
    for entry in node.children:
        path = entry.name
        oid = entry.id
        if entry.type == 'tree':
            mode = GIT_FILEMODE_TREE
        else:
            mode = GIT_FILEMODE_BLOB
        if oid:
            node.builder.insert(path, oid, mode)
        else:
            node.builder.remove(path)
    if node.path and len(node.builder) <= 0:
        node.action = 'remove'
        return None
    node.id = node.builder.write()


def write_blob(repository, node):
    if node.type != 'blob':
        return None
    if node.id:
        return None
    if node.action == 'remove':
        return None
    node.id = repository.write(GIT_OBJ_BLOB, node.content)


def init_root():
    return TreeNode(None, '', 'tree')


# TODO: move to tests...?
def test_node():
    root = TreeNode(None, '', 'tree')
    node = root.add_file('/tt/tt/tt1/t.txt')
    node = root.add_file('tt/tt/tt1/t1.txt')
    node = root.add_file('/tt/tt/tt2/t.txt')
    node = root.add_file('tt/tt/tt2/t1.txt')
    node = root.del_file('tt/tt/tt3/t.txt')
    node = root.del_file('tt/tt/tt4/t.txt')
    print "root", root.index
    print "root", root.children
    print "root", root.path
    print "{}", node.index
    print "t1.txt", node.path
    print "[]", node.children
    print "{t.txt}", node.parent.index
    print "t.txt", node.parent.children
    print "tt1", node.parent.path
    print "tt", node.parent.parent.path
    print "tt", node.parent.parent.parent.path
    print "/", node.parent.parent.parent.parent.path
    for n in root.walk():
        print n.type, n.path, n.action


if __name__ == '__main__':
    test_node()
