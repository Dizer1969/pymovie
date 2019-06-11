from pymovie import apertureEditDialog
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QTableWidgetItem


class EditApertureDialog(QDialog, apertureEditDialog.Ui_Dialog):
    def __init__(self, messager, saver, dictList):
        super(EditApertureDialog, self).__init__()
        self.setupUi(self)
        self.msgRoutine = messager
        self.settingsSaver = saver
        self.dictList = dictList
        self.fillApertureTable()

    def fillApertureTable(self):
        # self.showMsg('Aperture table filled from appDictList')
        for rowDict in self.dictList:
            numRows = self.tableWidget.rowCount()
            self.tableWidget.insertRow(numRows)

            item = QTableWidgetItem(str(rowDict['name']))
            self.tableWidget.setItem(numRows, 0, item)

            item = QTableWidgetItem(str(rowDict['xy']))
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidget.setItem(numRows, 1, item)

            item = QTableWidgetItem(str(rowDict['threshDelta']))
            self.tableWidget.setItem(numRows, 2, item)

            item = QTableWidgetItem(str(rowDict['defMskRadius']))
            self.tableWidget.setItem(numRows, 3, item)

            item = QTableWidgetItem(str(rowDict['color']))
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidget.setItem(numRows, 4, item)

            item = QTableWidgetItem(str(rowDict['joggable']))
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidget.setItem(numRows, 5, item)

            item = QTableWidgetItem(str(rowDict['autoTextOut']))
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidget.setItem(numRows, 6, item)

            item = QTableWidgetItem(str(rowDict['thumbnailSource']))
            item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
            self.tableWidget.setItem(numRows, 7, item)

            item = QTableWidgetItem(str(rowDict['outputOrder']))
            self.tableWidget.setItem(numRows, 8, item)

    def closeEvent(self, event):
        # self.msgRoutine("Saving aperture dialog settings")
        self.settingsSaver.setValue('appEditDialogSize', self.size())
        self.settingsSaver.setValue('appEditDialogPos', self.pos())

        # Now comes the hard work of validating and using the tableWidget data
        # to update the aperture properties

        for row in range(self.tableWidget.rowCount()):
            aperture = self.dictList[row]['appRef']

            aperture.name = self.tableWidget.item(row, 0).text()

            # Enforce that thresh is a positive integer
            text = self.tableWidget.item(row, 2).text()
            try:
                thresh = int(text)
            except ValueError:
                self.msgRoutine(f'In {aperture.name}(thresh): {text} is not a valid integer')
                return
            if thresh < 0:
                self.msgRoutine(f'In {aperture.name}(thresh): {text} is not a positive integer')
                return
            aperture.thresh = thresh

            # Enforce that def mask radius has value between 2.0 and 24.0
            text = self.tableWidget.item(row, 3).text()
            try:
                radius = float(text)
            except ValueError:
                self.msgRoutine(f'In {aperture.name}(def mask radius): {text} is not a valid float')
                return
            if radius < 2.0 or radius > 24.0:
                self.msgRoutine(f'In {aperture.name}(def mask radius): {text} is not in range 2.0 to 24.0')
                return
            aperture.default_mask_radius = radius

            aperture.color = self.tableWidget.item(row, 4).text()
            if aperture.color == 'green':
                aperture.setGreen()
            elif aperture.color == 'red':
                aperture.setRed()
            elif aperture.color == 'white':
                aperture.setWhite()
            elif aperture.color == 'yellow':
                aperture.setYellowNoCheck()

            text = self.tableWidget.item(row, 5).text()
            if text == 'True':
                aperture.jogging_enabled = True
            else:
                aperture.jogging_enabled = False

            text = self.tableWidget.item(row, 6).text()
            if text == 'True':
                aperture.auto_display = True
            else:
                aperture.auto_display = False

            text = self.tableWidget.item(row, 7).text()
            if text == 'True':
                aperture.thumbnail_source = True
            else:
                aperture.thumbnail_source = False

            # Enforce that output order is a positive integer
            text = self.tableWidget.item(row, 8).text()
            try:
                order = int(text)
            except ValueError:
                self.msgRoutine(f'In {aperture.name}(order): {text} is not a valid integer')
                return
            if order < 0:
                self.msgRoutine(f'In {aperture.name}(order): {text} is not a positive integer')
                return
            aperture.order_number = order

    def contextMenuEvent(self, event):
        # self.msgRoutine("Got a right-click event")
        self.col = self.tableWidget.currentColumn()
        self.row = self.tableWidget.currentRow()
        items = self.tableWidget.selectedItems()
        if not items:
            self.msgRoutine('Nothing selected')
            return
        # self.msgRoutine(f'row: {self.row}  column: {self.col} items: {items[0]}')

        if 5 <= self.col <= 7:
            self.menu = QtGui.QMenu()
            doTrue = QtGui.QAction("Set True", self)
            doTrue.triggered.connect(self.setTrue)
            self.menu.addAction(doTrue)

            doFalse = QtGui.QAction("Set False", self)
            doFalse.triggered.connect(self.setFalse)
            self.menu.addAction(doFalse)

            self.menu.popup(QtGui.QCursor.pos())
        elif self.col == 4:
            self.menu = QtGui.QMenu()

            setRed = QtGui.QAction("Set red", self)
            setRed.triggered.connect(self.setRed)
            self.menu.addAction(setRed)

            setGreen = QtGui.QAction("Set green", self)
            setGreen.triggered.connect(self.setGreen)
            self.menu.addAction(setGreen)

            setYellow = QtGui.QAction("Set yellow", self)
            setYellow.triggered.connect(self.setYellow)
            self.menu.addAction(setYellow)

            setWhite = QtGui.QAction("Set white", self)
            setWhite.triggered.connect(self.setWhite)
            self.menu.addAction(setWhite)

            self.menu.popup(QtGui.QCursor.pos())

    def setTrue(self):
        if self.col == 7:
            # We enforce the condition that only one aperture
            # can have True for this property
            for row in range(self.tableWidget.rowCount()):
                item = QTableWidgetItem('False')
                item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
                self.tableWidget.setItem(row, self.col, item)

        item = QTableWidgetItem('True')
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        self.tableWidget.setItem(self.row, self.col, item)

    def setFalse(self):
        item = QTableWidgetItem('False')
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        self.tableWidget.setItem(self.row, self.col, item)

    def setRed(self):
        item = QTableWidgetItem('red')
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        self.tableWidget.setItem(self.row, self.col, item)

    def setGreen(self):
        for row in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(row, self.col).text() == 'green':
                self.msgRoutine(f'!!! There can only be a single green aperture at a time !!!')
                return
        item = QTableWidgetItem('green')
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        self.tableWidget.setItem(self.row, self.col, item)

    def setYellow(self):
        numYellow = 0
        for row in range(self.tableWidget.rowCount()):
            if self.tableWidget.item(row, self.col).text() == 'yellow':
                numYellow += 1

        # self.msgRoutine(f'{numYellow} yellows found')

        if numYellow == 2:
            self.msgRoutine(f'!!! There can only be a max of two yellow apertures !!!')
            return

        item = QTableWidgetItem('yellow')
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        self.tableWidget.setItem(self.row, self.col, item)

    def setWhite(self):
        item = QTableWidgetItem('white')
        item.setFlags(item.flags() ^ QtCore.Qt.ItemIsEditable)
        self.tableWidget.setItem(self.row, self.col, item)
