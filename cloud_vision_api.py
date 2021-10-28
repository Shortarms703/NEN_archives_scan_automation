import os
from google.cloud import vision
from google.cloud.vision_v1.types import text_annotation
from google.oauth2 import service_account
from reportlab.pdfgen import canvas
import argparse
from enum import Enum
import io
from google.cloud import vision
from PIL import Image, ImageDraw


credentials = service_account.Credentials.from_service_account_file("creds.json")


client = vision.ImageAnnotatorClient(credentials=credentials)

# image_path = '/Users/joshua/Desktop/NEN archives/1983_04 April/20200623_0029.jpg'
# for directory_name in ['1980_11 November', '1981_02 February', '1981_06 June', '1981_10 October', '1981_12 December', '1982_02 February', '1982_04 April']:


def main():
    for directory_name in ['1980_06 June']:
        # directory_name = '1982_06 June'
        dir_path = os.path.join('/Users/joshua/Desktop/NEN archives', directory_name)
        jpg_list = sorted([x for x in os.listdir(dir_path) if x.endswith('.jpg')])

        if len(jpg_list) > 16:
            print('jpg list has len of ' + str(len(jpg_list)) + ' and has been skipped') # TODO fix this ty
            continue

        batch_request = []
        for each in jpg_list:
            image_path = os.path.join(dir_path, each)
            with open(image_path, 'rb') as image:
                content = image.read()
                request = {'image': {'content': content},
                           'features': [{'type_': vision.Feature.Type.DOCUMENT_TEXT_DETECTION}]}
                batch_request.append(request)


        response = client.batch_annotate_images(requests=batch_request)
        print('Obtained api response for ' + directory_name)


        # --------------------
        if 1 == 2:
            canv = canvas.Canvas(os.path.join(dir_path, directory_name + "+TEXT.pdf"))
            for each, img_file_name in zip(response.responses, jpg_list):
                # print(img_file_name)
                img_path = os.path.join(dir_path, img_file_name)

                canv.setPageSize((3008, 2000))
                canv.setFillColor('black', alpha=1)
                canv.drawImage(img_path, 0, 0)

                canv.setFillColor('green', alpha=0)
                font_size = 18
                canv.setFont('Times-Roman', font_size)

                document = each.full_text_annotation
                for page in document.pages:
                    for block in page.blocks:
                        for paragraph in block.paragraphs:
                            for i, word in enumerate(paragraph.words):
                                text = ''
                                for symbol in word.symbols:
                                    if symbol.text not in [',', '.']:
                                        text += symbol.text
                                first_char_in_next_word = paragraph.words[i + [1 if i + 1 < len(paragraph.words) else 0][0]].symbols[0].text
                                if first_char_in_next_word in [',', '.']:
                                    text += first_char_in_next_word
                                # font_size = abs(int(word.bounding_box.vertices[0].y - word.bounding_box.vertices[3].y))
                                # canv.setFont('Times-Roman', font_size)
                                canv.drawString(word.bounding_box.vertices[3].x, 2000 - word.bounding_box.vertices[3].y, text)
                # canvas.rotate(180)
                canv.showPage()

            canv.save()
            print('saved searchable pdf for ' + directory_name)
#     # --------------------
# quit()


class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5


# def main():
#     image_path = '/Users/joshua/Desktop/NEN archives/1983_04 April/20200623_0030.jpg'
#     bounds = get_document_bounds(image_path, FeatureType.BLOCK)
#     image = Image.open(image_path)
#     padded_margins, largest_bounds, middle, precise_middle = find_margins(image, bounds, padding=35)
#     draw_margins(image, padded_margins, 'red')
#     draw_margins(image, largest_bounds, 'blue')
#     draw_margins(image, middle, 'blue')
#     draw_margins(image, precise_middle, 'red')
#     # draw_boxes(image, bounds, 'red')
#
#     image.show()


