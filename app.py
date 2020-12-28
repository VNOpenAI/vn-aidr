import cv2
import numpy as np
import uvicorn
import base64
import onnxruntime as rt
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File

# intialising the fastapi.
app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

session = rt.InferenceSession("trained_models\ct_lung_segmentation_20201228.onnx")
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

@app.post("/api/lung_ct")
def lung_ct_endpoint(file: bytes = File(...)):

    # contents = file.read()
    nparr = np.fromstring(file, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    img = cv2.resize(img, (256, 256))
    img = img.astype(np.float32).reshape((1, 256, 256))

    net_input = np.array([img])
    ort_inputs = {session.get_inputs()[0].name: net_input}
    ort_outs = session.run(None, ort_inputs)
    out_img = ort_outs[0].reshape((256, 256))
    out_img = out_img * 255
    out_img = out_img.astype(np.uint8)

    _, im_png = cv2.imencode(".png", out_img)
    encoded_img = base64.b64encode(im_png)

    response = {
        "success": True,
        "image": 'data:image/png;base64,{}'.format(encoded_img.decode())
    }

    return response

if __name__ == '__main__':
    uvicorn.run("app:app",host='0.0.0.0', port=5000, reload=True, debug=True, workers=1)