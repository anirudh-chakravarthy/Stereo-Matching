import os
import numpy as np
import cv2


# normalize input RGB frame
def normalize(x):
  z = (x - x.mean(axis=(0,1), keepdims=True)) / x.std(axis=(0,1), keepdims=True)
  return z


# traversal - for debugging
def traverse(root):
  if root is None:
    return
  print("Level:", root.level, "Width:", root.width)
  traverse(root.left_child)
  traverse(root.right_child)


# write disparity mapping to image
def write_disparity_img(file, disparity, id="_disp"):
  filename, write_ext =  os.path.splitext(file)
  # video - write as jpg
  if id != "_disp":
    write_ext = ".jpg"
  cv2.imwrite(filename + id + write_ext, disparity)


def reach_level(tree, level):
  nodes = []
  if tree is None:
    return nodes
  assert tree.level <= level, "Reached greater level than %d" % level
    
  # traverse until level
  if tree.level < level:
    left_list = reach_level(tree.left_child, level)
    right_list = reach_level(tree.right_child, level)
    if left_list:
      nodes = nodes + left_list
    if right_list:
      nodes = nodes + right_list
  # level found - return node
  else: 
    nodes = [tree]
  return nodes