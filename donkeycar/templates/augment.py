import os
import json
import argparse
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import random
import numpy as np
from concurrent.futures import ThreadPoolExecutor

def load_image(image_path):
    return Image.open(image_path)

def save_image(image, path):
    image.save(path)

def augment_image(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    blurred_image = image.filter(ImageFilter.GaussianBlur(radius=2))
    
    def skew(image):
        width, height = image.size
        m = -0.5  # skew coefficient
        xshift = abs(m) * width
        new_width = width + int(round(xshift))
        skew_image = image.transform(
            (new_width, height),
            Image.AFFINE,
            (1, m, -xshift if m > 0 else 0, 0, 1, 0),
            Image.BICUBIC)
        return skew_image.crop((xshift if m > 0 else 0, 0, new_width - xshift if m > 0 else width, height))
    
    return skew(blurred_image)

def flip_image(image):
    return image.transpose(Image.FLIP_LEFT_RIGHT)

def color_jitter(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(np.random.uniform(0.8, 1.2))
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(np.random.uniform(0.8, 1.2))
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(np.random.uniform(0.8, 1.2))
    return image

def cutout(image, num_holes=1, max_hole_size=50):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    width, height = image.size
    draw = ImageDraw.Draw(image)

    for _ in range(num_holes):
        hole_width = random.randint(1, max_hole_size)
        hole_height = random.randint(1, max_hole_size)
        
        x1 = random.randint(0, width - hole_width)
        y1 = random.randint(0, height - hole_height)
        x2 = x1 + hole_width
        y2 = y1 + hole_height
        
        draw.rectangle([x1, y1, x2, y2], fill=(0, 0, 0))  # RGB black
    
    return image

def get_catalog_files(base_path):
    catalog_files = [f for f in os.listdir(base_path) if f.endswith('.catalog')]
    catalog_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    return catalog_files

def get_catalog_manifest_files(base_path):
    catalog_files = [f for f in os.listdir(base_path) if f.endswith('.catalog_manifest')]
    catalog_files.sort(key=lambda x: int(x.split('_')[1].split('.')[0]))
    return catalog_files

def update_catalog(file_path, new_data):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'a') as f:
            json_string = json.dumps(new_data)
            f.write(json_string + '\n')
        print(f"Data written to {file_path}")

    except Exception as e:
        print(f"Failed to write to {file_path}: {str(e)}")

def update_catalog_manifest(file_path, new_data):
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'a') as f:
            json_string = json.dumps(new_data)
            f.write(json_string + '\n')
        print(f"Data written to {file_path}")

    except Exception as e:
        print(f"Failed to write to {file_path}: {str(e)}")

def update_manifest_json(file_path, new_data):
    try:
        if not os.path.exists(file_path):
            print(f"No existing file at {file_path}. Creating new file.")
            with open(file_path, 'w') as f:
                f.write(json.dumps(new_data) + '\n')
            return

        with open(file_path, 'r') as f:
            lines = f.readlines()
        
        lines[-1] = json.dumps(new_data) + '\n'

        with open(file_path, 'w') as f:
            f.writelines(lines)
        
        print(f"Last line updated in {file_path}")

    except Exception as e:
        print(f"Failed to update {file_path}: {str(e)}")


