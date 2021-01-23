import cv2
import numpy as np
from skimage.morphology import remove_small_objects, remove_small_holes
from .common import get_areamax2

def postprocess_mask(img, mask, use_contour=True, thresh_obj=100, thresh_hole=36, add_pixel=20):

    _, mask = cv2.threshold(mask, 0.5, 1, cv2.THRESH_BINARY)
    mask = mask.astype(np.bool)
    remove_small_objects(mask, thresh_obj, in_place=True)
    remove_small_holes(mask, thresh_hole, in_place=True)

    if use_contour:
        contours, _ = cv2.findContours(
            (mask*255).astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        ms = get_areamax2(contours)
        new_img = np.zeros(mask.shape).astype(np.uint8)
        [cv2.fillPoly(new_img, [contours[aa].reshape((-1, 2))],
                      (255, 255, 255)) for aa in ms]
        mask = new_img/255.
    else:
        mask = mask*1.0
    
    im_height, im_width = img.shape[:2]
    mask = cv2.resize(mask, (im_width, im_height))
    mask[mask > 0] = 1
    _, mask = cv2.threshold(mask, 0.5, 255, cv2.THRESH_BINARY)
    mask = mask.astype(np.uint8)

    return mask
