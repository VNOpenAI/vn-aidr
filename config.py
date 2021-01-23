USE_GPU = False

ENABLE_ACCENT_MODEL = False
ACCENT_MODEL_CONFIG_PATH = "model_utils/vn_accent/model_config.json"
ACCENT_MODEL_NAME = "transformer_evolved"
ACCENT_MODEL_PATH = "trained_models/vn_accent/transformer_evolved_ep14.h5"
ACCENT_MODEL_TOKENIZER_PATH = "trained_models/vn_accent/tokenizer.h5"

LUNG_CT_SEGMENTATION_MODEL_PATH = "trained_models/ct_lung_segmentation_20201228.onnx"

CHEST_XRAY_CLASSIFICATION_MODEL_PATH = "trained_models/chest_xray_classification/chest_xray_abnormalities_effficentnetb4_20210114.onnx"
CHEST_XRAY_CLASSIFICATION_CONFIG_PATH = "trained_models/chest_xray_classification/chest_xray_20210109_config.json"

CHEST_XRAY_DETECTION_MODEL_PATH = "trained_models/chest_xray_detection/chest_xray_abnormalities_20200118.pth"
CHEST_XRAY_DETECTION_META_FILE = "trained_models/chest_xray_detection/train_meta.csv"
CHEST_XRAY_DETECTION_TRAIN_FILE = "trained_models/chest_xray_detection/train.csv"

class YOLOConfig:
    weights = ["trained_models/chest_xray_detection_yolov5/chest_xray_abnomalities_20200123.pt"]
    device = "cpu"
    imgsz = 512
    conf_thres = 0.5
    iou_thres = 0.45
    agnostic_nms = False