import cv2
import os
import numpy as np
import uvicorn
import base64
import onnxruntime as rt
from starlette.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File
from fastapi.staticfiles import StaticFiles
from utils import postprocess_mask

# intialising the fastapi.
app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# Load model
session = rt.InferenceSession("trained_models\ct_lung_segmentation_20201228.onnx")

# Static files
@app.route("/")
def homepage(data):
    return RedirectResponse(url='/ui/index.html')
app.mount("/ui/", StaticFiles(directory="frontend"), name="static")

@app.post("/api/lung_ct")
def lung_ct_endpoint(file: bytes = File(...)):

    nparr = np.fromstring(file, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    
    # Inference
    resized_img = cv2.resize(img, (256, 256))
    net_input = resized_img.astype(np.float32).reshape((1, 1, 256, 256))
    ort_inputs = {session.get_inputs()[0].name: net_input}
    ort_outs = session.run(None, ort_inputs)
    mask = ort_outs[0].reshape((256, 256))

    # Process mask
    mask = postprocess_mask(img, mask)

    # Generate output image
    out_img = cv2.hconcat([img, mask])

    # Return
    _, im_png = cv2.imencode(".png", out_img)
    encoded_img = base64.b64encode(im_png)
    response = {
        "success": True,
        "image": 'data:image/png;base64,{}'.format(encoded_img.decode())
    }
    return response

if __name__ == '__main__':
    uvicorn.run("app:app",host='0.0.0.0', port=5000, reload=True, debug=True, workers=1)