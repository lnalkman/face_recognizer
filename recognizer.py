# -*- coding: utf-8 -*-

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
                 maxSize=(720, 480), formats=[], **kwargs):
        self.notRecognizedDir = notRecognizedDir if os.path.isdir(unicode(notRecognizedDir)) else None
        self.notSureRecognizedDir = notSureRecognizedDir if os.path.isdir(unicode(notSureRecognizedDir)) else None
        self.photoDir = trainPhotoDir if os.path.isdir(unicode(trainPhotoDir)) else None
        self.unknownPhotoDir = forRecognitionPhotoDir if os.path.isdir(unicode(forRecognitionPhotoDir)) else None
        try:
            self.coef = maxCoefficient
        except TypeError:
            self.coef = 60
            sys.stderr.write('warning: maxCoefficient can\'t be converted to int\n')

        self.formats = formats

        try:
            self.minSize = tuple(minSize)
        except TypeError:
            self.minSize = (60, 60)
            sys.stderr.write('warning: minSize is not specified, or it has invalid format\n')

        try:
            self.maxSize = tuple(maxSize)
        except TypeError:
            self.maxSize = (60, 60)
            sys.stderr.write('warning: maxSize is not specified, or it has invalid format\n')

        if isinstance(faceCascade, str):
            self.faceCascade = cv2.CascadeClassifier(os.path.abspath(faceCascade))
        elif isinstance(faceCascade, cv2.CascadeClassifier):
            self.faceCascade = faceCascade
        if self.faceCascade.empty():
            sys.stderr.write('WARNING: face cascade empty.\n')

        self.recognizer = None

    def train(self):
        if self.faceCascade.empty(): return False

        images_and_labels = self.getTrainImages()
        if all(images_and_labels):
            self.recognizer = cv2.createLBPHFaceRecognizer(1,8,8,8,123)
            self.recognizer.train(images_and_labels[0], np.array(images_and_labels[1]))
            return True


    def getFaces(self, photoPath, Images=True, Labels=True):
        """
        Get all faces from photo and gives subject_number from
        self.getSubjectNumber method for all faces.
        """
        if not Images and not Labels: return None
        images, labels = [], []
        try:
            gray = Image.open(photoPath).convert('L')
        except IOError:
            return None # [], [] ?
        if Labels:
            subject_number = self.getSubjectNumber(photoPath)
        image = np.array(gray, 'uint8')
        faces = self.faceCascade.detectMultiScale(
                    image,
                    scaleFactor=1.1,
                    minNeighbors=3,
                    minSize=self.minSize)
        for (x, y, w, h) in faces:
            if Images:
                images.append(image[y: y + h, x: x + w])
            if Labels:
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
        if not self.photoDir: return images, labels

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


    def recognitionDataHandler(self, *args, **kwargs):
        pass


    def stopCondition(self, iteration=None, *args, **kwargs):
        if iteration == 10:
            return True

    def checkFormat(self, imagePath):
        """
        Return True if imagePath image format in self.formats
        else False
        """
        format = re.search(r"\.(\w+)[/\\]*$", imagePath)
        if format and format.groups(0)[0] in self.formats:
            return True
        return False


    def recognizeImage(self, imagePath):
        """
        Recognize all faces in image imagePath, ALL recognition data
        sends in method recognitionDataHandler
        """
        try:
            gray = Image.open(imagePath).convert('L')
        except IOError:
            return None
        image = np.array(gray, 'uint8')
        faces = self.faceCascade.detectMultiScale(
                    image,
                    scaleFactor=1.1,
                    minNeighbors=3,
                    minSize=self.minSize)

        facesCount = len(faces)
        if not facesCount: self.recognitionDataHandler(numPredicted=None,
                                    coef=None,
                                    imagePath=imagePath,
                                    faceNum=None,
                                    faceCount=None)

        for n, (x, y, w, h) in enumerate(faces, 1):
            number_predicted, coef = self.recognizer.predict(image[y: y + h, x: x + w])
            self.recognitionDataHandler(numPredicted=number_predicted,
                                        coef=coef,
                                        imagePath=imagePath,
                                        faceNum=n,
                                        faceCount=facesCount)


    def start_recognition(self):
        if not self.recognizer and not self.train():
            sys.stderr.write("WARNING: recognition can't be started, recognizer is not assigned\n")
            return None

        i = 0
        while True:
            images = [
                os.path.join(self.unknownPhotoDir, image)
                for image in os.listdir(self.unknownPhotoDir)
                ]
            images = filter(self.checkFormat, images)

            for path in images:
                i += 1
                self.recognizeImage(path)

                if self.stopCondition(i):
                    return None
