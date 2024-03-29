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
        return 'only one page found'
    else:
        return edge_points


def draw_margin_line(img, edge_points, thickness=3, top_bottom=False):
    if top_bottom is True:
        edge_y = [x[1] for x in edge_points]
        average = sum(edge_y) // len(edge_y)
        # img = cv.line(img, (edge_points[0][0], average), (edge_points[-1][0], average), (0, 0, 255), thickness)
    else:
        edge_x = [x[0] for x in edge_points]
        average = sum(edge_x) // len(edge_x)
        # img = cv.line(img, (average, edge_points[0][1]), (average, edge_points[-1][1]), (0, 0, 255), thickness)
    return img, average


def find_margins(path, first_image=False, last_image=False):
    img = cv.imread(path)
    shape = img.shape
    shape = {'x': shape[1], 'y': shape[0]}
    sides = {}

    side = 'left'
    edge_points = find_lr_side_margin(path, side, 0, 500, 0, shape['y'])
    if edge_points == 'only one page found':
        edge_points = find_lr_side_margin(path, side, shape['x'] // 2 - 200, shape['x'] // 2 + 300, 0, shape['y'])
        sides['single'] = 'right'
    img, average = draw_margin_line(img, edge_points)
    sides[side] = average
    if average < largest_crop['left'] and 'single' not in sides:
        largest_crop['left'] = average

    side = 'right'
    edge_points = find_lr_side_margin(path, side, shape['x'], shape['x'] - 500, 0, shape['y'])
    if edge_points == 'only one page found':
        edge_points = find_lr_side_margin(path, side, shape['x'] // 2 + 200, shape['x'] // 2 - 300, 0, shape['y'])
        sides['single'] = 'left'
    img, average = draw_margin_line(img, edge_points)
    sides[side] = average
    if average > largest_crop['right'] and 'single' not in sides:
        largest_crop['right'] = average


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

        img, average = draw_margin_line(img, edge_points, top_bottom=True)
        sides[side] = average
        if average < largest_crop['top'] and side == 'top' and 'single' not in sides:
            largest_crop[side] = average
        if average > largest_crop['bottom'] and side == 'bottom' and 'single' not in sides:
            largest_crop[side] = average

    if 'single' not in sides:
        # find middle here! or not?
        middle = (sides['right'] + sides['left']) // 2
        # img = cv.line(img, (middle, 0), (middle, shape['y']), (0, 0, 255), 3)

    # if True not in [first_image, last_image]:
    #     img = cv.rectangle(img, (largest_crop['left'], largest_crop['top']), (largest_crop['right'], largest_crop['bottom']), (255, 255, 0), 4)
    img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
    return [img]


# images = sorted(os.listdir('1980_06 June'))
dir_path = '/Users/joshua/Desktop/NEN archives'
# years = sorted(os.listdir(dir_path))[4:-6]
years = sorted(os.listdir(dir_path))[4:-6]
# images.remove('.DS_Store')
largest_crop = {'left': float('inf'), 'right': 0, 'top': float('inf'), 'bottom': 0}
for image_directory in years:
    jpg_list = sorted(os.listdir(os.path.join(dir_path, image_directory)))
    jpg_list = [x for x in jpg_list if all(['.pdf' not in x, '.DS_Store' not in x])]
    for i, image_file_name in enumerate(jpg_list):
        # print(image_file_name)
        if image_file_name.endswith('.pdf'):
            continue
        if i == 0:
            images_with_margins = find_margins(os.path.join(dir_path, image_directory, image_file_name), first_image=True)
        elif i == len(image_directory) - 1:
            images_with_margins = find_margins(os.path.join(dir_path, image_directory, image_file_name), last_image=True)
        else:
            images_with_margins = find_margins(os.path.join(dir_path, image_directory, image_file_name))
    img_list = []
    for i, image_file_name in enumerate(jpg_list):
        img = cv.imread(os.path.join(dir_path, image_directory, image_file_name))

        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
        crop_img = img[largest_crop['top']:largest_crop['bottom'], largest_crop['left']:largest_crop['right']]
        left_crop_img = crop_img[:, :crop_img.shape[1]//2]
        right_crop_img = crop_img[:, crop_img.shape[1]//2:crop_img.shape[1]]
        if i != 0:
            # img_list.append(Image.fromarray(left_crop_img))
            img_list.append(left_crop_img)
            # plt.imshow(left_crop_img)
            # plt.axis('off')
            # plt.show()
            # cv.imwrite('1980_06 June_cropped/' + 'page' + str(i + 1) + '_cropped.jpg', left_crop_img)
        if i != len(jpg_list) - 1:
            # img_list.append(Image.fromarray(right_crop_img))
            img_list.append(right_crop_img)
            # plt.imshow(right_crop_img)
            # plt.axis('off')
            # plt.show()
            # cv.imwrite('1980_06 June_cropped/' + 'page' + str(i + 1) + '_cropped.jpg', right_crop_img)
    if len(img_list) == 0:
        continue
    pdf_filename = os.path.join(dir_path, image_directory, image_directory + '_cropped.pdf')
    Image.fromarray(img_list[0]).save(pdf_filename, 'PDF', resolution=100.0, save_all=True, append_images=[Image.fromarray(x) for x in img_list[1:]])
    print('done ' + image_directory)
