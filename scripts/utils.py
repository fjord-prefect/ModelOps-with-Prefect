from pycocotools.coco import COCO
from tqdm import tqdm
import os
import pylab
import numpy as np
import skimage.io as io
import shutil

def get_coco(path):
    if not os.path.isdir('local_feature_store/annotations'):
        os.mkdir('local_feature_store/annotations')
        os.system('wget {}'.format(path))
        shutil.move("annotations_trainval2017.zip", "local_feature_store/annotations")
        os.system('unzip local_feature_store/annotations/*.zip -d local_feature_store/')
        os.system('rm local_feature_store/annotations/*.zip')
    if not os.path.isdir('local_feature_store/data'):
        os.mkdir('local_feature_store/data')
        os.mkdir('local_feature_store/data/train')
        os.mkdir('local_feature_store/data/val')
    if not os.path.isdir('local_feature_store/validation'):
        os.mkdir('local_feature_store/validation')
        os.mkdir('local_feature_store/validation/model')
        os.mkdir('local_feature_store/validation/predictions')

    coco = {
        'train':COCO('./local_feature_store/annotations/instances_train2017.json'),
        'val':COCO('./local_feature_store/annotations/instances_val2017.json')
    }
    
    return coco

def transform_load(coco, trainOrVal):
    
    catIds = coco[trainOrVal].getCatIds(catNms=['dog']);
    
    imgIds = coco[trainOrVal].getImgIds(catIds=catIds);

    
    train_path = 'local_feature_store/data/{}.txt'.format(trainOrVal)
    anno_list = []
    with open(train_path, 'w') as writer:
        for id_ in tqdm(imgIds[0:3]):
            coco_data = coco[trainOrVal].loadImgs(id_)[0]
            coco_bbox = coco[trainOrVal].loadAnns(coco[trainOrVal].getAnnIds(id_, catIds=catIds, iscrowd=None))[0]['bbox']
            yolo_bbox = [coco_bbox[0], coco_bbox[1], coco_bbox[2] + coco_bbox[0], coco_bbox[3] + coco_bbox[1]]
            str_bbox = ','.join([str(round(i)) for i in yolo_bbox])
            pic = io.imread(coco_data['coco_url'])
            path = os.path.join('local_feature_store/data', trainOrVal, '{}.jpg'.format(str(id_)))
            anno = path + ' ' + str_bbox + ',0'
            io.imsave(path, pic)
            writer.write('%s\n' % anno)
            anno_list.append(anno)
    return anno_list
