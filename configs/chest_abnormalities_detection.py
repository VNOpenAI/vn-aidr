from .common import USE_GPU

class ChestAbnormalitiesDetectron2Config:
    model_base = "COCO-Detection/faster_rcnn_R_50_FPN_3x.yaml"
    weights = "trained_models/chest_xray_detection_detectron/chest_xray_abnormalities_20210118.pth"
    labels = [
        'Aortic enlargement',
        'Atelectasis',
        'Calcification',
        'Cardiomegaly',
        'Consolidation',
        'ILD',
        'Infiltration',
        'Lung Opacity',
        'Nodule/Mass',
        'Other lesion',
        'Pleural effusion',
        'Pleural thickening',
        'Pneumothorax',
        'Pulmonary fibrosis',
    ]
    device = "cpu" if not USE_GPU else "cuda"
    conf_thres = 0.5

class ChestAbnormalitiesYOLOv5Config:
    weights = ["trained_models/chest_xray_detection_yolov5/chest_xray_abnomalities_20210123.pt"]
    device = "cpu" if not USE_GPU else "cuda"
    img_size = 512
    conf_thres = 0.5
    iou_thres = 0.45
    agnostic_nms = False
