# -*- coding: UTF-8 -*-
from PyQt4 import QtCore, QtGui
import sys

app = QtGui.QApplication(sys.argv)

class ScaledPhotoLabel(QtGui.QLabel):
    """
    Auto scalable photo label. Use in grid.
    """
    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, parent)
        self.orgPixmap = None

    def resizeEvent(self, event):
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
    def __init__(self, *args, **kwargs):
        QtGui.QTableWidget.__init__(self, 0, 3)

        self.setHorizontalHeaderLabels((u'Особа', u'Дата та час', u'K'))

        # Size properties
        self.hHeader = self.horizontalHeader()
        self.hHeader.setResizeMode(0, QtGui.QHeaderView.Stretch)
        self.hHeader.setResizeMode(1, QtGui.QHeaderView.Fixed)
        self.hHeader.setResizeMode(2, QtGui.QHeaderView.ResizeToContents)

        self.setShowGrid(False)
        self.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)

        self.setAlternatingRowColors(True)


    def addStudent(self, fullName=None, date=None, k=None, late=False):
        """
        Add student's name, date and k(recognition coefficient) to table.
        Accept fullName->String, date->String, k->[int, String], late->bool
        If late: added row will be painted in lateColor variable
        """
        lateColor = QtGui.QColor(255, 75, 75)

        name = QtGui.QTableWidgetItem(fullName or ' ')
        date = QtGui.QTableWidgetItem(date or ' ')
        k = QtGui.QTableWidgetItem(str(k or -1))

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
        self.studPhoto = ScaledPhotoLabel()
        self.studPhoto.setAlignment(QtCore.Qt.AlignCenter)
        img = QtGui.QPixmap();
        img.load('image.png')
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
        mainLayout.addWidget(self.tabMenu, 1, 2)

        # List of recognized students
        self.findedStudents = StudentsTable()
        self.tabMenu.insertTab(1, self.findedStudents, u'Розпізнані особи')

        # List of recognized students who absent
        self.absentStudents = QtGui.QListWidget()
        self.tabMenu.insertTab(3, self.absentStudents, u'Відсутні')

        # Recognition statistics
        self.stat = QtGui.QListWidget()
        self.tabMenu.insertTab(3, self.stat, u'Статистика')


    def setImage(self, imagePath=None):
        image = QtGui.QPixmap()
        image.load(imagePath)
        self.studPhoto.orgPixmap = image
        self.studPhoto.setPixmap(image)


window = Window()
window.show()

sys.exit(app.exec_())
