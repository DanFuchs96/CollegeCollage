# A strange program written by Daniel Fuchs.
# This file gives an example of how to use the provided modules to randomly generate images.
import imageio
from autocollage import *
from art_operations import *
from art_helper_modules import *


def main(seed='CollageCollege'):
    random.seed(seed)  # Consider randomizing the seed for non-deterministic output.

    # General Setup
    output_type = 'image'
    base_samples = 15000
    image_width = 7680*2
    image_height = 4320*2
    collage_set = build_collage()

    # Video Settings
    frame_count = 50
    frame_delay = 1/20

    # Create Initial Frame
    back_plate = gen_grid(image_width + (image_width//4), image_height + (image_height//4), seed=1)
    source_image = center_crop(populate(back_plate, collage_set, num=base_samples, max_percent=0.05, square=True),
                               image_width, image_height)
    output_filename = 'components/' + seed.replace(' ', '').lower()

    # Begin Execution
    if output_type == 'image':
        output_filename += '.png'
        create_image(source_image, artistic_fusilade, filename=output_filename)
    else:
        output_filename += '.gif'
        create_video(source_image, artistic_fusilade, frames=frame_count, speed=frame_delay, filename=output_filename)


# This function serves as an example of how to use this program. Realistically, you can just combine operations in
# whatever way you deem fit; when creating an image, you likely want an iterative process that applies a variety of
# operations, possibly in a random manner; the below function is an example of this. If you're creating a video, you
# probably want to use simpler functions. Be wary of file-size when outputting a video.
def artistic_fusilade(im, args=None):
    w, h = im.size
    outim = im
    outim = box_shuffle(outim, seed=0)
    outim = twist(outim, num=50, max_percent=0.7)
    iterations = random.randrange(100, 1000)
    for i in range(iterations):
        op_code = random.randrange(0, 5)
        if op_code == 0:
            if iterations - i > 100:
                continue
            decrv = [random.randrange(0, 2), random.randrange(0, 4), random.randrange(0, 8)]
            random.shuffle(decrv)
            outim = bar_gradient(outim, width=0.25, decr=(decrv[0], decrv[1], decrv[2]), part_size=20)
        elif op_code == 1:
            b_start = random.randrange(0, 99)
            b_end = random.randrange(b_start, 100)
            outim = bar_v_translate(outim, random.randrange(10, 1000), limit_low=b_start/100, limit_high=b_end/100)
        elif op_code == 2:
            b_start = random.randrange(0, 99)
            b_end = random.randrange(b_start, 100)
            outim = bar_h_translate(outim, random.randrange(10, 1000), limit_low=b_start/100, limit_high=b_end/100)
        elif op_code == 3:
            b_x = random.randrange(w//4, w)
            b_y = random.randrange(h//4, h)
            b_size = random.randrange(0, min(w - b_x, h - b_y))
            outim = box_translate(outim, random.randrange(10, 1000), random.randrange(10, 1000),
                                  (b_x, b_y, b_x + b_size, b_y + b_size))
        elif op_code == 4:
            None
    return outim


# Creates a single image. Operation should be a function expecting an Image, and should also return one.
def create_image(im, operation, compress=True, filename='out_art.png', quality=90):
    outim = operation(im)
    if compress:
        w, h = outim.size
        outim = outim.resize((w//2, h//2), Image.ANTIALIAS)
        outim.save(filename, optimize=True, quality=quality)
    else:
        outim.save(filename)
    return outim


# Creates a video. Operation should be a function expecting an Image, and should also return one. Currently configured
# to create a gif.
def create_video(im, operation, frames=100, filename='out_vid.gif', speed=1/50, compress=False, quality=90):
    frame_count = 0
    with imageio.get_writer(filename, mode='I', duration=speed) as video_head:
        outim = im.copy()
        for i in range(frames):
            outim = operation(outim, frame_count).convert('RGB')
            if not compress:
                outim.save('out_last_frame.png')
            else:
                outim.save(filename, optimize=True, quality=quality)
            video_head.append_data(imageio.imread('out_last_frame.png'))
            frame_count += 1
    return outim


# Create a set of images to draw from in generating the collage.
def build_collage(directory='components/art/'):
    collage_set = []
    image_paths = glob.glob(directory + '*.*g')
    for file in image_paths:
        collage_set.append(Image.open(file.replace('\\', '/')))
    return collage_set


if __name__ == '__main__':
    main()
