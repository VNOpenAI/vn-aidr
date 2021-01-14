import cv2
import argparse
import numpy as np
import uvicorn
import base64
from starlette.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File
from fastapi.staticfiles import StaticFiles
from vnaccent_runner import VNAccentRunner
from lung_seg_runner import LungSegmentationRunner
from chest_xray_runner import ChestXrayModelRunner


def get_arg():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000, required=False)
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
accent_model = VNAccentRunner()
lung_seg_model = LungSegmentationRunner()
chest_xray_model = ChestXrayModelRunner()

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

    # Return
    _, im_png = cv2.imencode(".png", out_img)
    encoded_img = base64.b64encode(im_png)
    response = {
        "success": True,
        "image": 'data:image/png;base64,{}'.format(encoded_img.decode())
    }
    return response


@app.post("/api/chest_xray")
def chest_xray_endpoint(file: bytes = File(...)):

    nparr = np.fromstring(file, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Inference
    proba, heatmaps = chest_xray_model.predict(img)
    viz_img = chest_xray_model.get_visualized_img(img, heatmaps)

    # Generate output image
    # out_img = cv2.hconcat([img, viz_img])
    out_img = viz_img

    # Return
    _, im_png = cv2.imencode(".png", out_img)
    encoded_img = base64.b64encode(im_png)
    response = {
        "success": True,
        "proba": proba,
        "image": 'data:image/png;base64,{}'.format(encoded_img.decode())
    }
    return response


# Process medical conclusion
@app.get("/api/vn_accent")
def accented(text):
    """ Add accent to given plain text """
    accented_text = accent_model.predict(text)
    print(accented_text)
    return {
        "success": True,
        "original": text,
        "with_accent": accented_text
    }

if __name__ == '__main__':
    args = get_arg()
    uvicorn.run("app:app",host='0.0.0.0', port=args.port, reload=True, debug=True, workers=1)