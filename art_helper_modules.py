import random
from math import gcd
from functools import reduce
from PIL import Image, ImageOps


def random_lim_factor(n, seed=None, sort=True):
    factors = list(reduce(list.__add__, ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))
    for factor in factors:
        if factor < 7 and len(factors) > 1:
            factors.remove(factor)
    if seed is None:
        return random.choice(factors)
    else:
        if sort:
            factors = list(sorted(factors, reverse=True))
        index = seed % len(factors)
        return factors[index]


def random_sor_factor(n, seed=None):
    factors = list(reduce(list.__add__, ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0)))
    factors = list(sorted(factors))
    if seed is None:
        return random.choice(factors)
    else:
        index = seed % len(factors)
        return factors[index]


def random_color():
    return '#' + "%06x" % random.randint(0, 0xFFFFFF)


def random_color_tuple():
    color_tuple = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    return color_tuple


def tint_image(src, color="#FFFFFF"):
    src.load()
    r, g, b, alpha = src.split()
    gray = ImageOps.grayscale(src)
    result = ImageOps.colorize(gray, (0, 0, 0, 0), color)
    result.putalpha(alpha)
    return result


def gen_grid(w=1000, h=1000, pool=8, seed=None, classic=False, checker=False, checker_wbt=((255, 255, 255), (0, 0, 0))):
    im = Image.new('RGBA', (w, h))
    BLS = random_lim_factor(gcd(w, h), seed=seed)
    x_blocks = w // BLS
    y_blocks = h // BLS
    bkmap = [(a * BLS, b * BLS, (a + 1) * BLS, (b + 1) * BLS) for a in range(x_blocks) for b in range(y_blocks)]

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

    if not checker:
        for block in bkmap:
            im.paste(random.choice(grid_pool).crop(block), block)
    else:
        white = Image.new('RGB', im.size, checker_wbt[0])
        black = Image.new('RGB', im.size, checker_wbt[1])
        counter = 0
        wrap_count = len(bkmap) ** 0.5
        if wrap_count % 2:
            for block in bkmap:
                if counter % 2:
                    im.paste(black.crop(block), block)
                else:
                    im.paste(white.crop(block), block)
                counter = counter + 1
        else:
            for block in bkmap:
                if (counter // wrap_count) % 2:
                    if counter % 2:
                        im.paste(black.crop(block), block)
                    else:
                        im.paste(white.crop(block), block)
                else:
                    if counter % 2:
                        im.paste(white.crop(block), block)
                    else:
                        im.paste(black.crop(block), block)
                counter = counter + 1
    return im


def generate_spectrum(filename, smooth=True):
    im = Image.open(filename)
    colors = ['#222222', '#FF0000', '#FFFF00', '#DDDDDD',
              '#00FFFF', '#0000FF', '#00FF00', '#FF00FF']
    for color in colors:
        outim = tint_image(im, color)
        outim.save(filename[:-4] + color[1:] + '.png')
    return


def generate_tints(filename, count=100):
    im = Image.open(filename)
    for i in range(count):
        color = random_color()
        outim = tint_image(im, color)
        outim.save(filename[:-4] + color[1:] + '.png')
    return


def generate_grad_img(filename, decr=(7, 7, 7), count=33, intensity_base=0.5, intensity_focus=2.0, linear_dim=False):
    im = Image.open(filename)
    color = gen_hex_gradient('#FFFFFF', decr, count, linear_dim=linear_dim)
    for i in range(count):
        alpha = ((intensity_base - (abs(i - count/2)/count))*(1/intensity_base))**intensity_focus
        colim = tint_image(im, color[i])
        outim = Image.blend(im, colim, alpha=alpha)
        outim.save(filename[:-4] + pad_digit(i+1, width=3) + '.png')
    return


def generate_gradient(fragments, width=1.0, decr=(7, 7, 7), intensity_base=0.5, intensity_focus=2.0, linear_dim=True):
    count = int(len(fragments) * width)
    offset = 0 if count == len(fragments) else random.randrange(0, len(fragments) - count)
    color = gen_hex_gradient('#FFFFFF', decr, count, linear_dim=linear_dim)

    for i in range(count):
        fragment = fragments[i + offset]
        alpha = ((intensity_base - (abs(i - count/2)/count))*(1/intensity_base))**intensity_focus
        colim = tint_image(fragment, color[i])
        fragments[i + offset] = Image.blend(fragment, colim, alpha=alpha)
    return fragments


def gen_hex_gradient(peak, diminisher, steps, linear=False, linear_dim=True, n_linear_r=50):
    gradient = []
    step_value = hex_to_list(peak)
    step_count = steps//2
    if linear:
        step_count = steps
    for i in range(step_count):
        gradient.append(list_to_hex(step_value))
        for j in range(len(diminisher)):
            step_value[j] = step_value[j] - (diminisher[j] if linear_dim else random.randrange(-n_linear_r, n_linear_r))
            if step_value[j] < 0:
                step_value[j] = 0
            elif step_value[j] > 255:
                step_value[j] = 255
    if linear:
        return gradient[::-1]
    if not steps % 2:
        gradient.extend(gradient[::-1])
    else:
        gradient.append(gradient[-1])
        gradient.extend(gradient[:-1][::-1])
    return gradient


def list_to_hex(x):
    hex_string = hex(x[0]*256*256 + x[1]*256 + x[2])[2:].upper()
    while len(hex_string) < 6:
        hex_string = '0' + hex_string
    return '#' + hex_string


def hex_to_list(x):
    return [int(x[1:3], 16), int(x[3:5], 16), int(x[5:7], 16)]


def pad_digit(x, width=8):
    out_name = ''
    leading_zeros = width - count_digits(x)
    for i in range(leading_zeros):
        out_name += '0'
    out_name += str(x)
    return out_name


def count_digits(value, base=10):
    num_digits = 0
    while value >= base ** num_digits:
        num_digits += 1
        if num_digits > 1000:
            break
    return num_digits
