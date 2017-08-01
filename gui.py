# -*- coding: UTF-8 -*-

import os
import sys
import re
from PyQt4 import QtCore, QtGui
from Controller import RecognitionController

app = QtGui.QApplication(sys.argv)

class ScaledPhotoLabel(QtGui.QLabel):
    """
    Auto scalable photo label. Use in grid.
    """
    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, parent)
        self.orgPixmap = None

    def resizeEvent(self, event=None):
        if self.orgPixmap:
            pixmap = self.orgPixmap
            size = event.size()
            self.setPixmap(pixmap.scaledToHeight(size.height() - 10))


class StudentInfo(QtGui.QGridLayout):
    """
    Layout with text labels where will be information about choosen student.
    """

    fields = [
        u"<span style='font-size: 26px; color: #0e2838;font-family: Arial,sans-serif;'>Ім'я</span>",
        u"<span style='font-size: 26px; color: #0e2838;font-family: Arial,sans-serif;'>Прізвище</span>",
        u"<span style='font-size: 26px; color: #0e2838;font-family: Arial,sans-serif;'>По батькові</span>",
        u"<span style='font-size: 26px; color: #0e2838;font-family: Arial,sans-serif;'>Група</span>",
    ]

    tag = [
        "<b style='font-size: 26px; color: #333333;font-family: Arial,sans-serif;'>",
        "</b>"
        ]

    def __init__(self, parent=None):
        QtGui.QGridLayout.__init__(self, parent)
        self.setVerticalSpacing(10)

        for i, field in enumerate(self.fields, 1):
            self.addWidget(QtGui.QLabel(field), i, 1)

        self.name = QtGui.QLabel("<b style='font-size: 26px; color: #333333;font-family: Arial,sans-serif;'>ExampleName</b>")
        # Reserve addition place for all labels in second column
        self.name.setMinimumWidth(350)
        self.addWidget(self.name, 1, 2)

        self.last_name = QtGui.QLabel("<b style='font-size: 26px; color: #333333;font-family: Arial,sans-serif;'>ExampleSecondName</b>")
        self.addWidget(self.last_name, 2, 2)

        self.middle_name = QtGui.QLabel("<b style='font-size: 26px; color: #333333;font-family: Arial,sans-serif;'>ExampleMiddleName</b>")
        self.addWidget(self.middle_name, 3, 2)

        self.group = QtGui.QLabel("<b style='font-size: 26px; color: #333333;font-family: Arial,sans-serif;'>ExampleGroup</b>")
        self.addWidget(self.group, 4, 2)


class StudentsTable(QtGui.QTableWidget):
    """
    Table with list of students.
    Implements a friendly api to add students.
    """
    def __init__(self, parent, *args, **kwargs):
        QtGui.QTableWidget.__init__(self, 0, 3)
        self.parent = parent

        self.setHorizontalHeaderLabels((u'Особа', u'Дата та час', u'K'))
        self.setStyleSheet('background-color: #d6f7ff;')

        # Size properties
        self.hHeader = self.horizontalHeader()
        self.hHeader.setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.hHeader.setResizeMode(1, QtGui.QHeaderView.Fixed)
        self.hHeader.setResizeMode(2, QtGui.QHeaderView.ResizeToContents)

        self.setShowGrid(False)
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.setAlternatingRowColors(True)

        self.rowsData = []

        QtCore.QObject.connect(self,
            QtCore.SIGNAL('cellDoubleClicked(int, int)'),
            self.cellDoubleClicked
            )



    def setConnection(self, controller):
        # True if table connected with controller class
        self.connection = self.connect(self.parent.controller,
            QtCore.SIGNAL('showStudent'),
            self.parent.controller.showStudent
            )



    def addStudent(self, fullName=None, date=None, k=None, late=False, metadata=None):
        """
        Add student's name, date and k(recognition coefficient) to table.
        Accept fullName->String, date->String, k->[int, String], late->bool
        If late: added row will be painted in lateColor variable
        """
        lateColor = QtGui.QColor(255, 75, 75)

        name = QtGui.QTableWidgetItem(fullName or ' ')
        date = QtGui.QTableWidgetItem(date or ' ')
        k = QtGui.QTableWidgetItem(str(k))

        if late:
            name.setBackgroundColor(lateColor)
            date.setBackgroundColor(lateColor)
            k.setBackgroundColor(lateColor)

        # Add new row
        currRow = self.rowCount()
        self.insertRow(currRow)
        self.setItem(currRow, 0, name)
        self.setItem(currRow, 1, date)
        self.setItem(currRow, 2, k)

        self.rowsData.append(metadata)


    def cellDoubleClicked(self, row, column):
        if self.connection:
            self.parent.controller.emit(QtCore.SIGNAL('showStudent'),
                    self.rowsData[row]
                )


