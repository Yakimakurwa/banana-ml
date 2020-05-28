# -*- coding: utf-8 -*-
"""Deep_dream_bot.py

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1OiGn1c_NbHWv1FXmTXDSUL2rOmzIXDkV
"""

# Commented out IPython magic to ensure Python compatibility.
import torch
import matplotlib.pyplot as plt
from skimage.transform import resize
# %matplotlib inline
from PIL import Image, ImageFilter, ImageChops
from torchvision import transforms
import numpy as np
from skimage.io import imread
import skimage

import requests

# class labels
LABELS_URL = 'https://s3.amazonaws.com/outcome-blog/imagenet/labels.json'
labels = {int(key):value for (key, value) in requests.get(LABELS_URL).json().items()}
print('--------------------------labels----------------------------')
from torchvision.models.inception import inception_v3

preprocess = transforms.Compose([transforms.ToTensor()])
    
class Predictor:
    def __init__(self, path='deep_dream_model'):
        self.model = self.model = inception_v3(pretrained=True, transform_input=True)
        self.model.aux_logits = False
        self.model.train(False)
        self.modulelist = list(self.model.children())
        print('-----------------------------------init--------------------------------------------')

    def dd_helper(self, image, layer, iterations, lr):
        input_var = torch.tensor(preprocess(image).unsqueeze(0), requires_grad=True,
                             dtype=torch.float32)
        self.model.zero_grad()
        for i in range(iterations):
            out = input_var
            for j in range(layer):
                out = self.modulelist[j](out)
            #out = out[:, index]
            loss = out.norm()
            loss.backward()
            input_var.data = input_var.data + lr * input_var.grad.data

        input_im = input_var.data.squeeze(0).cpu()
        input_im.transpose_(0, 1)
        input_im.transpose_(1, 2)
        input_im = np.clip(input_im, 0, 1)
        im = Image.fromarray(np.uint8(input_im * 255))
        return im

    def deep_dream(self, image, layer, iterations, lr, octave_scale, num_octaves):
        if num_octaves>0:
            image1 = image.filter(ImageFilter.GaussianBlur(2))
            if (image1.size[0] / octave_scale < 1 or image1.size[1] / octave_scale < 1):
                size = image1.size
            else:
                size = (int(image1.size[0] / octave_scale), int(image1.size[1] / octave_scale))
            
            image1 = image1.resize(size, Image.ANTIALIAS)
            image1 = self.deep_dream(image1, layer, iterations, lr, octave_scale, num_octaves-1)
            print('--------------------------------------------second deeam-----------------------------------')
            size = (image.size[0], image.size[1])
            image1 = image1.resize(size, Image.ANTIALIAS)
            image = ImageChops.blend(image, image1, 0.6)
        print("-------------- Recursive level: ", num_octaves, '--------------')
        img_result = self.dd_helper(image, layer, iterations, lr)
        img_result = img_result.resize(image.size)
        return img_result

    def get_image_predict(self, img_path='img_path.jpg'):
        print('--------------------------------------------got image----------------------------')
        image = Image.open(img_path).convert('RGB').resize((512, 512), Image.ANTIALIAS)
        result = self.deep_dream(image, 14, 5, 0.3, 2, 2)
        print('-------------------------------------------first dream-------------------------------------')
        #result = Image.fromarray(result)
        #print('------------------------------------------------got result-------------------------------------------')
        result.save('result.jpg')
        print('---------------------------------------------------------result saved-----------------------------------------------')
