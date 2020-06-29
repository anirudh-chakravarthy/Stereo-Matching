import numpy as np
from PIL import Image

from core.Match import match
from core.Tree import Node


image = Image.open('download.jpeg')
image = np.asarray(image, dtype="int32")

root = Node(image)
print(root.mean, root.stdev)
print(root.width)
# print(image[0])

root.split()
print(root.left_child.mean, root.left_child.stdev)
print(root.right_child.mean, root.right_child.stdev)