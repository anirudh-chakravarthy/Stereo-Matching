import math
import numpy as np

from core.Hypothesis import uniform_test, normal_test


class Objective:
  """
  Evaluate objective function
  Args:
    left_roots: list of left row trees
    right_roots: list of right row trees
    left_img: left stereo img
    disparity: predicted disparity maps
    use_vertical_smoothness: test vertical smoothness of disparity
    use_homogeneity: check homogeneity of nodes
  """
  def __init__(self, 
               left_roots, 
               right_roots, 
               left_img,
               disparity,
               use_vertical_smoothness=False, 
               use_homogeneity=False
  ):
    self.left_roots = left_roots
    self.right_roots = right_roots
    self.left_img = left_img
    self.disparity = disparity
    self.use_vertical_smoothness = use_vertical_smoothness
    self.use_homogeneity = use_homogeneity


  # quantitative homogenity metric
  def homogeneity(self, node):
    # constant intensity
    if (node.pixels == node.pixels[:, 0]).all():
      return 0., True
    if node.width == 2:
      sse = math.sqrt((node.pixels[:, 0] - node.pixels[:, 1]) ** 2)
      is_homogeneous = np.allclose(left, right, rtol=5e-2, atol=0)
      return sse.sum(), is_homogeneous

    # fit a low-order polynomial
    x = [i for i in range(node.width)]
    degree = 1
    p, residuals, rank, _, _ = np.polyfit(x, node.pixels, degree, full=True)
    return residuals.sum(), normal_test(residuals)


  # grow column tree for disparity smoothness
  def _grow_column_tree(self, node):
    if node.width == 1:
      return 0.

    if node.width == 2:
      is_homogeneous = np.allclose(node.pixels[0], node.pixels[1], rtol=5e-2, atol=0)
      if is_homogeneous:
        return 

    elif normal_test(root):
      return

    root.split()
    self._grow_column_tree(self, root.left_child)
    self._grow_column_tree(self, root.right_child)
    return

  def vertical_smoothness(self):
    num_cols = self.left_img.shape[1]
    for col_idx in range(num_cols):
      root = Node(self.left_img[:, col_idx])
      root = self._grow_column_tree(root)
    return col_trees_left, col_trees_right

  # find all regions
  def _find_regions(self, node):

    if node.width == 1:
      return 0., 0.

    # resigned to split into 2
    if node.width == 2:
      is_homogeneous = np.allclose(node.pixels[0], node.pixels[1], rtol=5e-2, atol=0)
      if is_homogeneous:
        idx = int(node.seq, 2)
        base = 2 ** len(node.seq)
        start = idx * node.width // base
        end = start + node.width


    else:
      stat, isSimilar = normal_test(node.pixels)
      if isSimilar:
        start = 
        end = start + node.width

        return stat

    stat = 0.
    node.split()
    stat += self._find_regions(node.left_child)
    stat += self._find_regions(node.right_child)
    return stat


  def compute(self):
    # horizontal homogeneity 
    for left_root, right_root in zip(left_roots, right_roots):
      pass

    num_cols = self.left_img.shape[1]
    res = 0.
    for idx in range(num_cols):
      root = Node(self.left_img[:, idx])
      res += self._find_regions(root)








class Similarity:
  """
    Interface for incorporating multiple components in objective function
    Args:
      left_node: row node for left tree
      right_node: row node for right tree
      strip: strip length of row trees
      use_horizontal: use horizontal intensity comparison
      use_vertical: use vertical intensity comparison
      use_homogeneous: use homoegneity test
  """
  def __init__(self, left_node, right_node, use_horizontal, use_vertical, use_homogeneous):
    self.left_node = left_node
    self.right_node = right_node
    self.strip = left_node.strip
    self.use_horizontal = use_horizontal 
    self.use_vertical = use_vertical
    self.use_homogeneous = use_homogeneous

    use_one = self.use_horizontal or self.use_vertical or self.use_homogeneous
    assert use_one, "Must use some similarity measure!"

  # compare horizontal intensities
  def horizontal(self):
    diff = self.left_node.pixels - self.right_node.pixels
    return np.linalg.norm(diff)

  # compare vertical smoothness
  def vertical(self):
    assert self.strip > 1, "Vertical smoothness requires valid strip"
    res = 0.
    for idx in range(self.left_node.width):
      left_column = np.asarray([self.left_node.pixels[s, idx] for s in range(self.strip)])
      right_column = np.asarray([self.right_node.pixels[s, idx] for s in range(self.strip)])
      diff = left_column - right_column
      res += np.linalg.norm(diff)
    return res

  # compare homogeneity of node
  def homogeneous(self, root):
    # constant intensity
    if (root.pixels == root.pixels[0]).all():
      return 0., True
    if root.width == 2:
      sse = math.sqrt((root.pixels[0] - root.pixels[1]) ** 2)
      return sse.sum()

    # fit a low-order polynomial
    x = [i for i in range(root.width)]
    degree = 1
    p, residuals, rank, _, _ = np.polyfit(x, root.pixels, degree, full=True)
    return residuals.sum()

  # TODO: weightage?
  def run(self):
    objective = 0.
    if self.use_horizontal:
      objective += self.horizontal()
    if self.vertical:
      objective += self.vertical()
    if self.use_homogeneous:
      objective += self.homogeneous()
    return objective
