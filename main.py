import os
import sys
import numpy as np
import cv2
# from PIL import Image

from core.Match import match
from core.Tree import Node

from core.Shift_utils import reach_level


IMAGE_EXT = (".jpg", ".jpeg", ".png")
VID_EXT = (".mp4")

'''
Doubts
  1. Which similarity measure to use? L2?
  2. How to use homogenity to stop splitting at intermediate level? Chi-squared test?
  3. Seems to take a lot of time for matching!
  4. Do we even need to perform shifting as an operation? Could we get list at level, and just match with all?
'''

'''
TODO
  1. Not sure whether match is working correctly? - rewrite match - too circuitous currently
'''

# store flattened disparity values from tree structure
class Disparity:
  def __init__(self, length):
    self.num_values = length
    self.disparities = np.zeros(self.num_values)

  def set_disparity(self, start, end, value):
    self.disparities[start:end] = value

  def get_disparity_values(self):
    return self.disparities


# traversal - for debugging
def traverse(root):
  if root is None:
    return
  print("Level:", root.level, "Width:", root.width)
  traverse(root.left_child)
  traverse(root.right_child)


# normalize input RGB frame
def normalize(x):
  z = (x - x.mean(axis=(0,1), keepdims=True)) / x.std(axis=(0,1), keepdims=True)
  return z


def build_tree(row, root=None):
  # create tree root node
  if root is None:
    root = Node(row)

  # reached pixel-level - REPLACE WITH HOMOGENEITY BASED TERMINATION LATER
  if root.width == 1:
    return root

  # grow the tree
  root.split()
  build_tree(row, root.left_child)
  build_tree(row, root.right_child)
  return root


# fill slices in disparity row based on tree matches
def get_disparities(tree, root=None, disparity=None):
  if tree is None:
    return

  if root is None:
    root = tree

  if disparity is None:
    disparity = Disparity(tree.pixels.shape[0])

  # traverse until match
  if not tree.match:
    get_disparities(tree.left_child, root, disparity)
    get_disparities(tree.right_child, root, disparity)

  # fill the disparity in a flattened format
  else:
    nodes = reach_level(root, len(tree.seq) + 1)
    base = len(nodes)
    position = nodes.index(tree)
    slice_start = position * disparity.num_values // base
    slice_end = slice_start + tree.width
    disparity.set_disparity(slice_start, slice_end, tree.disparity)

  return disparity


# multiple frames
def load_video(video_file):
  filename = video_file.split('.')[0]
  video = cv2.VideoCapture(video_file)
  i = 0
  left_frame, right_frame = None, None
  left_tree, right_tree = None, None
  disparity = None
  # play video frame by frame
  while(video.isOpened()):
    ret, frame = video.read()
    if ret == False:
      break
    # first frame
    if i == 0:
      left_frame = frame
      i += 1
      continue
    # second frame
    elif i == 1:
      right_frame = frame
    # continue stream
    else:
      left_frame = right_frame
      right_frame = frame

    # normalize frames
    left_frame = normalize(left_frame)
    right_frame = normalize(right_frame)

    disparity = np.zeros(left_frame.shape[:-1])
    # tree for each row
    for row in range(left_frame.shape[0]):
      left_tree = build_tree(left_frame[row])
      right_tree = build_tree(right_frame[row])
      match(left_tree, right_tree)
      disp_obj = get_disparities(right_tree)
      disparity[row] = disp_obj.get_disparity_values()

      # matched - generate disparity map for the row
      if left_tree.match:
        print("Frame:", str(i), "Row:", row, "matched!")

      else:
        print("Frame:", str(i), "Row:", row, "not entirely matched!")
        print("Possibly some regions in shadow exist?")

    os.makedirs(filename, exist_ok=True)
    cv2.imwrite(os.path.join(filename, "%03d" % i + ".jpg"), disparity)
    i += 1
  video.release()
  cv2.destroyAllWindows()


# stereo images
def load_image(left_img, right_img):
  left_image = cv2.imread(left_img)
  right_image = cv2.imread(right_img)
  assert left_image.shape == right_image.shape, "Stereo images should have same shape"

  disparity = np.zeros(left_image.shape[:-1])
  # tree for each row
  for row in range(left_image.shape[0]):
    left_tree = build_tree(left_image[row])
    right_tree = build_tree(right_image[row])
    match(left_tree, right_tree)
    disp_obj = get_disparities(right_tree)
    disparity[row] = disp_obj.get_disparity_values()

    # matched - generate disparity map for the row
    if left_tree.match:
      print("Row:", row, "matched!")

    else:
      print("Row:", row, "not entirely matched!")
      print("Possibly some regions in shadow exist?")

    left_filename, left_ext =  os.path.splitext(left_img)
    cv2.imwrite(left_filename + "_disp" + left_ext, disparity)


if __name__ == "__main__":
  assert len(sys.argv) in (2, 3), "Usage: python main.py video.mp4 or python main.py pic1.jpg pic2.jpg" 
  file = sys.argv[1]
  filename, ext = os.path.splitext(file)
  if ext in VID_EXT:
    load_video(file)
  elif ext in IMAGE_EXT:
    _, right_ext = os.path.splitext(sys.argv[2])
    assert right_ext in IMAGE_EXT, "Invalid right image extension"
    left_img = sys.argv[1]
    right_img = sys.argv[2]
    load_image(left_img, right_img)
  else:
    assert False, "Extension not supported"
