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

from configs.common import *
from configs.chest_abnormalities_detection import ChestAbnormalitiesDetectron2Config
from model_utils.contours import *


class ChestXrayDetectionDetectronRunner():

    def __init__(self):

        self.config = ChestAbnormalitiesDetectron2Config()
        
        c = get_cfg()
        fastRCNN = 'COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml'
        model_cfg = model_zoo.get_config_file(fastRCNN)
        c.merge_from_file(model_cfg)
        c.OUTPUT_DIR = "out"

        c.DATALOADER.NUM_WORKERS = 2
        c.SOLVER.IMS_PER_BATCH = 2
        c.MODEL.WEIGHTS = os.path.join(self.config.weights)  # path to the model we just trained
        c.MODEL.DEVICE = 'cpu'

        c.SOLVER.BASE_LR = 0.00025 
        c.SOLVER.MAX_ITER = 20000
        c.MODEL.ROI_HEADS.BATCH_SIZE_PER_IMAGE = 128   
        c.MODEL.ROI_HEADS.NUM_CLASSES = 14

        c.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.3
        self.predictor = DefaultPredictor(c)
    
    def predict(self, img, img_id):
        """
        Input: BGR images
        """

        pr_viz = predict_and_visualize(self.predictor, img, self.config.labels, viz_size=(img.shape[1], img.shape[0]))

        return pr_viz
