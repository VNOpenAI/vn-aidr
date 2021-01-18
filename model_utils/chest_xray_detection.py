import numpy as np
import pandas as pd
import cv2


CLASSES = [
    'Aortic enlargement',
    'Atelectasis',
    'Calcification',
    'Cardiomegaly',
    'Consolidation',
    'ILD',
    'Infiltration',
    'Lung Opacity',
    'Nodule/Mass',
    'Other lesion',
    'Pleural effusion',
    'Pleural thickening',
    'Pneumothorax',
    'Pulmonary fibrosis',
]

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
   
    return x_min_scale,y_min_scale,x_max_scale,y_max_scale

def visualize_ground_truth(image,
                         img_id,
                         df: pd.DataFrame,
                         original_df: pd.DataFrame):
  
    """
    - Input:
      1. img_id: the string is an id of the sample image
      2. df: the DataFrame of Metatfile, as in the format of train.csv
    - Output:
      Plotted image with bbox of deceases
    """

    image = image.copy()

    try:
        original_size = original_df[original_df.image_id == img_id].values[0,-2:]
        bboxes = df.loc[df['image_id'] == img_id, ['x_min',	'y_min', 'x_max', 'y_max']].values
        bboxes = [list(_resize_read_xray(original_size, tuple(bbox), image.shape[:2])) for bbox in bboxes]
        class_names = df.loc[df['image_id'] == img_id, ['class_name']].values
    except:
        return None

    for box, class_name in zip(bboxes, class_names):
        cv2.rectangle(image, (box[0], box[1]), (box[2], box[3]), (0, 0, 255), 1)
        (text_width, text_height), _ = cv2.getTextSize(class_name[0], cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1)    
        cv2.rectangle(image, (box[0], box[1] - int(1.3 * text_height)), (box[0] + text_width, box[1]), (0, 0, 255), -1)
        cv2.putText(
            image,
            text=class_name[0],
            org=(box[0], box[1] - int(0.3 * text_height)),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.0, 
            color=(0, 0, 0), 
            lineType=cv2.LINE_AA,
        )

    label = "Ground Truth"
    (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1)    
    cv2.rectangle(image, (0, 0), (20 + text_width, 40), (0, 255, 0), -1)
    cv2.putText(
            image,
            text=label,
            org=(10, 30),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.0, 
            color=(0, 0, 0), 
            lineType=cv2.LINE_AA,
        )
    
    return image
    
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
    bboxes = [np.array(i) for i in list(outputs['instances'].pred_boxes.to('cpu'))]

    # Please notice the order of output
    class_names = [classes[i] for i in list(outputs['instances'].pred_classes.to('cpu'))]

    draw = cv2.resize(image, viz_size)
    x_scale = viz_size[0] / image.shape[1]
    y_scale = viz_size[1] / image.shape[0]
    for box, class_name in zip(bboxes, class_names):
        x1 = int(box[0] * x_scale)
        y1 = int(box[1] * y_scale)
        x2 = int(box[2] * x_scale)
        y2 = int(box[3] * y_scale)
        cv2.rectangle(draw, (x1, y1), (x2, y2), (0, 0, 255), 1)
        ((text_width, text_height), _) = cv2.getTextSize(class_name, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1)    
        cv2.rectangle(draw, (x1, y1 - int(1.3 * text_height)), (x1 + text_width, y1), (0, 0, 255), -1)
        cv2.putText(
            draw,
            text=class_name,
            org=(x1, y1 - int(0.3 * text_height)),
            fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            fontScale=1.0, 
            color=(0, 0, 0), 
            lineType=cv2.LINE_AA,
        )

    label = "Prediction"
    (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 1)    
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
    

