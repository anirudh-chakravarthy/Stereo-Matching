from core.Shift import ObjectFragment
from core.Shift_utils import reach_level
from core.Tree import similarity

L2_THRESHOLD = 0.05


# match left tree node with corresponding right tree node - shift onto others if not match
def match(left_root, left_tree, right_root, right_tree, shift=0):
  # already matched
  if right_tree.match:
    return

  quality = similarity(left_tree, right_tree)
  # match found
  if quality < L2_THRESHOLD:
    right_tree.match = left_tree
    right_tree.quality = quality
    right_tree.disparity = shift
    left_tree.match = True
    return

  match(left_root, left_tree.left_child, right_root, right_tree.left_child, shift)
  match(left_root, left_tree.right_child, right_root, right_tree.right_child, shift)

  # if children matched - node is matched
  if left_tree.left_child.match and left_tree.right_child.match:
    left_tree.match = True

  # node still not matched - perform shifting on current node
  if not left_tree.match:
    obj_frag = ObjectFragment(left_root, [left_tree.seq])
    right_nodes = reach_level(right_tree, left_tree.level)
    
    # perform shift 
    for i, right_node in enumerate(right_nodes):
      # direct match without shift has already been tried - waste of effort
      if left_tree.seq == right_node.seq:
        continue

      shift_amt = int(right_node.seq, 2) - int(left_tree.seq, 2) # difference in sequences = shift multiple
      new_tree = obj_frag.shifted_tree(shift_amt)
      new_shift = (shift + shift_amt) * left_tree.width
      match(left_root, new_tree, right_root, right_node, new_shift)
      # matching with first node which provides good quality
      if right_node.match:
        break

      # no match exists - shadown region i.e unknown depth?
      if i == len(right_nodes) - 1:
        pass


    # shifted match exists
    # if min(quality) < L2_THRESHOLD:
    #   match_index = quality.index(min(quality))
    #   right_node = right_nodes[match_index]
    #   right_tree.match = left_tree
    #   right_tree.quality = quality
    #   # right_tree.disparity = shift
    #   left_tree.match = True

    # still no match - is it in a shadow region i.e unknown depth??
    # else:
    #   pass
