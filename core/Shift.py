from copy import deepcopy

from core.Tree import Node
from core.Shift_utils import find_lsb, reach_level, copy_tree, binary_add

'''
Doubts
  1. How to know which is the corresponding node in right tree
  2. While arithmetic will play with 'half', 
'''


class RowObject:
  '''
    Fields
      seqs: list of sequences corr. to each object
      nodes: list of nodes consisting of each sequence - for copying data later
      shifted_seqs: list of resultant shifted sequences for each object
      parents: list of parent nodes for each object
  '''
  def __init__(self, parents):
    self.seqs = []
    self.nodes = []
    self.shifted_seqs = []
    self.parents = []
    for parent in parents:
      new_parent = deepcopy(parent)
      new_parent.left_child = parent.right_child = None
      self.parents.append(new_parent)

  # gather all objects
  def add_sequence(self, sequence, nodes):
    self.seqs.append(sequence)
    self.nodes.append(nodes)

  # shift each object under the specific resolution
  def shifted_representation(self, shift):
    for seq in self.seqs:
      shifted_seq = binary_add(seq, bin(shift))
      self.shifted_seqs.append(shifted_seq)

  # generate trees for the shifted object
  def shifted_tree(self):
    for i, seq in enumerate(self.sequences):
      tmp = self.parents[i]
      nodes = self.nodes[i]
      # traverse sequence
      for j in range(len(seq)):
        # left node
        if seq[j] == "0":
          if tmp.left_child is None:
            tmp.left_child = Node(nodes[j].pixels, 0, nodes[j].level)
          tmp = tmp.left_child

        # right node
        else:
          if tmp.right_child is None:
            tmp.right_child = Node(nodes[j].pixels, 1, nodes[j].level)
          tmp = tmp.right_child


# reach leaf nodes, gather sequences and store in row object
def traverse_tree(tree, row_obj, nodes=[], seq=""):
  if tree is None:
    if seq: # add all non-trivial sequences
      row_obj.add_sequence(seq)

  shift_tree(tree.left_child, row_obj, nodes + tree.left_child, seq + str(tree.half))
  shift_tree(tree.right_child, row_obj, nodes + tree.right_child, seq + str(tree.half))


# def shift_tree(tree, shift):
#   assert shift != 0, "Shift needs to be non-zero"
#   direction, h = find_lsb(shift)
#   nodes_h, roots_h = reach_level(tree, h)
#   # if shift > 0, right-to-left postorder traversal
#   if direction > 0: 
#     nodes_h = reverse(nodes_h)
#     roots_h = reverse(roots_h)
#   for i, node in enumerate(nodes_h):
#     nodes_h[i] = copy_tree(node)
