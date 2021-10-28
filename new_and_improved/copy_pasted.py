#!/usr/bin/env python

# Copyright 2017 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# lInK fOr ThE pAgE: https://github.com/googleapis/python-vision/blob/main/samples/snippets/document_text/doctext.py

"""Outlines document text given an image.

Example:
    python doctext.py resources/text_menu.jpg
"""

import argparse
import os
import shutil
from enum import Enum
import io

from google.cloud import vision
from PIL import Image, ImageDraw, ImageFont
from google.oauth2 import service_account
from reportlab.pdfgen import canvas
import timeit


font = ImageFont.truetype("Roboto-Thin.ttf", 14)
PADDING = 15


class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5


def draw_boxes(image, bounds, color):
    """Draw a border around the image using the hints in the vector list."""
    draw = ImageDraw.Draw(image)

    for bound in bounds:
        draw.polygon([
            bound.vertices[0].x, bound.vertices[0].y,
            bound.vertices[1].x, bound.vertices[1].y,
            bound.vertices[2].x, bound.vertices[2].y,
            bound.vertices[3].x, bound.vertices[3].y], None, color)
    return image


def scuffed_draw_boxes(image, bounds, color):
    draw = ImageDraw.Draw(image)

    for bound in bounds:
        draw.polygon([
            bound.vertices[0].x, bound.vertices[0].y,
            bound.vertices[1].x, bound.vertices[1].y,
            bound.vertices[2].x, bound.vertices[2].y,
            bound.vertices[3].x, bound.vertices[3].y], None, color)
    return image


def get_document_bounds(response, feature):
    """Returns document bounds given an image."""

    bounds = []

    document = response.full_text_annotation

    # Collect specified feature bounds by enumerating all document features
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        if feature == FeatureType.SYMBOL:
                            bounds.append(symbol.bounding_box)

                    if feature == FeatureType.WORD:
                        bounds.append(word.bounding_box)

                if feature == FeatureType.PARA:
                    bounds.append(paragraph.bounding_box)

            if feature == FeatureType.BLOCK:
                bounds.append(block.bounding_box)

    # The list `bounds` contains the coordinates of the bounding boxes.
    return bounds


directory_top = '/Users/joshua/NEN archives'
editions = sorted(os.listdir('/Users/joshua/NEN archives'))[4:-6]

editions = editions[9:] # temporary

