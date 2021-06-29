import os,re
from tqdm import tqdm
from prefect import task, Flow, Parameter
from prefect.storage import Docker
from prefect.triggers import always_run

from prefect.tasks.shell import ShellTask
from prefect.engine.results import LocalResult

@task
def extract(path):
    from scripts.utils import get_coco
    coco = get_coco(path)
    return coco

@task
def train_imgs_extract(coco):
    from scripts.utils import transform_load
    transform_load(coco, 'train')
    return None

@task
def val_imgs_extract(coco):
    from scripts.utils import transform_load
    transform_load(coco, 'val')
    return None

@task
def val_imgs_transform():
    from dog.dataset import Dataset
    return Dataset('test')

@task
def train_imgs_transform():
    from dog.dataset import Dataset
    return Dataset('train')

@task
def TESTING_annos(dataset):
    from dog.configs import FEATURE_STORE_PATH
    assert dataset.annot_path.split('/')[0]==FEATURE_STORE_PATH
    annos = [re.sub('\n','', i) for i in open(dataset.annot_path).readlines()]
    
    img_dir = dataset.annot_path.split('.')[0]
    imgs = os.listdir(img_dir)
    assert len(annos)==len(imgs)
    return dataset

@task
def submit_trainval(dataset):
    import pickle
    trainval = dataset.annot_path.split('.')[0].split('/')[-1]
    pickle.dump(trainval, open(f'/home/volume/{trainval}_dataobject.pkl', 'wb'))
    return None

@task
def submit_to_feature_store():
    os.system('cp -avr /home/local_feature_store/. /home/volume/.')
    return None
@task
def train(trainset, testset):
    import dog.train as dog_model
    model = dog_model.train(trainset, testset)
    return model

@task
def validate(testset):
    from dog.yolov3 import Create_Yolov3
    from dog.evaluate_mAP import get_mAP
    from dog.configs import TEST_SCORE_THRESHOLD, TEST_IOU_THRESHOLD, YOLO_INPUT_SIZE, TRAIN_CLASSES
    from dog.configs import TRAIN_CHECKPOINTS_FOLDER, TRAIN_MODEL_NAME, TRAIN_FROM_CHECKPOINT
    
    model_candidate = Create_Yolov3(input_size=YOLO_INPUT_SIZE, CLASSES=TRAIN_CLASSES)
    model_candidate.load_weights(os.path.join(TRAIN_CHECKPOINTS_FOLDER, TRAIN_MODEL_NAME))
    
    mAP = get_mAP(model_candidate, testset, score_threshold=TEST_SCORE_THRESHOLD, iou_threshold=TEST_IOU_THRESHOLD)

    from dog.utils import detect_image
    from tensorflow.keras.preprocessing.image import array_to_img, save_img

    val_imgs_path = testset.annot_path.split('.')[0]
    
    for val_img in tqdm(os.listdir(val_imgs_path)):
        print(os.path.join(val_imgs_path,val_img))
        prediction_array = detect_image(model_candidate, image_path=os.path.join(val_imgs_path,val_img), 
                         output_path='local_feature_store/validation/predictions/{}'.format(val_img), 
                         input_size=YOLO_INPUT_SIZE, 
                         show=False, 
                         CLASSES=TRAIN_CLASSES, 
                         score_threshold=TEST_SCORE_THRESHOLD, 
                         iou_threshold=TEST_IOU_THRESHOLD, 
                         rectangle_colors='')

    return model_candidate

@task
def submit_data_to_volume():
    response = os.system('cp -avr /home/local_feature_store/. /home/volume/.')

    try:
        assert response == 0
    except AssertionError as e: 
        e.args += f'error code: {response} failed to copy /home/local_feature_store/. to /home/volume/.'
        raise
    return None

@task
def submit_model_to_registry(model_candidate, relax_submit=False):
    from dog.yolov3 import Create_Yolov3
    from dog.configs import YOLO_INPUT_SIZE, TRAIN_CLASSES, TRAIN_MODEL_NAME, TRAIN_FROM_CHECKPOINT
    
    existing_model = Create_Yolov3(input_size=YOLO_INPUT_SIZE, CLASSES=TRAIN_CLASSES)
    existing_model.load_weights(os.path.join(TRAIN_FROM_CHECKPOINT))

    existing_loss = sum(existing_model.losses).numpy()
    candidate_loss = sum(model_candidate.losses).numpy()
    
    if relax_submit:
        model_candidate.save_weights('local_feature_store/validation/model/{}'.format(TRAIN_MODEL_NAME))
        return None
    else:
        try:
            assert existing_loss > candidate_loss
        except AssertionError as e:
            message = 'existing_model total loss ({}) is less than model candidate loss ({})'
            e.args += (message.format(existing_loss,candidate_loss))
            raise
        model_candidate.save_weights('local_feature_store/validation/model/{}'.format(TRAIN_MODEL_NAME))
    return None
    
def build_flow():
    with Flow("docker-flow", storage = Docker(base_image="fjord_prefect:1", local_image=True)) as flow:
        
        path = 'http://images.cocodataset.org/annotations/annotations_trainval2017.zip'
        
        coco = extract(path)
        
        extracted_train = train_imgs_extract(coco)
        extracted_val = val_imgs_extract(coco)
        
        trainset = train_imgs_transform.set_upstream(extracted_train)
        testset = val_imgs_transform.set_upstream(extracted_val)

        trainset = TESTING_annos(trainset)
        testset = TESTING_annos(testset)
       
        submit_trainval(trainset)
        submit_trainval(testset)

        train_model = train(trainset, testset)

        validated_train_model = validate(testset).set_upstream(train_model)
        submit_data_to_volume().set_upstream(validated_train_model)
        submit_model_to_registry(validated_train_model, relax_submit=True)
        
    return flow

flow = build_flow()

flow.register('monster_mash', labels=['feature_store'])
