import random
from math import gcd
from PIL import Image
from art_helper_modules import random_lim_factor, random_color_tuple, generate_gradient


def apply_splotches(im, num=None, pool=8, classic=False, square=False, max_percent=0.1):
    w, h = im.size
    count = random.randint(0, 100) if num is None else num

    grid_pool = []
    if not classic:
        for i in range(pool):
            grid_pool.append(Image.new('RGB', im.size, random_color_tuple()))
    else:
        grid_pool.append(Image.new('RGB', im.size, (255,   0,   0)))
        grid_pool.append(Image.new('RGB', im.size, (255, 255,   0)))
        grid_pool.append(Image.new('RGB', im.size, (255, 255, 255)))
        grid_pool.append(Image.new('RGB', im.size, (0,   255, 255)))
        grid_pool.append(Image.new('RGB', im.size, (0,     0, 255)))
        grid_pool.append(Image.new('RGB', im.size, (255,   0, 255)))
        grid_pool.append(Image.new('RGB', im.size, (0,   255,   0)))
        grid_pool.append(Image.new('RGB', im.size, (0,     0,   0)))

    for i in range(count):
        s_w = random.randint(0, w*max_percent)
        s_h = random.randint(0, h*max_percent) if not square else min(s_w, h)
        s_x = random.randint(0, w - s_w)
        s_y = random.randint(0, h - s_h)
        block = (s_x, s_y, s_x + s_w, s_y + s_h)
        im.paste(random.choice(grid_pool).crop(block), block)

    return im


def populate(im, collage_set, num=None, square=False, max_percent=0.5):
    w, h = im.size
    count = random.randint(0, 10000) if num is None else num

    for i in range(count):
        piece = random.choice(collage_set)
        s_w = min(piece.size[0], random.randint(0, int(w*max_percent)))
        s_h = min(piece.size[1], random.randint(0, int(h*max_percent)) if not square else min(s_w, h))
        s_x = random.randint(0, w - s_w)
        s_y = random.randint(0, h - s_h)
        block = (s_x, s_y, s_x + s_w, s_y + s_h)
        im.paste(piece.crop((0, 0, s_w, s_h)), block)

    return im


def center_crop(im, width, height):
    w = min(im.size[0], width) if width > 0 else 1
    h = min(im.size[1], height) if height > 0 else 1
    outim = Image.new('RGBA', (w, h))
    W = (im.size[0] - w) // 2
    H = (im.size[1] - h) // 2
    outim.paste(im.crop((W, H, W + w, H + h)))
    return outim


def bar_h_translate(im, mag, part_size=1, limit_low=0.0, limit_high=1.0):
    w, h = im.size
    BLS = gcd(w, part_size)
    x_blocks = w // BLS
    colmap = [(a * BLS, int(h * limit_low), (a + 1) * BLS, int(h * limit_high)) for a in range(x_blocks)]
    scolmap = []
    for i in range(len(colmap)):
        scolmap.append(colmap[(i + mag + len(colmap)) % len(colmap)])
    outim = Image.new(im.mode, im.size)
    outim.paste(im.crop((0, 0, w, h)), (0, 0, w, h))
    for column, dest in zip(colmap, scolmap):
        outim.paste(im.crop(column), dest)
    return outim


def bar_v_translate(im, mag, part_size=1, limit_low=0.0, limit_high=1.0):
    w, h = im.size
    BLS = gcd(h, part_size)
    y_blocks = h // BLS
    rowmap = [(int(w * limit_low), b * BLS, int(w * limit_high), (b + 1) * BLS) for b in range(y_blocks)]
    srowmap = []
    for i in range(len(rowmap)):
        srowmap.append(rowmap[(i + mag + len(rowmap)) % len(rowmap)])
    outim = Image.new(im.mode, im.size)
    outim.paste(im.crop((0, 0, w, h)), (0, 0, w, h))
    for row, dest in zip(rowmap, srowmap):
        outim.paste(im.crop(row), dest)
    return outim


def bar_gradient(im, decr=None, part_size=8, width=1.0, height=1.0):
    w, h = im.size
    BLS = gcd(w, part_size)
    x_blocks = w // BLS
    colmap = [(a * BLS, int(h * (1.0 - height)), (a + 1) * BLS, int(h * height)) for a in range(x_blocks)]
    region_size = (colmap[0][2], colmap[0][3])
    shaded_regions = []
    for column in colmap:
        shaded_regions.append(Image.new(im.mode, region_size))
        shaded_regions[-1].paste(im.crop(column), (0, 0, region_size[0], region_size[1]))
    if decr is None:
        shaded_regions = generate_gradient(shaded_regions, width=width, linear_dim=False)
    else:
        shaded_regions = generate_gradient(shaded_regions, decr=decr, width=width, linear_dim=True)
    outim = Image.new(im.mode, im.size)
    outim.paste(im.crop((0, 0, w, h)), (0, 0, w, h))
    for i in range(len(colmap)):
        outim.paste(shaded_regions[i].crop((0, 0, region_size[0], region_size[1])), colmap[i])
    return outim


def box_translate(im, h, v, region=None):
    outim = bar_v_translate(bar_h_translate(im, h), v)
    if region is None:
        return outim
    else:
        target_im = im
        target_im.paste(outim.crop(region), region)
        return target_im


def box_shuffle(im, seed=None):
    w, h = im.size
    BLS = random_lim_factor(gcd(w, h), seed=seed)
    x_blocks = w // BLS
    y_blocks = h // BLS
    bkmap = [(a * BLS, b * BLS, (a + 1) * BLS, (b + 1) * BLS) for a in range(x_blocks) for b in range(y_blocks)]
    sbkmap = list(bkmap)
    random.shuffle(sbkmap)
    outim = Image.new(im.mode, im.size)
    for block, dest in zip(bkmap, sbkmap):
        outim.paste(im.crop(block), dest)
    return outim


def twist(im, num=None, max_percent=0.3):
    w, h = im.size
    count = random.randint(0, 100) if num is None else num

    for i in range(count):
        s = random.randint(0, min(w, h)*max_percent)
        x = random.randint(0, w - s)
        y = random.randint(0, h - s)
        block = (x, y, x + s, y + s)
        im.paste(im.crop(block).rotate(random.choice([90, 180, 270])), block)
    return im
