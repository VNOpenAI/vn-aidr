import cv2
import imutils

def find_contours(mask):
    """Find contours in a binary mask"""

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    return cnts


def draw_contours(img, cnts, draw_center=False):
    """Draw contours

    Args:
        img: Image to draw on
        cnts: Contours found by OpenCV
    """

    draw = img.copy()
    for c in cnts:
        # Draw the contour
        cv2.drawContours(draw, [c], -1, (0, 255, 0), 2)

        # Draw the center of the shape on the image
        if draw_center:
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            cv2.circle(draw, (cX, cY), 7, (255, 255, 255), -1)
            cv2.putText(draw, "center", (cX - 20, cY - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
 
    return draw