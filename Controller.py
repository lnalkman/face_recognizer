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
        parsedSettings = parse_settings('tools/settings.xml')
        QtCore.QThread.__init__(self)
        FaceRecognizer.__init__(
            self,
            faceCascade=os.path.abspath('tools/haarcascade_frontalface_default.xml'),
            forRecognitionPhotoDir=os.path.abspath('photo'),
            trainPhotoDir=os.path.abspath('../Release/Photoes'),
            **parsedSettings
            )

        self.internalRelations = shelve.open('tools/bd.dbm')
        self.finded = list()
        self.Window = window

        # self.relation[subject_number] = "subject_group/subject_folder"
        self.relation = []

        self.groups = parsedSettings.get('groups') or []
        if not self.groups:
            sys.stderr.write('WARNING: groups list is empty\n')


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
                if self.stat:
                    self.Window.stat.emit(QtCore.SIGNAL('setTextField'), '', group, 1)
            else:
                sys.stderr.write("\n===\nWarning: Can't find %s group folder\n===\n" % group)

        for group in groupFolders:
            for person in os.listdir(group):
                personFolder = os.path.join(group, person)
                if os.path.isdir(personFolder):
                    subject_number = self.getTempSubjectNumber(personFolder)
                    if self.stat:
                        self.Window.stat.emit(QtCore.SIGNAL('setNumericField'), 2, 0, 1)
                    for photo in os.listdir(personFolder):
                        images_and_labels = self.getFaces(os.path.join(personFolder, photo), Labels=False)
                        if images_and_labels:
                            if self.stat:
                                self.Window.stat.emit(QtCore.SIGNAL('setNumericField'), 3, 0, 1)
                            images += images_and_labels[0]
                            labels += [subject_number]
        # if self.stat:
        #     self.Window.stat.emit(QtCore.SIGNAL('setNumericField'), 2, len(self.relation))
        #     self.Window.stat.emit(QtCore.SIGNAL('setNumericField'), 3, len(images))
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
        if not isinstance(number, int): return info

        info['group'], info['folder'] = os.path.split(self.relation[number])
        info['images_path'] = os.path.join(self.photoDir, self.relation[number])
        info['full_name'] = self.internalRelations[info['group']][info['folder']]

        return info


    def recognitionDataHandler(self, numPredicted, coef, faceNum, faceCount, imagePath):
        if faceNum == faceCount:
            os.remove(imagePath)
        numPredicted = numPredicted if isinstance(numPredicted, int) else None

        if self.stat:
            self.Window.stat.emit(QtCore.SIGNAL('setNumericField'), 5, 0, 1)

        if numPredicted != None and numPredicted not in self.finded and coef < self.coef:
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
                self.Window.stat.emit(QtCore.SIGNAL('setNumericField'), 6, 0, 1)
        elif self.stat:
            self.Window.stat.emit(QtCore.SIGNAL('setNumericField'), 7, 0, 1)


    def showStudent(self, numPredicted):
        subjInfo = self.getSubjectInfo(numPredicted)
        self.Window.emit(QtCore.SIGNAL('showStudent'),
                  subjInfo
                  )

        return subjInfo


    def showSettings(self):
        if not self.stat: return None
        self.Window.stat.emit(QtCore.SIGNAL('setTextField'), ' ,'.join(self.formats), None, 10)
        self.Window.stat.emit(QtCore.SIGNAL('setTextField'), str(self.minSize), None, 11)
        self.Window.stat.emit(QtCore.SIGNAL('setTextField'), str(self.maxSize), None, 12)
        self.Window.stat.emit(QtCore.SIGNAL('setTextField'), str(self.coef), None, 13)
        self.Window.stat.emit(QtCore.SIGNAL('setTextField'), str(bool(self.notRecognizedDir)), None, 14)
        self.Window.stat.emit(QtCore.SIGNAL('setTextField'), str(bool(self.notSureRecognizedDir)), None, 15)



    def stopCondition(self, *args):
        return False


    def run(self):
        self.connect(self.Window,
                     QtCore.SIGNAL('showStudent'),
                     self.Window.showStudent
                     )
        self.stat = True
        try:
            if (self.connect(self.Window.stat,
                         QtCore.SIGNAL('setTextField'),
                         self.Window.stat.setTextField
                         )
                and
                self.connect(self.Window.stat,
                             QtCore.SIGNAL('setNumericField'),
                             self.Window.stat.setNumericField
                             )
                ):
                self.stat = True
        except AttributeError:
            self.stat = False

        self.showSettings()
        self.Window.statusBar.showMessage(u'Тренування')
        self.train()
        if self.recognizer:
            self.Window.statusBar.showMessage(u'Готово')
            self.start_recognition()
        else:
            self.Window.statusBar.showMessage(u'Тренування не вдалось')
