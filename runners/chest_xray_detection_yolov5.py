import sys
sys.path.append("model_utils/yolov5")

import cv2
import numpy as np
import pandas as pd
import torch
import torch.backends.cudnn as cudnn
from numpy import random

from configs.chest_abnormalities_detection import \
    ChestAbnormalitiesYOLOv5Config
from configs.common import *
from model_utils.yolov5.models.experimental import attempt_load
from model_utils.yolov5.utils.general import (apply_classifier, check_img_size,
                                              non_max_suppression,
                                              scale_coords, set_logging,
                                              xyxy2xywh)
from model_utils.yolov5.utils.plots import plot_one_box
from model_utils.yolov5.utils.torch_utils import load_classifier, select_device




class ChestXrayDetectionYOLOv5Runner():

    def __init__(self):

        cfg = ChestAbnormalitiesYOLOv5Config()
        self.cfg = cfg
        # Initialize
        set_logging()
        self.device = select_device(cfg.device)
        self.half = self.device.type != 'cpu'  # half precision only supported on CUDA

        # Load model
        self.model = attempt_load(
            cfg.weights, map_location=self.device)  # load FP32 model
        self.imgsz = check_img_size(
            cfg.imgsz, s=self.model.stride.max())  # check img_size
        if self.half:
            self.model.half()  # to FP16

        # Second-stage classifier
        self.classify = False
        if self.classify:
            self.modelc = load_classifier(name='resnet101', n=2)  # initialize
            self.modelc.load_state_dict(torch.load(
                'weights/resnet101.pt', map_location=self.device)['model']).to(self.device).eval()

        # Get names and colors
        self.names = self.model.module.names if hasattr(
            self.model, 'module') else self.model.names
        self.colors = [[random.randint(0, 255)
                        for _ in range(3)] for _ in self.names]

        # Run inference
        img = torch.zeros((1, 3, self.imgsz, self.imgsz),
                          device=self.device)  # init img
        _ = self.model(img.half(
        ) if self.half else img) if self.device.type != 'cpu' else None  # run once


    def predict(self, img0, img_id):
        """
        Input: BGR images
        """

        # Padded resize
        img = letterbox(img0, new_shape=self.imgsz)[0]

        # Prepare image as net input
        img = img[:, :, ::-1].transpose(2, 0, 1)  # BGR to RGB, to 3x416x416
        img = np.ascontiguousarray(img)
        img = torch.from_numpy(img).to(self.device)
        img = img.half() if self.half else img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if img.ndimension() == 3:
            img = img.unsqueeze(0)

        # Inference
        pred = self.model(img, augment=False)[0]

        # Apply NMS
        pred = non_max_suppression(
            pred, self.cfg.conf_thres, self.cfg.iou_thres, agnostic=self.cfg.agnostic_nms)

        # Apply Classifier
        if self.classify:
            pred = apply_classifier(pred, self.modelc, img, img0)

        # Process detections
        draw = img0.copy()
        for i, det in enumerate(pred):  # detections per image
            # normalization gain whwh
            gn = torch.tensor(draw.shape)[[1, 0, 1, 0]]
            if len(det):
                # Rescale boxes from img_size to draw size
                det[:, :4] = scale_coords(
                    img.shape[2:], det[:, :4], draw.shape).round()

                # Print results
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()  # detections per class
                # Write results
                for *xyxy, conf, cls in reversed(det):
                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) /
                            gn).view(-1).tolist()  # normalized xywh
                    label = f'{self.names[int(cls)]} {conf:.2f}'
                    plot_one_box(xyxy, draw, label=label,
                                 color=self.colors[int(cls)], line_thickness=3)

        label = "Prediction"
        (text_width, text_height), _ = cv2.getTextSize(
            label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1)
        cv2.rectangle(draw, (0, 0), (20 + text_width, 40), (0, 255, 0), -1)
        cv2.putText(
            draw,
            text=label,
            org=(10, 30),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.0,
            color=(0, 0, 0),
            lineType=cv2.LINE_AA,
        )

        return draw


def letterbox(img, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True):
    # Resize image to a 32-pixel-multiple rectangle https://github.com/ultralytics/yolov3/issues/232
    shape = img.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better test mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # width, height ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - \
        new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, 32), np.mod(dh, 32)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])
        ratio = new_shape[1] / shape[1], new_shape[0] / \
            shape[0]  # width, height ratios

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    img = cv2.copyMakeBorder(
        img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return img, ratio, (dw, dh)
