import os, sys, getopt
import base64
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

temp_thumb_file = 'thumbnail_tmp.jpg'
stand_pars = ['FN', 'TITLE', 'ORG', 'ADR', 'TEL', 'EMAIL', 'URL', 'PHOTO']
max_param_length = 24
X = 154
Y = 20
OFF = 20
small_size = (146, 196)
thumb_size = (350, 200)
pic_offset = (2, 2)
text_color = (0, 0, 0)
background_color = (255, 255, 255, 255)
font_size = 10
font_file = "Roboto-Regular.ttf"   # can be used instead of default font


def load_vcards(lines):  # form list of lines for each vcard, begin line excluded
    all_cards = list()
    card_lines = list()
    inside_card = False

    for line in lines:
        if ":" in line:  # parameter line 
            param, value = line.strip().split(':')
            if "BEGIN" in param:
                if not inside_card:
                    inside_card = True
                else:
                    print("invalid vcard format: END line missing")
                    return None
            elif "END" in param:
                if inside_card:
                    card_lines.append(line)
                    all_cards.append(card_lines)
                    card_lines = list()
                    inside_card = False
                else:
                    print("invalid vcard format: END line before BEGIN line")
                    return None
            else:
                card_lines.append(line)
        elif inside_card:
            card_lines.append(line)
        else:
            continue

    return all_cards


def decode_data(index, lines, pars, value):
    photo_data = value

    for line in lines[index + 1:]:
        if "END:VCARD" in line:
            break
        else:
            photo_data += line.strip()

    # we ignore parameters of encoding in pars list
    imgdata = base64.b64decode(photo_data)
    with open(temp_thumb_file, 'wb') as f:
        f.write(imgdata)

    return temp_thumb_file


def get_photo(card_lines):
    photo_file = ''

    for index, line in enumerate(card_lines):
        if ":" in line:  # parameter line 
            param, value = line.strip().split(':')
            p, *p_var = param.split(';')
            if p == 'PHOTO':
                if 'http' in value.lower():
                    # download photo from inet
                    break
                else:
                    # data is in the list, so we have to decode them
                    photo_file = decode_data(index, card_lines, p_var, value)
                    break

    return photo_file


def create_thumbnail(params, card_data):
    background = Image.new('RGBA', thumb_size, background_color)
    draw = ImageDraw.Draw(background)
    #font = ImageFont.truetype(font_file, font_size)
    font = ImageFont.load_default()

    if ('PHOTO' in params) and (card_data['PHOTO'] != ''):
        img = Image.open(card_data['PHOTO'], 'r')
        small_img = img.resize(small_size)
        background.paste(small_img, pic_offset)

    offset = Y
    for par in params:
        if par != 'PHOTO':
            draw.text((X, offset), par + ': ' + card_data[par], text_color, font=font)
            offset += OFF

    background.save((card_data['FN'].lower() + '.png').replace(' ', '_'))


def card_to_thumbnail(card_lines, params=stand_pars):
    card_data = dict()

    if 'PHOTO' in params:  # process PHOTO parameter if present
        card_data['PHOTO'] = result = get_photo(card_lines)
        if result == '':
            print("unable to load PHOTO data, parameter ignored")

    for line in card_lines:  # process others parameters
        if ":" in line:  # parameter line 
            param, value = line.strip().split(':')
            p1, *_ = param.split(';')
            if (p1 in params) and (p1 not in card_data):
                temp = " ".join(value.split(';')).strip()
                if len(temp) > max_param_length :    # cut long string
                    temp = temp[:max_param_length]
                card_data[p1] = temp

    create_thumbnail(params, card_data)


def main(argv):

    vcard_file = argv[0]
    with open(vcard_file, encoding="utf8") as f:
        data = f.readlines()

    dirname= vcard_file.lower().split('.')[0] + ".thumbs"
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    os.chdir(dirname)

    list_of_cards = load_vcards(data)
    if list_of_cards:
        for card in list_of_cards:
            card_to_thumbnail(card)
        print("loaded {} vcards".format(len(list_of_cards)))

        os.remove(temp_thumb_file)  # remove temporal jpg file


if __name__ == '__main__':
    main(sys.argv[1:])

