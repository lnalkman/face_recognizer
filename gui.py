# -*- coding: UTF-8 -*-
from PyQt4 import QtCore, QtGui
import sys

app = QtGui.QApplication(sys.argv)

class Window(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setMinimumSize(700, 550)
        self.setWindowTitle(u'Розпізнавання облич')
        #self.resize(750, 600)

        mainLayout = QtGui.QGridLayout(self)
        leftLayout = QtGui.QGridLayout()
        mainLayout.addLayout(leftLayout, 1, 1)

        # Photo label where will recognized or choosen student photo
        self.studPhoto = QtGui.QLabel(parent=self)
        self.studPhoto.setAlignment(QtCore.Qt.AlignCenter)
        img = QtGui.QPixmap();
        img.load('image.png')
        self.studPhoto.setPixmap(img)
        self.studPhoto.setSizePolicy(
            QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding,
            QtGui.QSizePolicy.MinimumExpanding)
            )
        leftLayout.addWidget(self.studPhoto, 1, 1)

        # Widget with information about choosen student
        self.studInfo = QtGui.QTableWidget(2,2)
        # print(self.studInfo.item(1,-1))
        self.studInfo.setItem(0,1, QtGui.QTableWidgetItem('hey i\'m 1,1'))
        leftLayout.addWidget(self.studInfo, 2, 1)

        # Tabs with information about recognition
        self.tabMenu = QtGui.QTabWidget()
        mainLayout.addWidget(self.tabMenu, 1, 2)

        # List of recognized students
        self.findedStudents = QtGui.QListWidget()
        self.findedStudents.addItem('Some item');self.findedStudents.addItem('Some item');self.findedStudents.addItem('Some item');self.findedStudents.addItem('Some item');self.findedStudents.addItem('Some item')
        self.findedStudents.item(0).setBackgroundColor(QtGui.QColor(200, 200, 255))
        self.tabMenu.insertTab(1, self.findedStudents, u'Розпізнані особи')

        # List of recognized students who were late
        self.lateStudents = QtGui.QListWidget()
        self.lateStudents.addItem('Some late item1');self.lateStudents.addItem('Some late item2');self.lateStudents.addItem('Some late item3');self.lateStudents.addItem('Some late item4');
        self.tabMenu.insertTab(2, self.lateStudents, u'Запізнення')

        # List of recognized students who absent
        self.lateStudents = QtGui.QListWidget()
        self.lateStudents.addItem('Some absent item1');self.lateStudents.addItem('Some absent item2');self.lateStudents.addItem('Some absent item3');self.lateStudents.addItem('Some absent item4');self.lateStudents.addItem('Some absent item5');self.lateStudents.addItem('Some absent item6');self.lateStudents.addItem('Some absent item7');
        self.tabMenu.insertTab(3, self.lateStudents, u'Відсутні')

        # Recognition statistics
        self.lateStudents = QtGui.QListWidget()
        self.lateStudents.addItem('Some late item1');self.lateStudents.addItem('Some late item2');self.lateStudents.addItem('Some late item3');self.lateStudents.addItem('Some late item4');
        self.tabMenu.insertTab(4, self.lateStudents, u'Статистика')


window = Window()
window.show()

sys.exit(app.exec_())
