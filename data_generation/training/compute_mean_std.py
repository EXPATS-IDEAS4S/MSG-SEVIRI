import numpy as np
import os
import glob
from PIL import Image
import torchvision.transforms as transforms
from math import sqrt
import random

train_path = '/work/dcorradi/crops/IR_108_2013-2014-2015-2016_200x200_EXPATS_fixed/CMA/closing/tif_200K-300K_greyscale/'
train_cot_files = glob.glob(os.path.join(train_path,"*.tif"))

RGB = False

x_pixels, y_pixels=200,200 

#initialize values for computing mean and std
r_channel ,r_total=0,0
g_channel, g_total=0,0
b_channel, b_total=0,0


transform = transforms.Compose([
    transforms.ToTensor()
])

train_cot_files1 = train_cot_files #random.sample(train_cot_files, 50000)

#compute iteritevely the mean
for file in train_cot_files1:
    img = Image.open(file)
    img_tr = transform(img)
    img_np = np.array(img_tr)
    #print(img_np.shape) # shape is (color channels, x, y) color channel is 1 for GS and 3 for RGB
    if RGB:
        r_channel = r_channel + np.sum(img_np[0,:,:])
        g_channel = g_channel + np.sum(img_np[1,:,:])
        b_channel = b_channel + np.sum(img_np[2,:,:])
    else:
        r_channel = r_channel + np.sum(img_np[0, :, :])


num = len(train_cot_files1) * x_pixels * y_pixels

r_mean = r_channel/num
g_mean = g_channel/num
b_mean = b_channel/num

#compute std
for file in train_cot_files1:
    img = Image.open(file)
    img_tr = transform(img)
    img_np = np.array(img_tr)
    #print(img_np)
    if RGB:
        r_total = r_total + np.sum((img_np[0, :, :] - r_mean) ** 2)
        g_total = g_total + np.sum((img_np[1, :, :] - g_mean) ** 2)
        b_total = b_total + np.sum((img_np[2, :, :] - b_mean) ** 2)
    else:
        r_total = r_total + np.sum((img_np[0, :, :] - r_mean) ** 2)

    
R_std = sqrt(r_total / num)
G_std = sqrt(g_total / num)
B_std = sqrt(b_total / num)

print('mean of image intensity is - ' + str(r_mean),str(g_mean),str(b_mean))

print('')
print('std of image intensity is - ' + str(R_std),str(G_std),str(B_std))
print('')

np.save(f'{train_path}mean.npy', np.array([r_mean,g_mean,b_mean]))
np.save(f'{train_path}std.npy', np.array([R_std,G_std,B_std]))



#mean of image intensity is - 0.24566070109766777 0.0 0.0

#std of image intensity is - 0.2668053317096114 0.0 0.0