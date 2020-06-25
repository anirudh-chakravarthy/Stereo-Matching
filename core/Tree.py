import numpy as np

'''
Doubts
	1. How do I find nodes at same level for the subtree?
'''


'''
TODO:
  1. Matching, shift can be passed around as a parameter
  2. Similarity measure?
'''

# tree node fields
class Node:
	'''
		Fields
			pixels: list of pixel corresponding to tree node
			mean, stdev: homogeneity measures for object segments
			left_child: instance of left child node
			right_child: instance of right child node
      width: width of subtree rooted at current node
      half: left half - 0 or right - 1 (necessary for performing tree shifts)
      level: level of node in the tree
	'''
	def __init__(self, pixels, half, level=1):
		self.pixels = pixels
		self.left_child = None
		self.right_child = None
    self.width = len(self.pixels) if self.pixels is not None else 0# size of segment is the width of tree
    self.level = level
    self.half = half

		self.compute_statistics()

	# split node into two child nodes
	def split(self):
		self.left_child = Node(self.pixels[:len(self.pixels) // 2], 0, level = 1 + self.level)
		self.right_child = Node(self.pixels[len(self.pixels) // 2:], 1, level = 1 + self.level)

	# gather homogenity metrics for node
	def compute_statistics(self):
		self.mean = np.mean(self.pixels)
		self.stdev = np.std(self.pixels)


# match two trees using a recursive procedure
def match(left_tree, right_tree):
