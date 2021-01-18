import os
import warnings

import pandas as pd
from detectron2 import model_zoo
from detectron2.config import get_cfg
from detectron2.engine import DefaultPredictor
from detectron2.utils.logger import setup_logger

from model_utils.chest_xray_detection import *

setup_logger()
warnings.filterwarnings("ignore")

from config import *
from model_utils.contours import *


class ChestXrayDetectionRunner():

    def __init__(self):
        
        cfg = get_cfg()
        fastRCNN = 'COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml'
        model_cfg = model_zoo.get_config_file(fastRCNN)
        cfg.merge_from_file(model_cfg)
        cfg.OUTPUT_DIR = "out"

        cfg.DATALOADER.NUM_WORKERS = 2
        cfg.SOLVER.IMS_PER_BATCH = 2
        cfg.MODEL.WEIGHTS = os.path.join(CHEST_XRAY_DETECTION_MODEL_PATH)  # path to the model we just trained
        cfg.MODEL.DEVICE = 'cpu'

        cfg.SOLVER.BASE_LR = 0.00025 
        cfg.SOLVER.MAX_ITER = 20000
        cfg.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128   
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = 14

        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.3
        self.predictor = DefaultPredictor(cfg)

        self.train_df = pd.read_csv(CHEST_XRAY_DETECTION_TRAIN_FILE)
        self.train_meta_df = pd.read_csv(CHEST_XRAY_DETECTION_META_FILE)

    
    def predict(self, img, img_id):
        """
        Input: BGR images
        """

        gt_viz = visualize_ground_truth(img, img_id, self.train_df, self.train_meta_df)
        if gt_viz is None:
            gt_viz = img.copy()

        pr_viz = predict_and_visualize(self.predictor, img, CLASSES, viz_size=(gt_viz.shape[1], gt_viz.shape[0]))

        return gt_viz, pr_viz
