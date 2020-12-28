import cv2
import numpy as np
from skimage.morphology import remove_small_objects, remove_small_holes

def area(vs):
    a = 0
    x0, y0 = vs[0]
    for [x1, y1] in vs[1:]:
        dx = x1-x0
        dy = y1-y0
        a += 0.5*(y0*dx - x0*dy)
        x0 = x1
        y0 = y1
    return a

def get_areamax2(contours):
    area_max = 0.0
    area_amax = 0.0
    id_max = 0
    id_amax = 0
    for i, contour in enumerate(contours):
        contour = contour.reshape((-1, 2))
        s = area(contour)
        if s > area_max:
            area_amax = area_max
            area_max = s
            id_amax = id_max
            id_max = i
        elif s > area_amax:
            area_amax = s
            id_amax = i
    return id_max, id_amax

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
