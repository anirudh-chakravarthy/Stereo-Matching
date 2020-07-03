import sys
import math

from core.Shift import ObjectFragment
from core.Shift_utils import reach_level
from core.Tree import similarity

L2_THRESHOLD = 0.30


# mark entire subtree as matched
def propagate_match(left_tree, right_tree):
  if left_tree is None:
    return

  left_tree.match = True
  right_tree.match = left_tree
  propagate_match(left_tree.left_child, right_tree.left_child)
  propagate_match(left_tree.right_child, right_tree.right_child)


# match left tree node with corresponding right tree node - shift onto others if not match
def match(left_tree, right_tree, left_root=None, right_root=None, shift=0):
  if left_tree is None or right_tree is None:
    return

  if left_root is None:
    left_root = left_tree
  if right_root is None:
    right_root = right_tree

  # already matched
  if right_tree.match:
    return

  quality = similarity(left_tree, right_tree)
  # match found
  if quality < L2_THRESHOLD:
    # right_tree.match = left_tree
    right_tree.quality = quality
    right_tree.disparity = shift
    propagate_match(left_tree, right_tree)
    # left_tree.match = True
    print("Matched {0} with {1} with quality: {2}".format(left_tree.seq, right_tree.seq, quality))
    return

  match(left_tree.left_child, right_tree.left_child, left_root, right_root, shift)
  match(left_tree.right_child, right_tree.right_child, left_root, right_root, shift)

  # pixel-level still no match
  if left_tree.width == 1:
    pass
  # if children matched - node is matched
  elif left_tree.left_child.match and left_tree.right_child.match:
    left_tree.match = True

  # matching complete
  if left_tree == left_root:
    return

  # print("{} not matched yet!".format(left_tree.seq))

  # node still not matched - perform shifting on current node
  if not left_tree.match:
    obj_frag = ObjectFragment(left_root, left_tree.seq)
    right_nodes = reach_level(right_root, left_tree.level)

    quality = [0] * len(right_nodes)
    # perform shift 
    for i, right_node in enumerate(right_nodes):
      # print("Match.py:", left_tree.seq, right_node.seq)
      shift_amt = int(right_node.seq, 2) - int(left_tree.seq, 2) # difference in sequences = shift multiple
      # if already matched / direct match already attempted anyways / sizes of fragments are different [if odd width]
      if shift_amt == 0 or right_node.match or right_node.width != left_tree.width:
        quality[i] = math.inf
        continue
      # new_tree = obj_frag.shifted_tree(shift_amt)
      quality[i] = similarity(left_tree, right_node)

    # match found
    if min(quality) < L2_THRESHOLD:
      idx = quality.index(min(quality))
      right_match_node = right_nodes[idx]
      # right_match_node.match = left_tree
      right_match_node.quality = quality[idx]
      right_match_node.disparity = shift + (int(right_match_node.seq, 2) - int(left_tree.seq, 2)) * left_tree.width
      # left_tree.match = True  
      propagate_match(left_tree, right_match_node)
      print("Matched {0} with {1} at idx {2} with quality: {3}, disparity: {4}".format(left_tree.seq, right_match_node.seq, idx, quality[idx], right_match_node.disparity))

    # not matched still - lies in shadow region?
    else:
      pass

      # print("Shifted Match.py:", new_tree.seq)
      # new_shift = shift + shift_amt * left_tree.width
      # match(new_tree, right_node, left_root, right_root, new_shift)
      # # matching with first node which provides good quality
      # if right_node.match == left_tree:
      #   break

      # # no match exists - shadown region i.e unknown depth?
      # if i == len(right_nodes) - 1:
      #   pass
