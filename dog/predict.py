#!/usr/bin/env python

import os
from yolov3.utils import *

def predict_out_val():
    yolo = Create_Yolov3(input_size=YOLO_INPUT_SIZE, CLASSES="model_data/box_classes.txt")
    yolo.load_weights("checkpoints/yolov3_custom") # use custom weights
    
    for i in os.listdir('data/val'): 
        path = os.path.join('data/val',i)
        out_path = os.path.join('out',i)
        detect_image(yolo, path, output_path=out_path, input_size=608, show=False, CLASSES=TRAIN_CLASSES, score_threshold=0.3, iou_threshold=0.45, rectangle_colors='')
    return None

predict_out_val()
