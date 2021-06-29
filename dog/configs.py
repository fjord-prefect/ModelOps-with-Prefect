# YOLO options
YOLO_TYPE                   = "yolov3" # yolov4 or yolov3
YOLO_FRAMEWORK              = "tf" # "tf" or "trt"
YOLO_V3_WEIGHTS             = "not used"
YOLO_STRIDES                = [8, 16, 32]
YOLO_IOU_LOSS_THRESH        = 0.5
YOLO_ANCHOR_PER_SCALE       = 3
YOLO_MAX_BBOX_PER_SCALE     = 100
YOLO_INPUT_SIZE             = 608
if YOLO_TYPE                == "yolov3":
    YOLO_ANCHORS            = [[[10,  13], [16,   30], [33,   23]],
                               [[30,  61], [62,   45], [59,  119]],
                               [[116, 90], [156, 198], [373, 326]]]
# Train options
TRAIN_YOLO_TINY             = False
TRAIN_SAVE_BEST_ONLY        = True # saves only best model according validation loss (True recommended)
TRAIN_SAVE_CHECKPOINT       = False # saves all best validated checkpoints in training process (may require a lot disk space) (False recommended)
FEATURE_STORE_PATH          = "local_feature_store"
TRAIN_CLASSES               = "dog/model_data/box_classes.txt"
TRAIN_ANNOT_PATH            = "local_feature_store/data/train.txt"
TRAIN_LOGDIR                = "dog/log"
TRAIN_CHECKPOINTS_FOLDER    = "dog/checkpoints"
TRAIN_MODEL_NAME            = "yolov3_custom"
TRAIN_LOAD_IMAGES_TO_RAM    = True # With True faster training, but need more RAM
TRAIN_BATCH_SIZE            = 1
TRAIN_INPUT_SIZE            = 608
TRAIN_DATA_AUG              = True
TRAIN_TRANSFER              = False # Start with DarkNet Weights
TRAIN_FROM_CHECKPOINT       = "dog/checkpoints/dogfinder"
TRAIN_LR_INIT               = 1e-4
TRAIN_LR_END                = 1e-6
TRAIN_WARMUP_EPOCHS         = 0
TRAIN_EPOCHS                = 2

# TEST options
TEST_ANNOT_PATH             = "local_feature_store/data/val.txt"
TEST_BATCH_SIZE             = 1
TEST_INPUT_SIZE             = 608
TEST_DATA_AUG               = False
TEST_DECTECTED_IMAGE_PATH   = ""
TEST_SCORE_THRESHOLD        = 0.3
TEST_IOU_THRESHOLD          = 0.45
