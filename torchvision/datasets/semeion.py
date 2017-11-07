from __future__ import print_function
from PIL import Image
import os
import os.path
import errno
import numpy as np
import sys
if sys.version_info[0] == 2:
    import cPickle as pickle
else:
    import pickle

import torch.utils.data as data
from .utils import download_url, check_integrity


class SEMEION(data.Dataset):
    """`SEMEION <http://archive.ics.uci.edu/ml/datasets/semeion+handwritten+digit>`_ Dataset.
    Args:
        root (string): Root directory of dataset where directory
            ``semeion.py`` exists.
        transform (callable, optional): A function/transform that  takes in an PIL image
            and returns a transformed version. E.g, ``transforms.RandomCrop``
        target_transform (callable, optional): A function/transform that takes in the
            target and transforms it.
        download (bool, optional): If true, downloads the dataset from the internet and
            puts it in root directory. If dataset is already downloaded, it is not
            downloaded again.
    """
    url = "http://archive.ics.uci.edu/ml/machine-learning-databases/semeion/semeion.data"
    filename = "semeion.data"
    md5_checksum = 'cb545d371d2ce14ec121470795a77432'

    def __init__(self, root, transform=None, target_transform=None, download=True):
        self.root = os.path.expanduser(root)
        self.transform = transform
        self.target_transform = target_transform

        if download:
            self.download()

        if not self._check_integrity():
            raise RuntimeError('Dataset not found or corrupted.' +
                               ' You can use download=True to download it')

        self.data = []
        self.labels = []
        fp = os.path.join(root, self.filename)
        file = open(fp, 'r')
        data = file.read()
        file.close()
        dataSplitted = data.split("\n")[:-1]
        datasetLength = len(dataSplitted)
        i = 0
        while i < datasetLength:
            # Get the 'i-th' row
            strings = dataSplitted[i]

            # Split row into numbers(string), and avoid blank at the end
            stringsSplitted = (strings[:-1]).split(" ")

            # Get data (which ends at column 256th), then in a numpy array.
            rawData = stringsSplitted[:256]
            dataFloat = [float(j) for j in rawData]
            img = np.array(dataFloat[:16])
            j = 16
            k = 0
            while j < len(dataFloat):
                temp = np.array(dataFloat[k:j])
                img = np.vstack((img, temp))

                k = j
                j += 16

            self.data.append(img)

            # Get label and convert it into numbers, then in a numpy array.
            labelString = stringsSplitted[256:]
            labelInt = [int(index) for index in labelString]
            self.labels.append(np.array(labelInt))
            i += 1

    def __getitem__(self, index):
        """
        Args:
            index (int): Index
        Returns:
            tuple: (image, target) where target is index of the target class.
        """
        img, target = self.data[index], self.labels[index]

        # doing this so that it is consistent with all other datasets
        # to return a PIL Image
        # convert value to 8 bit unsigned integer
        # color (white #255) the pixels
        img = img.astype('uint8') * 255
        img = Image.fromarray(img, mode='L')

        if self.transform is not None:
            img = self.transform(img)

        if self.target_transform is not None:
            target = self.target_transform(target)

        return img, target

    def __len__(self):
        return len(self.data)

    def _check_integrity(self):
        root = self.root
        fpath = os.path.join(root, self.filename)
        if not check_integrity(fpath, self.md5_checksum):
            return False
        return True

    def download(self):
        if self._check_integrity():
            print('Files already downloaded and verified')
            return

        root = self.root
        download_url(self.url, root, self.filename, self.md5_checksum)