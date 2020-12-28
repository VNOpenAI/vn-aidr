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
from faceswap import faceswapfunc
import imutils

IM_HEIGHT = 500

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


face = imutils.resize(cv2.imread("face1.jpg"), height=IM_HEIGHT)
hairstyle = imutils.resize(cv2.imread("face2.jpg"), height=IM_HEIGHT)
out_face = faceswapfunc(hairstyle, face)

@app.post("/api/hair")
def face(file: bytes = File(...)):

    global face, hairstyle, out_face

    nparr = np.fromstring(file, np.uint8)
    hair = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    hair = imutils.resize(hair, height=IM_HEIGHT)

    hairstyle = hair
    face = imutils.resize(cv2.imread("face1.jpg"), height=IM_HEIGHT)
    out_face = faceswapfunc(hairstyle, face)
    out_face = imutils.resize(out_face, height=IM_HEIGHT)
    
    # Generate output image
    output_img = cv2.hconcat([face, hairstyle, out_face])

    # Return
    _, im_png = cv2.imencode(".png", output_img)
    encoded_img = base64.b64encode(im_png)
    response = {
        "success": True,
        "image": 'data:image/png;base64,{}'.format(encoded_img.decode())
    }
    return response


@app.post("/api/face")
def face(file: bytes = File(...)):

    global face, hairstyle, out_face

    nparr = np.fromstring(file, np.uint8)
    face = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    face = imutils.resize(face, height=IM_HEIGHT)

    cv2.imshow("hairstyle", hairstyle)
    cv2.imshow("face", face)
    cv2.imshow("out_face", out_face)
    cv2.waitKey(0)
    out_face = faceswapfunc(hairstyle, face)
    out_face = imutils.resize(out_face, height=IM_HEIGHT)
    
    # Generate output image
    output_img = cv2.hconcat([face, hairstyle, out_face])

    # Return
    _, im_png = cv2.imencode(".png", output_img)
    encoded_img = base64.b64encode(im_png)
    response = {
        "success": True,
        "image": 'data:image/png;base64,{}'.format(encoded_img.decode())
    }
    return response

if __name__ == '__main__':
    uvicorn.run("app:app",host='0.0.0.0', port=5000, reload=True, debug=True, workers=1)