def get_last_line(filename):
    last_line = None
    try:
        with open(filename, 'r') as file:
            for line in file:
                if line.strip():
                    last_line = line
    except FileNotFoundError:
        print(f"The file {filename} does not exist.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    return last_line

def process_images(data_dir, base_path, augmentations):
    catalog_files = get_catalog_files(base_path)
    catalog_manifest_files = get_catalog_manifest_files(base_path)

    with open('data//catalog_0.catalog_manifest', 'r') as file:
        catalog_manifest_0_copy = [json.loads(line) for line in file if line.strip()]
    catalog_manifest_0_copy = catalog_manifest_0_copy[0]

    last_index_file_path = f"data//{catalog_files[-1]}"
    last_index = json.loads(get_last_line(last_index_file_path))['_index']

    manifest_json_file_path = f"data//manifest.json"
    last_index_manifest_json = json.loads(get_last_line(manifest_json_file_path))
    line_lengths = []

    catalog_manifest_0_copy['start_index'] = last_index + 1
    catalog_manifest_0_copy['path'] = "augment.catalog_manifest" 

    def process_item(item, augmentations):
        center_image_path = os.path.join(data_dir, 'images', item['cam/image_array'])
        left_image_path = os.path.join(data_dir, 'images', item['cam/left_image'])
        right_image_path = os.path.join(data_dir, 'images', item['cam/right_image'])

        center_image = load_image(center_image_path)
        left_image = load_image(left_image_path)
        right_image = load_image(right_image_path)

        results = []

        if 'skew' in augmentations:
            results.append(('skew', augment_image(center_image), augment_image(left_image), augment_image(right_image)))
        if 'flip' in augmentations:
            results.append(('flip', flip_image(center_image), flip_image(left_image), flip_image(right_image)))
        if 'jitter' in augmentations:
            results.append(('jitter', color_jitter(center_image), color_jitter(left_image), color_jitter(right_image)))
        if 'cutout' in augmentations:
            results.append(('cutout', cutout(center_image), cutout(left_image), cutout(right_image)))

        for aug_type, center_aug, left_aug, right_aug in results:
            new_center_image_path = os.path.join(data_dir, 'images', f'{aug_type}_' + item['cam/image_array'])
            new_left_image_path = os.path.join(data_dir, 'images', f'{aug_type}_' + item['cam/left_image'])
            new_right_image_path = os.path.join(data_dir, 'images', f'{aug_type}_' + item['cam/right_image'])

            save_image(center_aug, new_center_image_path)
            save_image(left_aug, new_left_image_path)
            save_image(right_aug, new_right_image_path)

            new_metadata = item.copy()
            new_metadata['cam/image_array'] = f'{aug_type}_' + item['cam/image_array']
            new_metadata['cam/left_image'] = f'{aug_type}_' + item['cam/left_image']
            new_metadata['cam/right_image'] = f'{aug_type}_' + item['cam/right_image']

            global last_index
            last_index += 1
            new_metadata['_index'] = last_index

            if aug_type == 'flip':
                new_metadata['user/angle'] = new_metadata['user/angle'] * -1

            update_catalog('data//augment.catalog', new_metadata)
            item_line_length_index = item['_index'] % 1000
            item_line_length = catalog_manifest_data['line_lengths'][item_line_length_index]
            line_lengths.append(item_line_length)

    with ThreadPoolExecutor() as executor:
        for catalog_file, catalog_manifest_file in zip(catalog_files, catalog_manifest_files):
            catalog_path = os.path.join(base_path, catalog_file)
            catalog_manifest_path = os.path.join(base_path, catalog_manifest_file)
            with open(catalog_path, 'r') as file:
                catalog_data = [json.loads(line) for line in file if line.strip()]
            with open(catalog_manifest_path, 'r') as file:
                catalog_manifest_data = [json.loads(line) for line in file if line.strip()]
            catalog_manifest_data = catalog_manifest_data[0]

            executor.map(lambda item: process_item(item, augmentations), catalog_data)

    catalog_manifest_0_copy['line_lengths'] = line_lengths

    last_index_manifest_json['paths'] = last_index_manifest_json['paths'] + ['augment.catalog']
    last_index_manifest_json['current_index'] = last_index + 1
    last_index_manifest_json['max_len'] = max(len(line_lengths), 1000)

    update_catalog_manifest('data//augment.catalog_manifest', catalog_manifest_0_copy)
    update_manifest_json('data//manifest.json', last_index_manifest_json)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Image augmentation script.')
    parser.add_argument('--skew', action='store_true', help='Apply skew augmentation')
    parser.add_argument('--flip', action='store_true', help='Apply flip augmentation')
    parser.add_argument('--jitter', action='store_true', help='Apply color jitter augmentation')
    parser.add_argument('--cutout', action='store_true', help='Apply cutout augmentation')

    args = parser.parse_args()
    augmentations = []
    if args.skew:
        augmentations.append('skew')
    if args.flip:
        augmentations.append('flip')
    if args.jitter:
        augmentations.append('jitter')
    if args.cutout:
        augmentations.append('cutout')

    data_dir = "data"
    base_path = data_dir
    process_images(data_dir, base_path, augmentations)