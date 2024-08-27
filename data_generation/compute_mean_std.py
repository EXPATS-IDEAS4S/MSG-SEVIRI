import numpy as np
import os
import glob
from PIL import Image
import torchvision.transforms as transforms
from math import sqrt
import random

train_path = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/tif_25th-75th/'
train_cot_files = glob.glob(os.path.join(train_path,"*.tif"))

x_pixels, y_pixels=128,128 

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
    r_channel = r_channel + np.sum(img_np[:,:,0])
    g_channel = g_channel + np.sum(img_np[:,:,1])
    b_channel = b_channel + np.sum(img_np[:,:,2])


num = len(train_cot_files1) * x_pixels * y_pixels

r_mean = r_channel/num
g_mean = g_channel/num
b_mean = b_channel/num

#compute std
for file in train_cot_files1:
    img = Image.open(file)
    img_tr = transform(img)
    img_np = np.array(img_tr)
    r_total = r_total + np.sum((img_np[:, :, 0] - r_mean) ** 2)
    g_total = g_total + np.sum((img_np[:, :, 1] - g_mean) ** 2)
    b_total = b_total + np.sum((img_np[:, :, 2] - b_mean) ** 2)

    
R_std = sqrt(r_total / num)
G_std = sqrt(g_total / num)
B_std = sqrt(b_total / num)

print('mean of RGB is - ' + str(r_mean),str(g_mean),str(b_mean))

print('')
print('std of RGB is - ' + str(R_std),str(G_std),str(B_std))
print('')

np.save(f'{train_path}mean.npy', np.array([r_mean,g_mean,b_mean]))
np.save(f'{train_path}std.npy', np.array([R_std,G_std,B_std]))