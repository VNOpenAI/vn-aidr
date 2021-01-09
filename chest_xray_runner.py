import os
import json
import argparse

import numpy as np
import cv2
import onnxruntime as rt
from easydict import EasyDict as edict

from model_utils.chest_xray_utils import *
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
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        processed_img, padding_percent = preprocess(self.cfg, gray)
        width_pad_percent, height_pad_percent = padding_percent

        net_input = np.expand_dims(processed_img, axis=0)
        ort_inputs = {self.model.get_inputs()[0].name: net_input}
        ort_outs = self.model.run(None, ort_inputs)

        # Apply sigmoid
        for i in range(len(ort_outs)):
            ort_outs[i] = 1/(1 + np.exp(-ort_outs[i])) 
        proba = np.array(ort_outs[:5]).flatten().tolist()

        # Assign labels for probability
        proba_with_labels = {}
        for i in range(len(proba)):
            proba_with_labels[self.labels[i]] = proba[i]

        # Heatmap
        heatmaps = ort_outs[5:10]

        # Remove paddding for heatmap
        for i in range(len(heatmaps)):
            heatmaps[i] = remove_padding(heatmaps[i], width_pad_percent, height_pad_percent)

        return proba_with_labels, heatmaps

    
    def get_visualized_img(self, img, heatmaps):
        """
        Input: BGR image
        Output: Visualized result
        """
        heatmap = np.sum(heatmaps, axis=0)
        heatmap = np.maximum(heatmap, 0)
        heatmap /= np.max(heatmap)

        heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
        heatmap = cv2.applyColorMap(np.uint8(255*heatmap), cv2.COLORMAP_JET)

        intensity = 0.2
        img = heatmap * intensity + img
        return img
