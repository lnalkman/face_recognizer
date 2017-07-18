# -*- coding: utf-8 -*-

import os
import shelve
import datetime
from PyQt4 import QtCore
from tools.parser import parse_settings
from recognizer import FaceRecognizer


class RecognitionController(QtCore.QThread, FaceRecognizer):
    """
    Class bind the recognizer to the graphical interface.
    Show some recognition data in GUI.
    """
    def __init__(self, window=None):
        QtCore.QThread.__init__(self)
        FaceRecognizer.__init__(
            self,
            faceCascade=os.path.abspath('tools/haarcascade_frontalface_default.xml'),
            forRecognitionPhotoDir=os.path.abspath('photo'),
            trainPhotoDir=os.path.abspath('../Release/Photoes/IS-62'),
            **parse_settings('tools/settings.xml')
            )

        self.relations = shelve.open('tools/relation.dbm')
        self.finded = list()
        self.Window = window

        # self.train()
        # self.start_recognition()


    def recognitionDataHandler(self, numPredicted, coef, faceNum, faceCount, imagePath):
        if faceNum == faceCount:
            os.remove(imagePath)
        numPredicted = str(numPredicted)

        if numPredicted not in self.finded and self.relations.has_key(numPredicted):
            self.finded.append(numPredicted)
            self.Window.findedStudents.addStudent(fullName=self.relations[numPredicted],
                                                  date="{:0>4}-{:0>2}-{:0>2} {:0>2}:{:0>2}".format(
                                                    *datetime.datetime.now().timetuple()
                                                    ),
                                                  k=int(coef))

            self.emit(QtCore.SIGNAL('setNewImage'),
                      self.getImagePathByNumber(numPredicted)
                      )


    def stopCondition(self, *args):
        return False


    def getImagePathByNumber(self, number):
        """
        Returns the absolute path to the first photo in the folder
        of the specified person's number.
        """
        path = os.path.join(self.photoDir,
                            'id{:0>3}'.format(number)
                            )
        path = os.path.abspath(path)
        return os.path.join(path, os.listdir(path)[0])


    def run(self):
        self.Window.connect(self,
                            QtCore.SIGNAL('setNewImage'),
                            self.Window.setImage
                            )
        self.train()
        self.start_recognition()
