import os
import glob
from PIL import Image
import PIL

train_path = '/data/sat/msg/ml_train_crops/IR_108_2013_128x128_EXPATS/tif/'
train_cot_files = sorted(glob.glob(os.path.join(train_path,"*.tif")))

def file_detail(file_location):
    detail = file_location.split('/')[-1]
    return detail


for index,file in enumerate(train_cot_files):
    img = Image.open(file)
    if img.mode == 'RGB':
        img.close()
        print(file_detail(file)+ ' already RGB in training')
        print('index = ' + str(index))
        
    else:
        """
        Saves a rgb-a figure to given directory with rgb format.
        :return:
        """
        filename = file_detail(file)
        print(f'converting {filename} to RGB')
        rgba_image = PIL.Image.open(file)
        rgb_image = rgba_image.convert('RGB')
        rgb_image.save(file)
        rgb_image.close()
        print(filename+ ' converted to RGB in training')
        print('index = ' + str(index)) 

        #exit()