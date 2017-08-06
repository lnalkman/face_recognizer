# -*- coding: utf-8 -*-

import os
import sys
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
            trainPhotoDir=os.path.abspath('../Release/Photoes'),
            **parse_settings('tools/settings.xml')
            )

        self.internalRelations = shelve.open('tools/bd.dbm')
        self.finded = list()
        self.Window = window

        # self.relation[subject_number] = "subject_group/subject_folder"
        self.relation = []
        ### # For Test
        self.groups = ["IS-62"]
        ###


    def getTrainImages(self):
        """
        Get all images in self.photoDir folders which in self.groups list.
        """
        images, labels = [], []
        # Group folders that are written in self.folders
        groupFolders = []
        try:
            dirs = os.listdir(self.photoDir)
        except WindowsError as e:
            sys.stderr.write("\n===\n%s\n===\n" % e)
            return images, labels
        for group in self.groups:
            if group in dirs:
                folder = os.path.join(self.photoDir, group)
                groupFolders.append(folder)
                # If group folder exist, write it in statistics
                self.Window.stat.emit(QtCore.SIGNAL('setGroups'), '', group)
            else:
                sys.stderr.write("\n===\nWarning: Can't find %s group folder\n===\n" % group)

        for group in groupFolders:
            for person in os.listdir(group):
                personFolder = os.path.join(group, person)
                if os.path.isdir(personFolder):
                    subject_number = self.getTempSubjectNumber(personFolder)
                    for photo in os.listdir(personFolder):
                        images_and_labels = self.getFaces(os.path.join(personFolder, photo), Labels=False)
                        if images_and_labels:
                            images += images_and_labels[0]
                            labels += [subject_number]
        if self.stat:
            self.Window.stat.emit(QtCore.SIGNAL('setNumericField'), 1, len(self.relation))
            self.Window.stat.emit(QtCore.SIGNAL('setNumericField'), 2, len(images))

        return images, labels


    def getTempSubjectNumber(self, path):
        """
        Add new subject in self.relation and return his number.
        """
        path = os.path.split(path)
        self.relation.append(
            os.path.join(os.path.split(path[0])[1], path[1])
        )

        return len(self.relation) - 1


    def getSubjectInfo(self, number):

        info = {'full_name': None,
                'group': None,
                'folder': None,
                'images_path': None,
                }
        if not number: return info
        number = int(number)


        info['group'], info['folder'] = os.path.split(self.relation[number])
        info['images_path'] = os.path.join(self.photoDir, self.relation[number])
        info['full_name'] = self.internalRelations[info['group']][info['folder']]

        return info


    def recognitionDataHandler(self, numPredicted, coef, faceNum, faceCount, imagePath):
        if faceNum == faceCount:
            os.remove(imagePath)
        numPredicted = str(numPredicted)
        if self.stat:
            self.Window.stat.emit(QtCore.SIGNAL('setNumericField'), 4, 0, 1)

        if numPredicted not in self.finded:
            subjInfo = self.showStudent(numPredicted)
            self.finded.append(numPredicted)
            self.Window.findedStudents.addStudent(fullName=subjInfo['full_name'],
                                                  date="{:0>4}-{:0>2}-{:0>2} {:0>2}:{:0>2}".format(
                                                    *datetime.datetime.now().timetuple()
                                                    ),
                                                  k=int(coef),
                                                  metadata=numPredicted
                                                  )
            if self.stat:
                self.Window.stat.emit(QtCore.SIGNAL('setNumericField'), 5, 0, 1)
        elif numPredicted == -1:
            self.Window.stat.emit(QtCore.SIGNAL('setNumericField'), 6, 0, 1)            


    def showStudent(self, numPredicted):
        subjInfo = self.getSubjectInfo(numPredicted)
        self.Window.emit(QtCore.SIGNAL('showStudent'),
                  subjInfo
                  )

        return subjInfo


    def stopCondition(self, *args):
        return False


    def run(self):
        self.connect(self.Window,
                     QtCore.SIGNAL('showStudent'),
                     self.Window.showStudent
                     )
        if (self.connect(self.Window.stat,
                     QtCore.SIGNAL('setGroups'),
                     self.Window.stat.setGroups
                     )
            and
            self.connect(self.Window.stat,
                         QtCore.SIGNAL('setNumericField'),
                         self.Window.stat.setNumericField
                         )
            ):
            self.stat = True
        else:
            self.stat = False


        self.Window.statusBar.showMessage(u'Тренування')
        self.train()
        if self.recognizer:
            self.Window.statusBar.showMessage(u'Готово')
            self.start_recognition()
        else:
            self.Window.statusBar.showMessage(u'Тренування не вдалось')
