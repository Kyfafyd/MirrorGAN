import argparse
import os
import imghdr
from PIL import Image


def resize_image(image, size, imgType):
    """Resize an image to the given size."""

    print imgType
    if imgType == 'png':
        r, g, b, a = image.split()
        image = Image.merge("RGB", (r, g, b))
    return image.resize(size, Image.ANTIALIAS)


def resize_images(image_dir, output_dir, size):
    """Resize the images in 'image_dir' and save into 'output_dir'."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    dirs = os.listdir(image_dir)
    for a in dirs:
        if not os.path.exists(output_dir + '/' + a):
            os.makedirs(output_dir + '/' + a)
        images = os.listdir(image_dir + '/' + a)
        num_images = len(images)
        for i, image in enumerate(images):
            imgType = imghdr.what(image_dir + '/' + a + '/' + image)
            with open(os.path.join(image_dir, a, image), 'r+b') as f:
                with Image.open(f) as img:
                    img = resize_image(img, size, imgType)
                    img.save(os.path.join(output_dir, a, image), img.format)
            if (i + 1) % 100 == 0:
                print ("[{}/{}] Resized the images and saved into '{}/{}'."
                       .format(i + 1, num_images, output_dir, a))


def main(args):
    image_dir = args.image_dir
    output_dir = args.output_dir
    image_size = [args.image_size, args.image_size]
    resize_images(image_dir, output_dir, image_size)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_dir', type=str, default='../data/health/CUB_200_2011/images',
                        help='directory for train images')
    parser.add_argument('--output_dir', type=str, default='../data/health/CUB_200_2011/resized_500/',
                        help='directory for saving resized images')
    parser.add_argument('--image_size', type=int, default=500,
                        help='size for image after processing')
    args = parser.parse_args()
    main(args)