class StatusBar(QtGui.QStatusBar):

    def __init__(self, *args):
        QtGui.QStatusBar.__init__(self)

        font = QtGui.QFont('Arial', 12)
        # font.setUnderline(True)
        self.setFont(font)
        self.setStyleSheet(
            '''background-color: #1488a0;
            color: #fff;'''
        )
        self.setCursor(
            QtGui.QCursor(QtCore.Qt.PointingHandCursor)
            )
        self.showMessage(u'Завантаження')


    def enterEvent(self, event):
        new_font = self.font()
        new_font.setUnderline(True)
        self.setFont(new_font)


    def leaveEvent(self, event):
        new_font = self.font()
        new_font.setUnderline(False)
        self.setFont(new_font)


class Window(QtGui.QWidget):

    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setMinimumSize(700, 550)
        self.setWindowTitle(u'Розпізнавання облич')
        #self.resize(750, 600)
        self.setStyleSheet('background-color: #aaf0ff;')

        mainLayout = QtGui.QGridLayout(self)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        leftLayout = QtGui.QGridLayout()
        leftLayout.setContentsMargins(11, 11, 0, 15)
        mainLayout.addLayout(leftLayout, 1, 1)

        # Photo label where will recognized or choosen student photo
        self.studPhoto = ScaledPhotoLabel()
        self.studPhoto.setAlignment(QtCore.Qt.AlignCenter)
        img = QtGui.QPixmap();
        img.load('image.jpg')
        self.studPhoto.orgPixmap = img
        self.studPhoto.setPixmap(img)
        self.studPhoto.setSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding,
            QtGui.QSizePolicy.MinimumExpanding
            )
        leftLayout.addWidget(self.studPhoto, 1, 1)

        # Layout with information about choosen student
        self.studInfo = StudentInfo()
        leftLayout.addLayout(self.studInfo, 2, 1)

        # Tabs with information about recognition
        self.tabMenu = QtGui.QTabWidget()
        self.tabMenu.setSizePolicy(
            QtGui.QSizePolicy.MinimumExpanding,
            QtGui.QSizePolicy.MinimumExpanding
            )
        tabLayout = QtGui.QGridLayout()
        tabLayout.addWidget(self.tabMenu)
        tabLayout.setContentsMargins(0, 11, 11, 15)
        mainLayout.addLayout(tabLayout, 1, 2)

        # List of recognized students
        self.findedStudents = StudentsTable(self)
        self.tabMenu.insertTab(1, self.findedStudents, u'Розпізнані особи')

        # List of recognized students who absent
        self.absentStudents = QtGui.QListWidget()
        self.tabMenu.insertTab(3, self.absentStudents, u'Відсутні')

        # Recognition statistics
        self.stat = QtGui.QListWidget()
        self.tabMenu.insertTab(3, self.stat, u'Статистика')

        self.statusBar = StatusBar()

        # self.statusBar.hide()
        mainLayout.addWidget(self.statusBar, 2, 1, 1, 2)


    def setImage(self, imagePath=None):
        """
        Set new image in self.studPhoto label.
        New image resize to prew image size.
        """
        event = QtGui.QResizeEvent(
            self.studPhoto.sizeHint(),
            QtCore.QSize()
            )
        image = QtGui.QPixmap()
        image.load(imagePath)
        self.studPhoto.orgPixmap = image
        self.studPhoto.setPixmap(image)
        self.studPhoto.resizeEvent(event)


    def setLabelsData(self, name=None, sname=None, mname=None, group=None):
        tag = self.studInfo.tag
        student = self.studInfo
        student.name.setText(tag[0] + unicode(name) + tag[1])
        student.last_name.setText(tag[0] + unicode(sname) + tag[1])
        student.middle_name.setText(tag[0] + unicode(mname) + tag[1])
        student.group.setText(tag[0] + unicode(group) + tag[1])


    def showStudent(self, data=None):
        if not data:
            return None

        name, sname, mname = None, None, None

        imagePath = data.get('images_path')
        if imagePath:
            images = os.listdir(imagePath)
            if images:
                # Set first photo in imagePath dir
                self.setImage(os.path.join(imagePath, images[0]))

        full_name = data.get('full_name')
        if isinstance(full_name, str) or isinstance(full_name, unicode):
            full_name = full_name.split(' ')
            # If full name has initials
            if len(full_name) == 2 and full_name[1].count('.') == 2:
                dotPos = full_name[1].find('.') + 1
                name = full_name[1][:dotPos]
                sname = full_name[0]
                mname = full_name[1][full_name[1].find('.') + 1:]
            elif len(full_name) == 3:
                name, sname, mname = full_name

        group = data.get('group')

        self.setLabelsData(name, sname, mname, group)


    def setController(self, controller):
        self.controller = controller(self)
        self.findedStudents.setConnection(controller)


window = Window()
window.setController(RecognitionController)
window.controller.start()
window.show()

sys.exit(app.exec_())
