import cv2
import base64


def get_base64_png(img):
    """Get base64 png format of an OpenCV image
    """
    _, im_png = cv2.imencode(".png", img)
    encoded_img = base64.b64encode(im_png)
    result = 'data:image/png;base64,{}'.format(encoded_img.decode())
    return result