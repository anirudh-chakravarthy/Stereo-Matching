from copy import deepcopy


# return H - LSB position containing a 1
def find_lsb(num):
  sign = 1 if num >= 0 else -1
  binary = str(bin(num))
  lsb = binary.rfind('1')
  return sign, lsb


# bit-wise binary addition - a: sequence string ('010...'), b: shift amount in binary ('0bxxx'), res: resultant sequence
def binary_add(a, b, carry_in=0):
  res = bin(int(a, 2) + int(b, 2) + carry_in)
  res = res[2:] # strip '0b'
  # drop carry
  if len(res) > len(a):
    res = res[1:]
  # pad with zeros to maintain same length as input sequence
  elif len(res) < len(a):
    zeros = "0" * (len(a) - len(res))
    res = zeros + res
  return res


# traverse tree to retrieve all nodes and corresponding root nodes at a given level
def reach_level(tree, level):
  nodes = []
  parents = []
  if tree is None:
    return nodes, []

  # traverse until level
  if tree.level <= level:
    left_list, left_parents = reach_level(tree.left_child, level)
    right_list, right_parents = reach_level(tree.right_child, level)
    if left_list:
      nodes = nodes + left_list
    if right_list:
      nodes = nodes + right_list
    # gather root nodes i.e nodes at level H
    if tree.level == level:
      parents.append(tree)
    else:
      parents = left_parents + right_parents
    return nodes, parents

  # level found - return node
  else: 
    nodes = nodes + tree
    return nodes, []


# deep copy tree structure - for shifting tree
def copy_tree(root):
  if root is None:
    return None
  root_copy = deepcopy(root)
  root_copy.left_child = copy_tree(root.left_child)
  root_copy.right_child = copy_tree(root.right_child)
  return root_copy
