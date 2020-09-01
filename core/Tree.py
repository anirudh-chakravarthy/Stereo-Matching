import numpy as np

from core.Hypothesis import uniform_test, normal_test


'''
  Fields
    pixels: array of pixels corresponding to tree node (STRIP x W x C)
    mean, stdev: homogeneity measures for object segments
    left_child: instance of left child node
    right_child: instance of right child node
    width: width of subtree rooted at current node
    strip: length of strip of rows
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
    self.strip = self.pixels.shape[0]
    self.width = self.pixels.shape[1] # size of segment is the width of tree
    self.seq = seq
    self.level = len(self.seq) + 1
    self.match = False
    self.quality = -1
    self.disparity = 0

    self.compute_statistics()

  # split node into two child nodes
  def split(self):
    self.left_child = Node(self.pixels[:, :self.width // 2], self.seq + "0")
    self.right_child = Node(self.pixels[:, :self.width // 2:], self.seq + "1")

  # gather homogenity metrics for node
  def compute_statistics(self):
    self.mean = np.mean(self.pixels)
    self.stdev = np.std(self.pixels)


# whether two nodes are close
def closeness_test(left, right, rtol=5e-2, atol=0):
  return np.allclose(left, right, rtol, atol)


# test if a given node is homogeneous
def homogenity_test(root):
  # constant intensity
  if (root.pixels == root.pixels[0]).all():
    return True
  if root.width == 2:
    return closeness_test(root.pixels[0], root.pixels[1])

  # fit a low-order polynomial
  x = [i for i in range(root.width)]
  degree = 1
  p, residuals, rank, _, _ = np.polyfit(x, root.pixels, degree, full=True)
  
  # the residuals are only some noise
  stat, hypothesis = normal_test(residuals)
  return hypothesis


# grow tree until pixel-level resolution
def grow_tree(root):
  '''
  Arguments
    root (Node): root of tree
  '''
  if root.width == 1:
    return root

  root.split()
  grow_tree(root.left_child)
  grow_tree(root.right_child)
  return root
