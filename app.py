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
from utils import postprocess_mask, find_contours, draw_contours
import accent.model as accent_model_lib

# intialising the fastapi.
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
lung_model = rt.InferenceSession("trained_models/ct_lung_segmentation_20201228.onnx")
accent_model = accent_model_lib.load_model("trained_models/vietnamese_accent_v1")

@app.post("/api/lung_ct")
def lung_ct_endpoint(file: bytes = File(...)):

    nparr = np.fromstring(file, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Inference
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resized_img = cv2.resize(gray, (256, 256))
    net_input = resized_img.astype(np.float32).reshape((1, 1, 256, 256))
    ort_inputs = {lung_model.get_inputs()[0].name: net_input}
    ort_outs = lung_model.run(None, ort_inputs)
    mask = ort_outs[0].reshape((256, 256))

    # Process mask
    mask = postprocess_mask(img, mask)
    contours = find_contours(mask)
    img = draw_contours(img, contours)

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


# Process medical conclusion
@app.get("/api/accent")
def accented(text):
    """ Add accent to given plain text """
    accented_text = accent_model.add_accent(text)
    print(accented_text)
    return {
        'original': text,
        'with_accent': accented_text
    }

if __name__ == '__main__':
    uvicorn.run("app:app",host='0.0.0.0', port=5000, reload=True, debug=True, workers=1)