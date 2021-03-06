import argparse

import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, File, Form
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from model_utils.transforms import get_base64_png
from configs.common import ENABLE_ACCENT_MODEL
from download_models import download_models_and_data

from runners.lung_ct_seg import LungSegmentationRunner
from runners.vn_accent import VNAccentRunner
from runners.chest_xray_detection_detectron import ChestXrayDetectionDetectronRunner
from runners.chest_xray_detection_yolov5 import ChestXrayDetectionYOLOv5Runner
from runners.chest_xray_classification import ChestXrayClassificationRunner
from runners.skin_lesion_seg import SkinLesionSegmentationRunner

# Download models and data first
download_models_and_data()

def get_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=80, required=False)
    args = parser.parse_args()
    return args

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# Static files
@app.route("/")
def homepage(data):
    return RedirectResponse(url='/ui/index.html')
app.mount("/ui/", StaticFiles(directory="frontend"), name="static")

# Load models
if ENABLE_ACCENT_MODEL:
    accent_model = VNAccentRunner()
lung_seg_model = LungSegmentationRunner()
skin_lesion_seg_model = SkinLesionSegmentationRunner()
chest_xray_model = ChestXrayClassificationRunner()
chest_xray_detection_model = ChestXrayDetectionDetectronRunner()
chest_xray_detection_yolov5_model = ChestXrayDetectionYOLOv5Runner()

@app.post("/api/lung_ct_seg")
def lung_ct_endpoint(file: bytes = File(...)):

    nparr = np.fromstring(file, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Inference
    mask = lung_seg_model.predict(img)
    img = lung_seg_model.get_visualized_img(img, mask)

    # Generate output image
    # out_img = cv2.hconcat([img, mask])
    out_img = img

    response = {
        "success": True,
        "prepend_original_image": False,
        "results": [
            {
                "label": "Segmentation Map",
                "image": get_base64_png(out_img)
            }
        ]
    }
    return response


@app.post("/api/skin_lesion_seg")
def skin_lesion_endpoint(file: bytes = File(...)):

    nparr = np.fromstring(file, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Inference
    mask = skin_lesion_seg_model.predict(img)
    img = skin_lesion_seg_model.get_visualized_img(img, mask)

    # Generate output image
    out_img = img

    response = {
        "success": True,
        "prepend_original_image": False,
        "results": [
            {
                "label": "Segmentation Map",
                "image": get_base64_png(out_img)
            }
        ]
    }
    return response


@app.post("/api/chest_xray_classification")
def chest_xray_endpoint(file: bytes = File(...)):

    nparr = np.fromstring(file, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Inference
    model_results = chest_xray_model.predict(img)
    ## Result format:
    # [{
    #     "label": <label>
    #     "probability": 0.9,
    #     "heatmap": <np.array>
    # }, ...]

    # Prepare result
    api_results = []
    for result in model_results:
        api_result = {
            "label": result["label"],
            "probability": result["probability"]
        }

        if "heatmap" in result.keys():
            heatmap = result["heatmap"]
            color_heatmap = chest_xray_model.get_visualized_img(img, heatmap)
            base64_img = get_base64_png(color_heatmap)
            api_result["image"] = base64_img
        api_results.append(api_result)

    response = {
        "success": True,
        "prepend_original_image": True,
        "results": api_results
    }
    return response


@app.post("/api/chest_xray_detection")
def chest_xray_detection_endpoint(file: bytes = File(...), filename: str = Form(...)):

    nparr = np.fromstring(file, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Inference
    img_id = filename.split(".")[0]
    pr_viz, gt_viz = chest_xray_detection_model.predict(img, img_id=img_id, draw_gt=True)

    pr_viz = cv2.resize(pr_viz, (gt_viz.shape[1], gt_viz.shape[0]))
    out_img = cv2.hconcat([gt_viz, pr_viz])

    response = {
        "success": True,
        "prepend_original_image": False,
        "results": [
            {
                "label": "Prediction Result",
                "image": get_base64_png(out_img)
            }
        ]
    }
    return response



@app.post("/api/chest_xray_detection_yolov5")
def chest_xray_detection_yolov5_endpoint(file: bytes = File(...), filename: str = Form(...)):

    nparr = np.fromstring(file, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Inference
    img_id = filename.split(".")[0]
    pr_viz, gt_viz = chest_xray_detection_yolov5_model.predict(img, img_id=img_id, draw_gt=True)

    pr_viz = cv2.resize(pr_viz, (gt_viz.shape[1], gt_viz.shape[0]))
    out_img = cv2.hconcat([gt_viz, pr_viz])

    response = {
        "success": True,
        "prepend_original_image": False,
        "results": [
            {
                "label": "Prediction Result",
                "image": get_base64_png(out_img)
            }
        ]
    }
    return response


# Process medical conclusion
@app.get("/api/vn_accent")
def accented(text):
    """ Add accent to given plain text """
    if ENABLE_ACCENT_MODEL:
        accented_text = accent_model.predict(text)
    else:
        accented_text = text
    return {
        "success": True,
        "original": text,
        "with_accent": accented_text
    }

if __name__ == '__main__':
    args = get_arg()
    uvicorn.run("app:app", host='0.0.0.0', port=args.port)
