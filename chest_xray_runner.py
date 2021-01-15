import os
import json
import argparse

import numpy as np
import cv2
import onnxruntime as rt
from easydict import EasyDict as edict

from model_utils.chest_xray_utils import *
from model_utils.contours import *
from config import *

class ChestXrayModelRunner():

    def __init__(self):
        self.model = rt.InferenceSession(CHEST_XRAY_MODEL_PATH)
        with open(CHEST_XRAY_CONFIG_PATH) as f:
            self.cfg = edict(json.load(f))
        self.labels = [
            'Cardiomegaly',
            'Edema',
            'Consolidation',
            'Atelectasis',
            'Pleural Effusion'
        ]
    
    def predict(self, img):
        """
        Input: BGR image
        Output: probability mask, label
        """
        
        processed_img, padding_percent = preprocess(self.cfg, img)
        width_pad_percent, height_pad_percent = padding_percent

        net_input = np.expand_dims(processed_img, axis=0)
        ort_inputs = {self.model.get_inputs()[0].name: net_input}
        ort_outs = self.model.run(None, ort_inputs)

        # Apply sigmoid to classification result
        for i in range(len(ort_outs)):
            ort_outs[i] = 1/(1 + np.exp(-ort_outs[i])) 
        proba = np.array(ort_outs[:5]).flatten().tolist()

        # Get heatmaps
        heatmaps = ort_outs[5:10]

        # Prepare classification result and heatmaps
        results = []
        for i in range(len(proba)):
            result = {}
            result["label"] = self.labels[i]
            result["probability"] = proba[i]

            # Add heatmap to output if probability > 0.5
            if proba[i] > 0.5:
                heatmap = heatmaps[i]
                heatmap = remove_padding(heatmap, width_pad_percent, height_pad_percent)
                result["heatmap"] = heatmap

            results.append(result)

        return results

    
    def get_visualized_img(self, img, heatmap):
        """
        Input: BGR image
        Output: Visualized result
        """

        # Normalize heatmap
        max_value = np.max(heatmap)
        if max_value != 0:
            heatmap = heatmap / max_value

        # Only show large values on heatmap
        p80 = np.quantile(heatmap, 0.8)
        heatmap[heatmap < p80] = 0
        heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
        heatmap = cv2.GaussianBlur(heatmap, (11, 11), 0)
        
        # Bind color heatmap with original image
        color_heatmap = cv2.applyColorMap(np.uint8(255*heatmap), cv2.COLORMAP_JET)
        binded_img = cv2.addWeighted(color_heatmap, 0.3, img, 0.7, 0.0)
        bgr_heatmap = cv2.cvtColor(heatmap, cv2.COLOR_GRAY2BGR)
        binded_img = (bgr_heatmap * binded_img).astype(np.uint8)
        bg_img = img.copy()
        bg_img = ((1 - bgr_heatmap) * bg_img).astype(np.uint8)
        binded_img = cv2.add(binded_img, bg_img)

        return binded_img
