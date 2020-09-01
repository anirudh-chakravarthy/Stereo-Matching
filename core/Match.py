import sys
import math
import numpy as np

# from core.Similarity import Similarity
from core.utils import reach_level
from core.Hypothesis import normal_test


class MatchTrees:
  '''
  Fields
    left_root: root of left tree
    right_tree: root of right tree
    similarity_test: statistical test for comparing object fragments
  '''
  def __init__(self, 
               left_root, 
               right_root, 
               use_homogeneity=False,

  ):
    self.left_root = left_root
    self.right_root = right_root
    self.use_homogeneity = use_homogeneity
    self.match_objective = 0.
    # self.similarity_obj = Similarity(left_root, right_root, horizontal, vertical, homogeneity)

  def similarity_test(self, left_tree, right_tree):
    diff = left_tree.pixels - right_tree.pixels
    quality = np.linalg.norm(left_tree.pixels - right_tree.pixels)
    stat, similar = normal_test(left_tree.pixels - right_tree.pixels)
    return quality, stat, similar

  # mark entire right subtree as matched
  def _propagate_match(self, left_tree, right_tree):
    if right_tree is None:
      return

    left_tree.match = True
    right_tree.match = left_tree
    self._propagate_match(left_tree, right_tree.left_child)
    self._propagate_match(left_tree, right_tree.right_child)

  # match the subtrees directly
  def _direct_match(self, left_tree, right_tree):
    quality, stat, isSimilar = self.similarity_test(left_tree, right_tree)
    if isSimilar:
      right_tree.quality = quality
      self.match_objective += quality
      if self.use_homogeneity:
        self.match_objective += 1 - stat
      right_tree.disparity = 0
      self._propagate_match(left_tree, right_tree)
      print("Directly matched {0} with {1} with quality: {2}"\
              .format(left_tree.seq, right_tree.seq, quality))
      return

    # reached pixel level
    if right_tree.width == 1:
      return

    # left tree is dynamically grown
    left_tree.split()
    self._direct_match(left_tree.left_child, right_tree.left_child)
    self._direct_match(left_tree.right_child, right_tree.right_child)

  # perform match with all unmatched nodes at given level
  def _match_level(self, left_tree, right_tree):
    if left_tree is None or left_tree.match:
      return

    # extract all nodes at given level
    right_nodes = reach_level(self.right_root, left_tree.level)
    quality = [0] * len(right_nodes)
    stat = [0] * len(right_nodes)
    isSimilar = [False] * len(right_nodes)
    exactPosition = 0

    # match left nodes with all right nodes at given level
    for i, right_node in enumerate(right_nodes):
      # skip if same index already tried before / already matched / different width 
      if right_node.seq == left_tree.seq or right_node.match or left_tree.width != right_node.width:
        quality[i] = math.inf
        if right_node.seq == left_tree.seq:
          exactPosition = i
        continue
      quality[i], stat[i], isSimilar[i] = self.similarity_test(left_tree, right_node)

    # greedy match - best quality
    idx = quality.index(max(quality))
    if isSimilar[idx]:
      self.match_objective += quality[idx]
      if self.use_homogeneity:
        self.match_objective += 1. - stat[idx]
      right_match_node = right_nodes[idx]
      right_match_node.quality = quality[idx]
      right_match_node.disparity = abs(exactPosition - idx) * left_tree.width
      self._propagate_match(left_tree, right_match_node)
      print("Matched {0} with {1} at idx {2} with quality: {3}, disparity: {4}"\
              .format(left_tree.seq, right_match_node.seq, idx, quality[idx], right_match_node.disparity))

    # best isn't good enough
    else:
      if left_tree.left_child is None and left_tree.right_child is None:
        print("Unable to match", left_tree.seq, "Width:", left_tree.width, "Quality:", max(quality))
      self._match_level(left_tree.left_child, right_tree.left_child)
      self._match_level(left_tree.right_child, right_tree.right_child)

  # match the two images
  def run(self):
    self._direct_match(self.left_root, self.right_root) # direct matches
    self._match_level(self.left_root, self.right_root) # match remaining nodes
    return self.match_objective
