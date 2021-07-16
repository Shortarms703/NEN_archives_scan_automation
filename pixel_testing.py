import math
import os
from pathlib import Path
from PIL import Image

from matplotlib import pyplot as plt
import matplotlib
import cv2 as cv

# IMPORTANT:
# img[y:y+h, x:x+w]
# img[y1:y2, x1:x2]

matplotlib.rcParams["figure.dpi"] = 300



def pixel_difference(p1, p2):
    p1 = [int(x) for x in p1]
    p2 = [int(x) for x in p2]
    distance = math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2 + (p2[2] - p1[2]) ** 2)
    return distance


def find_lr_side_margin(img_path, side, x_start, x_end, y_start, y_end, inner_step=5, outer_step=20, min_pixel_diff=25, min_edge_points=30):
    img = cv.imread(img_path)
    edge_points = []
    for y in range(y_start, y_end, outer_step):
        if side == 'left':
            last = img[y, x_start]
            x_step = inner_step
        if side == 'right':
            x_start = int(3007 if x_start == 3008 else x_start)
            last = img[y, x_start - 1]
            x_step = -1 * inner_step
        for x in range(x_start, x_end, x_step):
            # x = x * inner_step
            current = img[y, x]
            diff = pixel_difference(current, last)
            if diff > min_pixel_diff:
                edge_points.append([x, y])
                break
            last = img[y, x]

    if len(edge_points) < min_edge_points:
        raise ValueError('No margin found for image:' + img_path)
    else:
        return edge_points


def draw_margin_line(img, edge_points, average, thickness=3, top_bottom=False):
    if top_bottom is True:
        img = cv.line(img, (edge_points[0][0], average), (edge_points[-1][0], average), (0, 0, 255), thickness)
    else:
        img = cv.line(img, (average, edge_points[0][1]), (average, edge_points[-1][1]), (0, 0, 255), thickness)
    return img


