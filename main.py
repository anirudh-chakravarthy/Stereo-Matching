import numpy as np
from PIL import Image

from core.Tree import Node


image = Image.open('download.jpeg').convert('L')
image = np.asarray(image, dtype="int32")
print(image.shape)

root = Node(image[0])
print(root.mean, root.stdev)
print(image[0])

root.split()
print(root.left_child.mean, root.left_child.stdev)
print(root.right_child.mean, root.right_child.stdev)