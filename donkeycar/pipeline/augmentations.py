import cv2
import logging
from cv2 import GaussianBlur
from cv2 import addWeighted
import numpy as np

from donkeycar.config import Config

logger = logging.getLogger(__name__)

class ImageAugmentation:
    def __init__(self, cfg, key, prob=0.5, always_apply=False):
        aug_list = getattr(cfg, key, [])
        self.augmentations = [ImageAugmentation.create(a, cfg, prob, always_apply) for a in aug_list]

    @classmethod
    def create(cls, aug_type: str, config: Config, prob, always) -> callable:
        """ Augmentation factory."""

        if aug_type == 'BRIGHTNESS':
                b_limit = getattr(config, 'AUG_BRIGHTNESS_RANGE', 0.2)
                logger.info(f'Creating augmentation {aug_type} {b_limit}')
                bightness = np.random.uniform(-b_limit, b_limit)
                return lambda img_arr: addWeighted(img_arr, 1.0 + bightness, img_arr, 0, 0)
                
        
        elif aug_type == 'BLUR':
            b_range = getattr(config, 'AUG_BLUR_RANGE', 3)
            logger.info(f'Creating augmentation {aug_type} {b_range}')
            return lambda img_arr: GaussianBlur(img_arr, (13, 13), b_range)
        
    # Parts interface
    def run(self, img_arr):
        for augmentation in self.augmentations:
            img_arr = augmentation(img_arr)
        return img_arr