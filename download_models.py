import gdown
import os
from pathlib import Path


DATA_FILES = [
    {
        "path": "trained_models/chest_xray_classification/chest_xray_20210109_config.json",
        "url": "https://drive.google.com/uc?id=1-vIVreY3gsI_9b_H8D9kQm-eV8Gk-Hvd"
    },
    {
        "path": "trained_models/chest_xray_classification/chest_xray_effficentnetb4_20210114.onnx",
        "url": "https://drive.google.com/uc?id=1N49KJ_naExOzSJVMKPcjpcHZrkPPO6gV"
    },
    {
        "path": "trained_models/vn_accent/tokenizer.h5",
        "url": "https://drive.google.com/uc?id=1fqtQrs3y_a63z6_fJ4Z-FJnreL0k3zp5"
    },
    {
        "path": "trained_models/vn_accent/transformer_evolved_ep14.h5",
        "url": "https://drive.google.com/uc?id=1hbA78RVq5wdsM3H3YCn0YXyGP5D1DsLc"
    },
    {
        "path": "trained_models/chest_xray_detection/train_meta.csv",
        "url": "https://drive.google.com/uc?id=13YrjdHMSR2I2JIUHVw0t4lbgS_1JQRvF"
    },
    {
        "path": "trained_models/chest_xray_detection/train.csv",
        "url": "https://drive.google.com/uc?id=13SJCsvUdwZWciZIC4cbAhdrbVGqBPIZd"
    },
    {
        "path": "trained_models/chest_xray_detection/chest_xray_abnomalities_20200118.pth",
        "url": "https://drive.google.com/uc?id=11aJO_cLaXtdYKb3M02BjuTQ3Uq1anwIe"
    }
]

def download_file(url, file_path, force=False):
    """Download a file from Google Drive
    """

    if os.path.exists(file_path) and not force:
        return
    dirname = os.path.dirname(file_path)
    Path(dirname).mkdir(parents=True, exist_ok=True)
    gdown.download(url, file_path, quiet=False)


def download_models_and_data():
    """Download all models and data files"""

    for file in DATA_FILES:
        download_file(file["url"], file["path"])