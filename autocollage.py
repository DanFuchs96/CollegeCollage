from PIL import Image
import shutil
import time
import glob
import re
import os


def full_sys_collage(working_dir='C:/Users'):
    collage_set = []
    for root, dirs, files in os.walk(working_dir):
        for root_path in root.split('\n'):
            images = (glob.glob(root_path + '\\*.png'))
            images.extend(glob.glob(root_path + '\\*.jpg'))
            for image in images:
                image_path = image.replace('\\', '/')
                if not re.match('.*e Emblem H.*', image_path) and not re.match('.*Microsoft\.Windows.*', image_path):
                    collage_set.append(Image.open(image_path))
    return collage_set


def shred(seed=0):
    files = glob.glob('components/shredder/*.*')
    while files:
        file = files.pop()
        newname = str(hash(str(file) + str(seed))) + str(file[-4:])
        shutil.move(file, 'components/shreddings/' + newname[3:])
    return


def shredder(duration=1000):
    timer = duration
    while timer > 0:
        time.sleep(1)
        timer -= 1
        shred(timer)
    return


def shrink(ratio=0.25):
    files = glob.glob('components/shredder/*.*')
    while files:
        file = files.pop().replace('\\', '/')
        outim = Image.open(file)
        w, h = outim.size
        outim = outim.resize((int(w * ratio), int(h * ratio)), Image.ANTIALIAS)
        outim.save(file[:-4] + '_shrunken' + file[-4:], optimize=True, quality=75)
        shutil.move(file[:-4] + '_shrunken' + file[-4:], 'components/shreddings/')
    return


def serialize(image_set):
    height = image_set[0].size[1]
    width = 0
    h_p = 0

    for image in image_set:
        width += image.size[0]
        height = min(height, image.size[1])
    outim = Image.new(image_set[0].mode, (width, height))

    for image in image_set:
        s_block = (0, 0, image.size[0], height)
        t_block = (h_p, 0, h_p + image.size[0], height)
        h_p += image.size[0]
        outim.paste(image.crop(s_block), t_block)
    return outim


def timeline(image_set):
    width, height = image_set[0].size
    count = len(image_set)
    part_width = width // count

    for image in image_set:
        if image.size[0] != width or image.size[1] != height:
            print("Could not create timeline; returned image has inconsistent dimensions.")
            return image
    outim = Image.new(image_set[0].mode, (part_width * count, height))

    h_p = 0
    for image in image_set:
        block = (h_p, 0, h_p + part_width, height)
        outim.paste(image.crop(block), block)
        h_p += part_width

    return outim
