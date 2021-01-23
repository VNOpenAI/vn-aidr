import argparse
import json
import os

import cv2
import numpy as np
import onnxruntime as rt

from configs.common import *
from configs.skin_lesion import SkinLeisonSegmentationConfig
from model_utils.contours import draw_contours, find_contours
from model_utils.segmentation import postprocess_mask


class SkinLesionSegmentationRunner():

    def __init__(self):

        self.config  = SkinLeisonSegmentationConfig()
        self.model = rt.InferenceSession(self.config.weights)
    
    def predict(self, img):
        """
        Input: BGR image
        Output: Segmented mask
        """
        resized_img = cv2.resize(img, self.config.img_size)
        net_input = resized_img.astype(np.float32)
        net_input = net_input - np.median(net_input) + 127.0
        net_input /= 255.0
        net_input = np.expand_dims(net_input, axis=0)
        ort_inputs = {self.model.get_inputs()[0].name: net_input}
        ort_outs = self.model.run(None, ort_inputs)
        mask = ort_outs[0][0][:, :, 1]
        mask = cv2.resize(mask, self.config.img_size)
        mask = (mask * 255).astype(np.uint8)

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