def find_margins(path, first_image=False, last_image=False):
    # TODO draw margins should take averages from sides and draw the margins at the very end
    img = cv.imread(path)
    shape = img.shape
    shape = {'x': shape[1], 'y': shape[0]}
    sides = {} # left right top bottom middle

    side = 'left'
    if first_image is True:
        edge_points = find_lr_side_margin(path, side, shape['x'] // 2 - 200, shape['x'] // 2 + 300, 0, shape['y'])
    else:
        edge_points = find_lr_side_margin(path, side, 0, 500, 0, shape['y'])

    x_edge_points = [x[0] for x in edge_points]
    average = sum(x_edge_points) // len(x_edge_points)
    sides[side] = average

    # TODO deal with this:
    # if average < largest_crop['left'] and 'single' not in sides:
    #     largest_crop['left'] = average

    side = 'right'
    if last_image is True:
        edge_points = find_lr_side_margin(path, side, shape['x'] // 2 + 200, shape['x'] // 2 - 300, 0, shape['y'])
    else:
        edge_points = find_lr_side_margin(path, side, shape['x'], shape['x'] - 500, 0, shape['y'])

    x_edge_points = [x[1] for x in edge_points]
    average = sum(x_edge_points) // len(x_edge_points)
    sides[side] = average

    # TODO deal with this:
    # if average > largest_crop['right'] and 'single' not in sides:
    #     largest_crop['right'] = average


    inner_step = 5
    outer_step = 20
    for side in ['top', 'bottom']:
        edge_points = []
        for px in range(0, shape['x'], outer_step):
            if side == 'top':
                last = img[0, px]
            if side == 'bottom':
                last = img[shape['y'] - 1, px]
            for py in range(0, 500, inner_step):
                if side == 'bottom':
                    py = shape['y'] - py - 1

                current = img[py, px]
                diff = pixel_difference(current, last)
                if diff > 25:
                    edge_points.append([px, py])
                    break
                last = img[py, px].copy()

        edge_y = [x[1] for x in edge_points]
        average = sum(edge_y) // len(edge_y)
        sides[side] = average

        # TODO fix this
        # if average < largest_crop['top'] and side == 'top' and 'single' not in sides:
        #     largest_crop[side] = average
        # if average > largest_crop['bottom'] and side == 'bottom' and 'single' not in sides:
        #     largest_crop[side] = average

    # TODO find middle


    # TODO then find middle points
    middle_points = {'left', 'right'}

    # img = cv.cvtColor(img, cv.COLOR_RGB2BGR) # idk if this is needed, might be getting reversed later

    return sides, middle_points


# images = sorted(os.listdir('1980_06 June'))
dir_path = '/Users/joshua/Desktop/NEN archives'
# years = sorted(os.listdir(dir_path))[4:-6]
years = sorted(os.listdir(dir_path))[4:-6]
years = ['1983_04 April']
# images.remove('.DS_Store')
largest_box = {'x': 0, 'y': 0}
for image_directory in years:
    jpg_list = sorted(os.listdir(os.path.join(dir_path, image_directory)))
    jpg_list = [x for x in jpg_list if all(['.pdf' not in x, '.DS_Store' not in x])]

    edition_sides = []
    for i, image_file_name in enumerate(jpg_list):
        print(image_file_name)

        if i == 0: # if its the first page
            sides, middle_points = find_margins(os.path.join(dir_path, image_directory, image_file_name), first_image=True)
        elif i == len(image_directory) - 1: # if its the last page
            sides, middle_points = find_margins(os.path.join(dir_path, image_directory, image_file_name), last_image=True)
        else: # not first or last page
            sides, middle_points = find_margins(os.path.join(dir_path, image_directory, image_file_name))
        edition_sides.append(sides)
        img = cv.imread(os.path.join(dir_path, image_directory, image_file_name))
        img = cv.rectangle(img, (sides['left'], sides['top']), (sides['right'], sides['bottom']), (255, 0, 0), 3)
        plt.imshow(img)
        plt.axis('off')
        plt.show()

    # finds largest box for a page
    for sides in edition_sides:
        pass

    continue
    img_list = []
    for i, image_file_name in enumerate(jpg_list):
        img = cv.imread(os.path.join(dir_path, image_directory, image_file_name))
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR) # TODO find out which ones are needed
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
        size_ratio = [11.375, 14.5]

        # TODO change these:
        # width = (largest_box['right'] + largest_box['left']) // 2
        # height = (largest_box['top'] + largest_box['bottom']) // 2
        # print(width, height)
        if height / width > 14.5 / 11.375:
            # too tall
            height = 14.5 / 11.375 * width
        else:
            width = 11.375 * height / 14.5




        # # crop_img = img[largest_crop['top']:largest_crop['bottom'], largest_crop['left']:largest_crop['right']]
        # # left_crop_img = crop_img[:, :crop_img.shape[1]//2]
        # img = cv.rectangle(img, (largest_crop['left'], largest_crop['top']), (largest_crop['right'], largest_crop['bottom']), (255, 255, 0), 3)
        # img = cv.line(img, ((largest_crop['left'] + largest_crop['right'])//2, 0), ((largest_crop['left'] + largest_crop['right'])//2, img.shape[0]), (255, 255, 0), 3)
        # # right_crop_img = crop_img[:, crop_img.shape[1]//2:crop_img.shape[1]]
        # plt.imshow(img)
        # plt.axis('off')
        # plt.show()
        # # if i != 0:
        # #     # img_list.append(Image.fromarray(left_crop_img))
        # #     img_list.append(left_crop_img)
        # #     plt.imshow(left_crop_img)
        # #     plt.axis('off')
        # #     plt.show()
        # # if i != len(jpg_list) - 1:
        # #     # img_list.append(Image.fromarray(right_crop_img))
        # #     img_list.append(right_crop_img)
        # #     plt.imshow(right_crop_img)
        # #     plt.axis('off')
        # #     plt.show()
    # # if len(img_list) == 0:
    # #     continue
    # # pdf_filename = os.path.join(dir_path, image_directory, image_directory + '_cropped.pdf')
    # # Image.fromarray(img_list[0]).save(pdf_filename, 'PDF', resolution=100.0, save_all=True, append_images=[Image.fromarray(x) for x in img_list[1:]])
    # # print('done ' + image_directory)
