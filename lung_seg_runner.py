import os
import json
import argparse

import numpy as np
import cv2
import onnxruntime as rt

from model_utils.lung_seg_utils import postprocess_mask, find_contours, draw_contours
from config import *

class LungSegmentationRunner():

    def __init__(self):
        self.model = rt.InferenceSession(LUNG_CT_SEGMENTATION_MODEL_PATH)
    
    def predict(self, img):
        """
        Input: BGR image
        Output: Segmented mask
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        resized_img = cv2.resize(gray, (256, 256))
        net_input = resized_img.astype(np.float32).reshape((1, 1, 256, 256))
        ort_inputs = {self.model.get_inputs()[0].name: net_input}
        ort_outs = self.model.run(None, ort_inputs)
        mask = ort_outs[0].reshape((256, 256))

        # Process mask
        mask = postprocess_mask(img, mask)
        return mask

    
    def get_visualized_img(self, img, mask):
        """
        Input: BGR image
        Output: Visualized result
        """
        contours = find_contours(mask)
        img = draw_contours(img, contours)
        return img
