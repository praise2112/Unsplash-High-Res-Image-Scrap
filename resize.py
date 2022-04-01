from PIL import ImageOps, Image
import os
from tqdm import tqdm


DIR = "D:\\unsplash_5371_full_size"
RESIZED_IMG_DIR = "D:\\unsplash_5k_1536x1152_resized"
NEW_IMAGE_DIMENSIONS = (1536, 1152)


def resize():
  os.makedirs(RESIZED_IMG_DIR, exist_ok=True)
  for item in tqdm(os.listdir(DIR)):
    file_path = os.path.join(DIR, item)
    if os.path.isfile(file_path):
      im = Image.open(file_path)
      im = ImageOps.contain(im, NEW_IMAGE_DIMENSIONS)
      im.save(os.path.join(RESIZED_IMG_DIR, item), quality=90)


if __name__ == '__main__':
  resize()