for edition in editions:
    start = timeit.default_timer()
    print(edition)
    edition_path = os.path.join(directory_top, edition)
    # directory = '/Users/joshua/PycharmProjects/NEN_archives/1980_06 June'
    directory = edition_path
    imgs = [os.path.join(directory, x) for x in sorted(os.listdir(directory))[1:] if x.lower().endswith(('.jpg', '.jpeg'))]
    img_list = []
    all_bounds = []
    for filein in imgs:
        with io.open(filein, 'rb') as image_file:
            content = image_file.read()

        image = vision.Image(content=content)

        client = vision.ImageAnnotatorClient(
            credentials=service_account.Credentials.from_service_account_file("creds.json"))
        response = client.document_text_detection(image=image)

        image = Image.open(filein)
        # bounds = get_document_bounds(response, FeatureType.BLOCK)
        # draw_boxes(image, bounds, 'blue')
        bounds = get_document_bounds(response, FeatureType.PARA)
        text_bounds = {'left': 10000, 'right': 0, 'top': 10000, 'bottom': 0}

        for bound in bounds:
            left = max(bound.vertices[0].x, bound.vertices[3].x)
            right = min(bound.vertices[1].x, bound.vertices[2].x)
            bot = max(bound.vertices[2].y, bound.vertices[3].y)
            top = min(bound.vertices[0].y, bound.vertices[1].y)

            if left < text_bounds['left']:
                text_bounds['left'] = left
            if right > text_bounds['right']:
                text_bounds['right'] = right
            if bot > text_bounds['bottom']:
                text_bounds['bottom'] = bot
            if top < text_bounds['top']:
                text_bounds['top'] = top

        text_bounds['left'] -= PADDING
        text_bounds['right'] += PADDING
        text_bounds['top'] -= PADDING
        text_bounds['bottom'] += PADDING
        # draw_boxes(image, bounds, 'blue')

        # draw = ImageDraw.Draw(image)
        # draw.polygon([
        #     text_bounds['left'], text_bounds['top'],
        #     text_bounds['right'], text_bounds['top'],
        #     text_bounds['right'], text_bounds['bottom'],
        #     text_bounds['left'], text_bounds['bottom']], None, 'red')
        # middle = (text_bounds['right'] + text_bounds['left']) // 2
        # draw.polygon([
        #     middle, text_bounds['top'],
        #     middle, text_bounds['bottom']], None, 'red')
        fileout = os.path.join('/Users/joshua/PycharmProjects/NEN_archives/new_and_improved/temp', filein.split('/')[-1].strip('.jpg') + '_crop.jpg')
        image.save(fileout)
        # img_list.append(fileout)
        all_bounds.append(text_bounds)

    # split pages into left and right
    max_bounds = {'top': min([x['top'] for x in all_bounds]), 'bot': max([x['bottom'] for x in all_bounds]), 'left': min([x['left'] for x in all_bounds]), 'right': max([x['right'] for x in all_bounds])}

    directory = '/Users/joshua/PycharmProjects/NEN_archives/new_and_improved/temp'
    pages = [os.path.join(directory, x) for x in sorted(os.listdir(directory)) if x.lower().endswith(('.jpg', '.jpeg'))]
    middle = (max_bounds['left'] + max_bounds['right']) // 2
    for n, page in enumerate(pages):
        img_file = os.path.join(directory, page)
        image = Image.open(img_file)
        # if n == 0 :
        #     image.crop((middle, max_bounds['top'], max_bounds['right'], max_bounds['bottom']))
        # elif n == len(page) - 1:
        #     image.crop((max_bounds['left'], max_bounds['top'], middle, max_bounds['bottom']))
        # else:
        # draw = ImageDraw.Draw(image)
        # draw.polygon((middle, max_bounds['top'],
        #               max_bounds['right'], max_bounds['top'],
        #               max_bounds['right'], max_bounds['bot'],
        #               middle, max_bounds['bot']), None, 'blue')
        # draw.polygon((max_bounds['left'], max_bounds['top'],
        #               middle, max_bounds['top'],
        #               middle, max_bounds['bot'],
        #               max_bounds['left'], max_bounds['bot']), None, 'blue')
        # image.save(img_file.split('.')[0] + '_edit.jpg')
        # img_list.append(img_file.split('.')[0] + '_edit.jpg')
        # continue
        if n != 0:
            image_left = image.crop((max_bounds['left'], max_bounds['top'], middle, max_bounds['bot']))
            image_left.save(img_file.split('.')[0]+'_left.jpg')
            img_list.append(img_file.split('.')[0] + '_left.jpg')
        if n != len(pages) - 1:
            image_right = image.crop((middle, max_bounds['top'], max_bounds['right'], max_bounds['bot']))
            image_right.save(img_file.split('.')[0]+'_right.jpg')
            img_list.append(img_file.split('.')[0]+'_right.jpg')


    edition_name = edition_path.split('/')[-1]
    canv = canvas.Canvas(os.path.join(edition_path, edition_name + '_croppedv3.pdf'))

    for image_path in img_list:
        canv.setPageSize(((max_bounds['right'] - max_bounds['left']) / 2, (max_bounds['bot']) - (max_bounds['top']))) # padding can be moved here
        canv.drawImage(image_path, 0, 0)
        canv.showPage()

    canv.save()


    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

    stop = timeit.default_timer()
    print('Time: ', stop - start)
