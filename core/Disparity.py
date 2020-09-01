import numpy as np
from statistics import mode

from core.Tree import Node
from core.Hypothesis import normal_test
from core.utils import reach_level


class ColumnTree:
  '''
    Include vertical smoothness across homogeneous columns to objective
  '''
  def __init__(self,
               img
               disparities
  ):
    self.img = img
    self.disparities = disparities
    self.match_objective = 0.
    self._regions = [] # memory for each column

  # get vertically homogenous regions fr
  def _find_vertical_regions(self, root):
    if root.width == 1:
      return

    if root.width == 2:
      if np.allclose(root.pixels[:, 0], root.pixels[:, 1], rtol=5e-2, atol=0):
        self._regions.append(root)
        return

    else:
      quality, isSimilar = homogeneity_test(root.pixels)
      if isSimilar:
        self._regions.append(root)
        return

    root.split()
    self._find_vertical_regions(root.left_child)
    self._find_vertical_regions(root.right_child)


  def _enforce_smoothness(self):
    for region in self._regions:
      if region.seq:
        base = int(region.seq, 2)
        power = 2 ** len(region.seq)
        start = base * region.width // power
        end = start + region.width
      else:
        start, end = 0, region.width
      disparity = self.disparities[col, start:end]
      frequent = mode(disparity)
      for element in set(disparity):
        if abs(element - frequent) > 5:
          self.match_objective += abs(element - frequent)


  def vertical_smoothness(img, disparities):
    num_cols = img.shape[1]
    for col in num_cols:
      root = Node(np.expand_dims(img[:, col], axis=0)) # temporary measure for handling strips
      self._find_vertical_regions(root)
      self._enforce_smoothness()
      self._regions = []
    return self.match_objective


# store flattened disparity values from tree structure
class Disparity:
  def __init__(self, length):
    self.num_values = length
    self.disparities = np.zeros(self.num_values)

  def set_disparity(self, start, end, value):
    self.disparities[start:end] = value

  def get_disparity_values(self):
    return self.disparities


def get_disparities(tree, disparity=None):
  if tree is None:
    return

  if disparity is None:
    disparity = Disparity(tree.pixels.shape[0])

  # not matched 
  if not tree.match:
    get_disparities(tree.left_child, disparity)
    get_disparities(tree.right_child, disparity)

  # generate disparity map wrt left image
  else:
    matching_node = tree.match
    if not matching_node.seq:
      slice_start = 0
      slice_end = tree.width
    else:
      position = int(matching_node.seq, 2) 
      base = 2 ** (matching_node.level - 1)
      slice_start = position * disparity.num_values // base
      slice_end = slice_start + tree.width
    disparity.set_disparity(slice_start, slice_end, tree.disparity)
  return disparity
