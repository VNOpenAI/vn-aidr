import numpy as np
import cv2

def _resize_read_xray(data_shape, bbox, new_shape):
    """
    - Input:
        1. Tuple of original data shape
        2. Tuple of bbox data
        3. Tuple of desired shape.
    - Output:
        1. A tuple of resized bbox
    """
    # Scalling factor
    y_scale = new_shape[0] / data_shape[0]
    x_scale = new_shape[1] / data_shape[1]

    # Transforming bbox
    x_min, y_min, x_max, y_max = bbox
    x_min_scale = int(np.round(x_min * x_scale))
    y_min_scale = int(np.round(y_min * y_scale))
    x_max_scale = int(np.round(x_max * x_scale))
    y_max_scale = int(np.round(y_max * y_scale))

    return x_min_scale, y_min_scale, x_max_scale, y_max_scale


def predict_and_visualize(
        predictor,
        image,
        classes: list,
        viz_size: tuple):
    """
    - Input:
      1. image: input image to predictor
      2. predictor: predictor in the format output of Detectron2
      3. classes:  list of output class, as in the config of Detectron2 model
      4. viz_size: size of visualization image
    - Output:
      Plotted image with bbox of deceases
    """

    net_input = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32)
    outputs = predictor(net_input)
    bboxes = [np.array(i)
              for i in list(outputs['instances'].pred_boxes.to('cpu'))]
    scores = [np.array(i) for i in list(outputs['instances'].scores.to('cpu'))]

    # Please notice the order of output
    class_names = [classes[i]
                   for i in list(outputs['instances'].pred_classes.to('cpu'))]

    draw = cv2.resize(image, viz_size)
    x_scale = viz_size[0] / image.shape[1]
    y_scale = viz_size[1] / image.shape[0]
    for box, class_name, score in zip(bboxes, class_names, scores):
        x1 = int(box[0] * x_scale)
        y1 = int(box[1] * y_scale)
        x2 = int(box[2] * x_scale)
        y2 = int(box[3] * y_scale)
        cv2.rectangle(draw, (x1, y1), (x2, y2), (0, 0, 255), 1)
        class_name_with_score = '{} {:.2f}'.format(class_name, score)
        ((text_width, text_height), _) = cv2.getTextSize(
            class_name_with_score, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1)
        cv2.rectangle(draw, (x1, y1 - int(1.3 * text_height)),
                      (x1 + text_width, y1), (0, 0, 255), -1)
        cv2.putText(
            draw,
            text=class_name_with_score,
            org=(x1, y1 - int(0.3 * text_height)),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.0,
            color=(0, 0, 0),
            lineType=cv2.LINE_AA,
        )

    label = "Prediction"
    (text_width, text_height), _ = cv2.getTextSize(
        label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1)
    cv2.rectangle(draw, (0, 0), (20 + text_width, 40), (0, 255, 0), -1)
    cv2.putText(
        draw,
        text=label,
        org=(10, 30),
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=1.0,
        color=(0, 0, 0),
        lineType=cv2.LINE_AA,
    )

    return draw
