import numpy as np


'''
  Fields
    pixels: array of pixels corresponding to tree node
    mean, stdev: homogeneity measures for object segments
    left_child: instance of left child node
    right_child: instance of right child node
    width: width of subtree rooted at current node
    seq: binary representation of object position
    level: level of node in the tree
    match: store matching left node in the right tree nodes
    quality: quality of match between corresponding nodes
    disparity: shift amount between corresponding object fragments
'''
class Node:
  def __init__(self, pixels, seq=""):
    self.pixels = pixels
    self.left_child = None
    self.right_child = None
    self.width = len(self.pixels) # size of segment is the width of tree
    self.seq = seq
    self.level = len(self.seq) + 1
    self.match = False
    self.quality = -1
    self.disparity = 0

    self.compute_statistics()

  # split node into two child nodes
  def split(self):
    self.left_child = Node(self.pixels[:len(self.pixels) // 2], self.seq + "0")
    self.right_child = Node(self.pixels[len(self.pixels) // 2:], self.seq + "1")

  # gather homogenity metrics for node
  def compute_statistics(self):
    self.mean = np.mean(self.pixels)
    self.stdev = np.std(self.pixels)


def similarity(left_node, right_node):
  l2 = np.linalg.norm(left_node.pixels - right_node.pixels)
  return l2
