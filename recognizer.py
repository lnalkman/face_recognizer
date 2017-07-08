# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import re
import sys
import time
import shutil
import datetime
from tools import cv2
import numpy as np
from PIL import Image

class FaceRecognizer(object):
    """
    Recognize faces in photos and send recognition data to
    dataHandle which can be overwriten.
    By default all persons labeled by number in the end of folder where stored
    photo for training.
    """

    def __init__(self, notRecognizedDir=None, notSureRecognizedDir=None,
                 forRecognitionPhotoDir=None, trainPhotoDir=None,
                 faceCascade=None, maxCoefficient=60, minSize=(60, 60),
                 formats=[]):
        self.notRecognizedDir = notRecognizedDir
        self.notSureRecognizedDir = notSureRecognizedDir
        self.photoDir = trainPhotoDir#CHECK
        self.unknownPhotoDir = forRecognitionPhotoDir
        self.coef = maxCoefficient#CHECK
        self.formats = formats#CHECK
        self.minSize = minSize
        if isinstance(faceCascade, str):
            self.faceCascade = cv2.CascadeClassifier(os.path.abspath(faceCascade))
        else:
            self.faceCascade = faceCascade#CHECK

        # Check main variables    
        def __check():
            assert self.faceCascade.empty()
            assert os.path.isdir(self.photoDir)
            assert os.path.isdir(self.unknownPhotoDir)
            if self.notRecognizedDir:
                assert os.path.isdir(self.notRecognizedDir)
            if self.notSureRecognizedDir:
                assert os.path.isdir(self.notSureRecognizedDir)
            assert [x for x in formats if isinstance(x, str)]
            assert maxCoefficient
            assert len(minSize) == 2
        __check()


    def _training(self):
        pass


    def getFaces(self, photoPath):
        """
        Get all faces from photo and gives subject_number from
        self.getSubjectNumber method for all faces.
        """
        images, labels = [], []
        try:
            gray = Image.open(photoPath)
        except IOError:
            return None # [], [] ?
        subject_number = self.getSubjectNumber(photoPath)
        image = np.array(gray, 'uint8')
        faces = self.faceCascade.detectMultiScale(
                    image,
                    scaleFactor=1.1,
                    minNeighbors=3,
                    minSize=self.minSize)
        for (x, y, w, h) in faces:
            images.append(image[y: y + h, x: x + w])
            labels.append(subject_number)
        return images, labels


    # Can be overwriten
    def getSubjectNumber(self, path):
        num = re.search(r'(\d+)$', os.path.split(path)[0])
        return int(num.group()) if num else None


    # Can be overwriten
    def getTrainImages(self):
        """
        Get all images in self.photoDir folders for training, not photo files ignore.
        """
        images = []
        labels = []
        # Get all folders in self.photoDir
        folders = filter(
            os.path.isdir,
            [os.path.join(self.photoDir, f) for f in os.listdir(self.photoDir)]
            )

        for folder in folders:
            for photo in os.listdir(folder):
                images_and_labels = self.getFaces(os.path.join(folder, photo))
                if images_and_labels:
                    images += images_and_labels[0]
                    labels += images_and_labels[1]

        return images, labels


    def start_recognition(self, data=None, dataHandler=None):
        pass
