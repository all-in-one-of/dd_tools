import inspect
import os
import hou
import subprocess
import shutil

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    from Qt import QtWidgets, QtCore, QtGui

'''
from Qt import QtWidgets, QtCore, QtGui
'''

class DeselectableListWidget(QtWidgets.QListWidget):
    def mousePressEvent(self, event):
        self.clearSelection()
        QtWidgets.QListWidget.mousePressEvent(self, event)

class Toolbox(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(Toolbox, self).__init__(parent)

        self.currentlist = list()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timeout)
        self.timer.start(5000)

        #self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        self.setWindowTitle("Toolbox")

        #get current tools folder
        filename = inspect.getframeinfo(inspect.currentframe()).filename
        self.path = os.path.dirname(os.path.abspath(filename)) + '\\tools\\'

        #create widgets
        self.listWidget = DeselectableListWidget() #QtWidgets.QListWidget()
        #self.listWidget.setIconSize(QtCore.QSize(18, 18))
        self.button = QtWidgets.QPushButton('Refresh')

        #force interface creation
        self.createInterface()

        # layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        #add widgets to layout
        #mainLayout.addWidget(self.button)
        mainLayout.addWidget(self.listWidget)

        self.setLayout(mainLayout)
        #self.layout().setContentsMargins(0, 0, 0, 0)

    def timeout(self):
        tmplist = list()
        for file in os.listdir(self.path):
            hidden = os.path.isfile(self.path + file + '\\hidden')
            if (not hidden):
                tmplist.append(file.title())

        if tmplist != self.currentlist:
            self.update()


    def editScript(self):
        #execute selected tool
        item = self.listWidget.currentItem()
        py_file = self.path + item.data(QtCore.Qt.UserRole) + '\\script.py'
        subprocess.Popen(['C:/Program Files/JetBrains/PyCharm Community Edition 2017.1.4/bin/pycharm64.exe', py_file])

    def openScriptFolder(self):
        item = self.listWidget.currentItem()
        name = item.text().replace(" ", "_").lower()
        os.startfile(self.path + name)

    def editDescription(self):
        #execute selected tool
        item = self.listWidget.currentItem()
        description_file = self.path + item.data(QtCore.Qt.UserRole) + '\\description'
        proc = subprocess.Popen(['notepad.exe', description_file])
        proc.wait()
        with open(description_file) as file_content:
            data = "".join(line.rstrip() for line in file_content)
            item.setToolTip(data)


    def editIcon(self):
        #execute selected tool
        item = self.listWidget.currentItem()
        icon_file = self.path + item.data(QtCore.Qt.UserRole) + '\\icon.svg'
        proc = subprocess.Popen(['C:/Program Files/Inkscape/inkscape.exe', icon_file])
        proc.wait()
        qIcon = QtGui.QIcon(icon_file)
        item.setIcon(qIcon)

    def openScene(self, item):
        #execute selected tool
        py_file = self.path + item.data(QtCore.Qt.UserRole) + '\\script.py'
        execfile(py_file)

    def update(self):
        self.currentlist = list()
        self.listWidget.clear()
        for file in os.listdir(self.path):
            hidden = os.path.isfile(self.path + file + '\\hidden')
            if (not hidden):
                self.currentlist.append(file.title())
                item = QtWidgets.QListWidgetItem(file.title().replace("_", " "), self.listWidget)
                item.setData(QtCore.Qt.UserRole, file)
                # item.setSizeHint(QtCore.QSize(0, 26))
                # item.setText(filename.title().replace("_"," "))
                # self.listWidget.addItem(item)

                icon_file = self.path + file + '\\icon.svg'
                if (os.path.isfile(icon_file)):
                    qIcon = QtGui.QIcon(icon_file)
                    item.setIcon(qIcon)

                description_file = self.path + file + '\\description'
                if (os.path.isfile(description_file)):
                    with open(description_file) as file_content:
                        data = "".join(line.rstrip() for line in file_content)
                        item.setToolTip(data)

                item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

    def contextMenuEvent(self, QPos):
        if len(self.listWidget.selectedItems()) > 0:
            menu = QtWidgets.QMenu(self)
            attachAction = menu.addAction("Edit script in PyCharm")
            attachAction.triggered.connect(self.editScript)
            attachAction = menu.addAction("Edit description")
            attachAction.triggered.connect(self.editDescription)
            attachAction = menu.addAction("Edit icon in Inkscape")
            attachAction.triggered.connect(self.editIcon)
            attachAction = menu.addAction("Open script folder")
            attachAction.triggered.connect(self.openScriptFolder)
            if QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.AltModifier:
                menu.addSeparator()
                attachAction = menu.addAction("Rename")
                attachAction.triggered.connect(self.rename)
                attachAction = menu.addAction("Hide")
                attachAction.triggered.connect(self.setHidden)
                attachAction = menu.addAction("Duplicate")
                attachAction.triggered.connect(self.duplicate)
                attachAction = menu.addAction("Delete")
                attachAction.triggered.connect(self.delete)

            parentPosition = self.listWidget.mapToGlobal(QtCore.QPoint(0, 0))
            menu.move(parentPosition + QPos)
            menu.show()

    def rename(self):
        # execute selected tool
        item = self.listWidget.currentItem()
        self.listWidget.editItem(item)

    def duplicate(self):
        # execute selected tool
        item = self.listWidget.currentItem()
        newitem = QtWidgets.QListWidgetItem(item.text() + ' (Copy)', self.listWidget)
        oldname = item.data(QtCore.Qt.UserRole).replace(" ", "_").lower()
        newname = newitem.text().replace(" ", "_").lower()
        #newitem.setData(QtCore.Qt.UserRole, newname)
        #newitem.setIcon(item.icon())
        #self.listWidget.setCurrentItem(newitem)
        try:
            shutil.copytree(os.path.join(self.path, oldname), os.path.join(self.path, newname))
        except:
            pass
        self.update()

    def delete(self):
        # execute selected tool
        item = self.listWidget.currentItem()
        name = item.text().replace(" ", "_").lower()
        try:
            shutil.rmtree(os.path.join(self.path, name))
        except:
            pass
        self.update()

    def setHidden(self):
        item = self.listWidget.currentItem()
        hidden_file = self.path + item.data(QtCore.Qt.UserRole) + '\\hidden'
        f = open(hidden_file, 'w')
        f.close()
        self.update()

    def nameChanged(self, item):
        item.setText(item.text().title().replace("_", " "))
        #item = self.listWidget.currentItem()
        oldname = item.data(QtCore.Qt.UserRole).replace(" ", "_").lower()
        newname = item.text().replace(" ", "_").lower()
        item.setData(QtCore.Qt.UserRole, newname)
        try:
            os.rename(os.path.join(self.path, oldname), os.path.join(self.path, newname))
        except:
            pass

    def createInterface(self):

        self.update()

        #connect list items to function
        #self.listWidget.doubleClicked.connect(self.editScript)
        self.listWidget.clicked.connect(self.openScene)

        self.listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.contextMenuEvent)
        self.listWidget.itemChanged.connect(self.nameChanged)

        #connect refresh button
        self.button.clicked.connect(self.update)

def run():
    window = Toolbox()
    window.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
    window.show()
