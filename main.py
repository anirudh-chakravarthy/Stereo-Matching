import os
import sys
import argparse
import numpy as np
import cv2

from core.Disparity import get_disparities, ColumnTree
from core.Match import MatchTrees
from core.Tree import Node, grow_tree
from core.utils import normalize, traverse, write_disparity_img


IMAGE_EXT = (".jpg", ".jpeg", ".png")
VID_EXT = (".mp4")

"""
Doubts
  1. How to polyfit over a strip? - labels are now 3D?
"""


# row trees - perform matching
def match_rows(left_image, right_image, num_rows, strip_len):
  row_trees_left, row_trees_right = [], []
  disparity = np.zeros(left_image.shape[:-1])
  cost = 0.

  # row-wise matching
  for row_start in range(0, num_rows, strip_len):
    row_end = row_start + strip_len # a bit hacky
    left_root = Node(left_image[row_start:row_end])
    right_root = Node(right_image[row_start:row_end])
    right_root = grow_tree(right_root)
    match_trees = MatchTrees(left_root, right_root)
    cost += match_trees.run()

    disp_obj = get_disparities(right_root)
    disparity[row_start:row_end] = disp_obj.get_disparity_values()
    row_trees_left.append(left_root)
    row_trees_right.append(right_root)
  return row_trees_left, row_trees_right, disparity, match_objective



# # grow column trees for redundancy
# def add_columns(left_image, right_image, num_cols, strip_len):
#   col_trees_left, col_trees_right = [], []
#   for col_start in range(0, num_cols, strip_len):
#     col_end = -1 if col_start + strip_len >= num_cols else col_start + strip_len
#     left_root = Node(left_image[:, col_start:col_end])
#     right_root = Node(right_image[:, col_start:col_end])
#     left_root = grow_tree(left_root, stop="homogeneity")
#     right_root = grow_tree(right_root, stop="homogeneity")
#     col_trees_left.append(left_root)
#     col_trees_right.append(right_root)
#   return col_trees_left, col_trees_right


# multiple frames
def load_video(video_file, strip_len, use_disp_smoothness):
  left_frame, right_frame = None, None
  left_row_list, right_row_list = [], []
  left_col_list, right_col_list = [], []

  # play video frame by frame
  i = 0
  video = cv2.VideoCapture(video_file)
  match_objective =0.
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

    num_rows, num_cols = left_frame[0:2]
    # perform matching
    left_row_roots, right_row_roots, disparity, cost = match_rows(left_frame, right_frame, num_rows, strip_len)
    left_row_list.append(left_row_roots)
    right_row_list.append(right_row_roots)
    if use_disp_smoothness:
      column_obj = ColumnTree(left_frame, disparity)
      cost += column_obj.vertical_smoothness()
    match_objective += cost
    write_disparity_img(video_file, disparity, "%03d" % str(i))
    i += 1
  video.release()
  cv2.destroyAllWindows()
  return match_objective


# stereo images
def load_image(left_img, right_img, strip_len, use_disp_smoothness):
  left_image = cv2.imread(left_img)
  right_image = cv2.imread(right_img)
  assert left_image.shape == right_image.shape, "Should have same shape. Got \
                                                {0} and {1}".format(left_image.shape, right_image.shape)
  num_rows, num_cols = left_image.shape[0:2]
  left_row_roots, right_rows_roots, disparity, cost = match_rows(left_image, right_image, num_rows, strip_len)
  if use_disp_smoothness:
    column_obj = ColumnTree(left_image, disparity)
    cost += column_obj.vertical_smoothness()
  write_disparity_img(left_img, disparity)
  return match_objective


def main():
  parser = argparse.ArgumentParser(description='Matching on rectified stereo images or a video track.')
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument('-i', '--images', nargs=2, help='match two images')
  group.add_argument('-v', '--video', nargs=1, help='match video frame by frame')
  parser.add_argument('-s', '--strip', type=int, default=2, help='length of row or column strips')
  parser.add_argument('-d', '--disp_smoothness', type=bool, action='store_true', 
                          help='include disparity vertical smoothness in match objective')
  args = parser.parse_args()

  assert args.strip > 0, "Strip length must be positive"

  # video
  if args.video:
    _, ext = os.path.splitext(args.video)
    assert ext in VID_EXT, "{} not supported".format(ext)
    cost = load_video(args.video, args.strip, args.disp_smoothness)

  # stereo images
  if args.images:
    _, left_ext = os.path.splitext(args.images[0])
    _, right_ext = os.path.splitext(args.images[1])
    assert left_ext in IMAGE_EXT, "{} not supported".format(left_ext)
    assert right_ext in IMAGE_EXT, "{} not supported".format(right_ext)
    cost = load_image(args.images[0], args.images[1], args.strip, args.disp_smoothness)


if __name__ == "__main__":
  main()
