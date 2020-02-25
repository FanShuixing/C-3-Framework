import numpy as np
import os
import random
from scipy import io as sio
import sys
import torch
from torch.utils import data
from PIL import Image, ImageOps

import pandas as pd
import re

from config import cfg


class SHHB(data.Dataset):
    def __init__(self, data_path, mode, main_transform=None, img_transform=None, gt_transform=None):
        self.img_path = data_path + '/images'
        if mode == 'train':
            self.gt_path = data_path + '/npy_sigma8.0'
            self.gt_txt = data_path + '/train.txt'
        else:
            self.gt_path = data_path + '/npy_sigma8.0'
            self.gt_txt = data_path + '/val.txt'
        with open(self.gt_txt) as fr:
            self.data_files = [re.sub('.csv', '.jpg', filename.strip()) for filename in fr.readlines()]

        self.num_samples = len(self.data_files)
        self.main_transform = main_transform
        self.img_transform = img_transform
        self.gt_transform = gt_transform

    def __getitem__(self, index):
        fname = self.data_files[index]
        img, den = self.read_image_and_gt(fname)
        if self.main_transform is not None:
            img, den = self.main_transform(img, den)
        if self.img_transform is not None:
            img = self.img_transform(img)
        if self.gt_transform is not None:
            den = self.gt_transform(den)
        return img, den

    def __len__(self):
        return self.num_samples

    def read_image_and_gt(self, fname):
        img = Image.open(os.path.join(self.img_path, fname+'.jpg'))
        if img.mode == 'L':
            img = img.convert('RGB')
        img = img.resize((768, 576))
        # den = sio.loadmat(os.path.join(self.gt_path,os.path.splitext(fname)[0] + '.mat'))
        # den = den['map']
        # den = pd.read_csv(os.path.join(self.gt_path, os.path.splitext(fname)[0] + '.csv'), sep=',', header=None).values
        den = np.load(os.path.join(self.gt_path, fname + '.npy'))

        den = den.astype(np.float32, copy=False)
        den = Image.fromarray(den)
        return img, den

    def get_num_samples(self):
        return self.num_samples

