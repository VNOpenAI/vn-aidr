import argparse
import json
import os

import cv2
import numpy as np
import onnxruntime as rt

from configs.common import *
from configs.lung_ct_seg import LungCTSegmentationConfig
from model_utils.contours import draw_contours, find_contours
from model_utils.lung_ct_seg import postprocess_mask


class LungSegmentationRunner():

    def __init__(self):

        self.config  = LungCTSegmentationConfig()
        self.model = rt.InferenceSession(self.config.weights)
    
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