def find_margins(image, bounds, padding):
    class LargestBounds:
        def __init__(self, left, right, top, bottom):
            self.left = left
            self.right = right
            self.top = top
            self.bottom = bottom
            self.middle = None
            self.middle_left = 0
            self.middle_right = float('inf')

        def update_left(self, left):
            if left < self.left:
                self.left = left

        def update_right(self, right):
            if right > self.right:
                self.right = right

        def update_top(self, top):
            if top < self.top:
                self.top = top

        def update_bottom(self, bottom):
            if bottom > self.bottom:
                self.bottom = bottom

        # def apply_aspect_ratio(self, width=11.375 * 2, height=14.5):
        #     current_width = abs(self.right - self.left)
        #     current_height = abs(self.top - self.bottom)
        #     print(self.left, self.top, self.right, self.bottom)
        #     # print
        #     if current_width / current_height < width / height:
        #         # too tall
        #         # not wide enough
        #         new_width = width * current_height / height
        #         width_change = (new_width - current_width) // 2
        #         self.top -= width_change
        #         self.bottom += width_change
        #     else:
        #         new_height = current_width * height / width
        #         height_change = (new_height - current_height) // 2
        #         self.left -= height_change
        #         self.right += height_change
        #     print(self.left - self.right, self.top - self.bottom)
        def calc_middle(self):
            self.middle = (self.left + self.right) // 2

        def calc_precise_middle(self, point_x):
            if self.middle_left < point_x < self.middle:
                self.middle_left = point_x
            if self.middle < point_x < self.middle_right:
                self.middle_right = point_x

    margin_bounds = LargestBounds(bounds[0].vertices[0].x, bounds[0].vertices[0].y, bounds[0].vertices[2].x, bounds[0].vertices[2].y)
    for bound in bounds:
        margin_bounds.update_left(bound.vertices[0].x)
        margin_bounds.update_top(bound.vertices[0].y)
        margin_bounds.update_right(bound.vertices[1].x)
        margin_bounds.update_top(bound.vertices[1].y)
        margin_bounds.update_right(bound.vertices[2].x)
        margin_bounds.update_bottom(bound.vertices[2].y)
        margin_bounds.update_left(bound.vertices[3].x)
        margin_bounds.update_bottom(bound.vertices[3].y)
    largest_bounds = [margin_bounds.left, margin_bounds.top, margin_bounds.right, margin_bounds.top, margin_bounds.right, margin_bounds.bottom, margin_bounds.left, margin_bounds.bottom ]
    padded_bounds = [margin_bounds.left - padding, margin_bounds.top - padding, margin_bounds.right + padding, margin_bounds.top - padding, margin_bounds.right + padding, margin_bounds.bottom + padding, margin_bounds.left - padding, margin_bounds.bottom + padding]
    margin_bounds.calc_middle()
    middle = [margin_bounds.middle, margin_bounds.top, margin_bounds.middle, margin_bounds.bottom]
    for bound in bounds:
        for i in [0, 1, 2, 3]:
            margin_bounds.calc_precise_middle(bound.vertices[i].x)
    precise_middle = (margin_bounds.middle_right + margin_bounds.middle_left) / 2
    precise_middle_line = [precise_middle, margin_bounds.top - padding, precise_middle, margin_bounds.bottom + padding]
    return padded_bounds, largest_bounds, middle, precise_middle_line


def draw_margins(image, margin_bounds, color):
    draw = ImageDraw.Draw(image)
    draw.polygon(margin_bounds, None, color)
    return image


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


def get_document_bounds(image_file, feature):
    """Returns document bounds given an image."""
    client = vision.ImageAnnotatorClient(credentials=credentials)

    bounds = []

    with io.open(image_file, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    document = response.full_text_annotation

    # Collect specified feature bounds by enumerating all document features
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    for symbol in word.symbols:
                        if (feature == FeatureType.SYMBOL):
                            bounds.append(symbol.bounding_box)

                    if (feature == FeatureType.WORD):
                        bounds.append(word.bounding_box)

                if (feature == FeatureType.PARA):
                    bounds.append(paragraph.bounding_box)

            if (feature == FeatureType.BLOCK):
                bounds.append(block.bounding_box)

    # The list `bounds` contains the coordinates of the bounding boxes.
    return bounds


def render_doc_text(filein, fileout):
    image = Image.open(filein)
    bounds = get_document_bounds(filein, FeatureType.BLOCK)
    draw_boxes(image, bounds, 'blue')
    bounds = get_document_bounds(filein, FeatureType.PARA)
    draw_boxes(image, bounds, 'red')
    bounds = get_document_bounds(filein, FeatureType.WORD)
    # draw_boxes(image, bounds, 'yellow')

    if fileout != 0:
        image.save(fileout)
    else:
        image.show()


if __name__ == '__main__':
    main()
    # parser = argparse.ArgumentParser()
    # parser.add_argument('detect_file', help='The image for text detection.')
    # parser.add_argument('-out_file', help='Optional output file', default=0)
    # args = parser.parse_args()
    #
    # render_doc_text('/Users/joshua/Desktop/NEN archives/1983_04 April/20200623_0029.jpg', 'boxes.jpg')
