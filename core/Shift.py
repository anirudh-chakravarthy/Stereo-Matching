from copy import deepcopy

from core.Shift_utils import reach_level, binary_add
from core.Tree import Node


class ObjectFragment:
  '''
  Fields
    seq: sequence corr. to object
    shifted_seq: resultant shifted sequences for the object
    root: root of tree
    new_tree: root of new shifted tree for all sequences
  '''
  def __init__(self, root, seq):
    self.seq = seq
    self.shifted_seq = None
    self.root = root
    self.new_tree = deepcopy(root) # create duplicate root for accessing new tree!
    self.new_tree.left_child = self.new_tree.right_child = None

  # shift each object under the specific resolution
  def _shifted_representation(self, shift):
    self.shifted_seq = binary_add(self.seq, bin(shift))
    print("Seq:", self.seq, "Shift:", shift)
    print("Shifted Seq:", self.shifted_seq)

  # generate trees for the shifted object
  def shifted_tree(self, shift):
    self._shifted_representation(shift)
    orig_itr = self.root
    new_itr = self.new_tree
    
    # traverse shifted sequence 
    for j in range(len(self.shifted_seq)):
      # left node
      if self.shifted_seq[j] == "0":
        # traverse original tree based on original sequence
        if self.seq[j] == "0":
          orig_itr = orig_itr.left_child
        else:
          orig_itr = orig_itr.right_child
        # copy data to corresponding node in new tree
        if new_itr.left_child is None:
          new_itr.left_child = Node(orig_itr.pixels, self.shifted_seq[:j+1])
        new_itr = new_itr.left_child

      # right node
      else:
        # traverse original tree based on original sequence
        if self.seq[j] == "0":
          orig_itr = orig_itr.left_child
        else:
          orig_itr = orig_itr.right_child
        # copy data to corresponding node in new tree
        if new_itr.right_child is None:
          new_itr.right_child = Node(orig_itr.pixels, self.shifted_seq[:j+1])
        new_itr = new_itr.right_child
    print(shi)
    return new_itr
