import inspect
import os
import subprocess
import shutil
import MaxPlus
import maxparenting

reload(maxparenting)

try:
	from PySide import QtCore, QtGui
except ImportError:
    from Qt import QtCore, QtGui



class CustomListWidget(QtGui.QListWidget):
    def mousePressEvent(self, event):
        self.clearSelection()
        self.mouseButton = event.button()
        QtGui.QListWidget.mousePressEvent(self, event)

    def edit(self, index, trigger, event):
        if trigger == QtGui.QAbstractItemView.DoubleClicked:
            return False
        return QtGui.QListWidget.edit(self, index, trigger, event)

class Toolbox(maxparenting.MaxWidget):

    def __init__(self, parent=None):
        super(Toolbox, self).__init__(parent)

        self.currentlist = list()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timeout)
        self.timer.start(5000)

        #self.setParent(hou.ui.mainQtWindow(), QtCore.Qt.Window)
        self.setWindowTitle("Toolbox")
        self.resize(310, 225)
        self.setStyleSheet("""
            QWidget {
                font-family: MS Shell Dlg 2;
            }
            QLabel {
                background: rgba(48, 48, 48, 255);
                padding: 2px 2px 5px 2px;
            }
            QListView {
                outline: none;                                      
                border: none;
                show-decoration-selected: 1; /* make the selection span the entire width of the view */
            }
            QListView::item {              
                margin-left: 0px;
                border: 1px solid rgba(0, 0, 0, 0);
            }
            QListView::item:alternate {
                background: #EEEEEE;
            }
            QListView::item:selected {
                color: white;
                border: 1px solid rgba(255, 165, 0, 200);
            }            
            QListView::item:selected:!active {                
                background: rgba(255, 165, 0, 32);                
            }            
            QListView::item:selected:active {
                background: rgba(255, 165, 0, 32);                
            }            
            QListView::item:hover {
                background: rgba(255, 255, 255, 16);
            }
            QLineEdit {    
                background: rgba(25, 25, 25, 255);
                padding: 0px;
                margin-left: 1px;
                margin-right: -2px;
                border-style: none;
                font-size: 12px;
                selection-color: black;
                selection-background-color: rgba(255, 165, 0, 200);
            }"""
        )

        #get current tools folder
        filename = inspect.getframeinfo(inspect.currentframe()).filename
        self.path = os.path.dirname(os.path.abspath(filename)) + '\\tools\\'

        #create widgets
        self.listWidget = CustomListWidget() #QtWidgets.QListWidget()
        #self.listWidget.setIconSize(QtCore.QSize(18, 18))
        #self.button = QtGui.QPushButton('Refresh')

        self.banner = QtGui.QLabel()
        self.banner.setPixmap(QtGui.QPixmap(os.path.dirname(os.path.abspath(filename)) + '\\header.png'))

        #force interface creation
        self.createInterface()

        # layout
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)

        #add widgets to layout
        #mainLayout.addWidget(self.button)
        mainLayout.addWidget(self.banner)
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
        #execute editScript tool
        item = self.listWidget.currentItem()
        ms_file = self.path + item.data(QtCore.Qt.UserRole) + '\\script.ms'
        subprocess.Popen(['C:/Program Files/JetBrains/PyCharm Community Edition 2017.1.4/bin/pycharm64.exe', ms_file])

    def openScriptFolder(self):
        item = self.listWidget.currentItem()
        name = item.text().replace(" ", "_").lower()
        os.startfile(self.path + name)

    def editDescription(self):
        #execute editDescription tool
        item = self.listWidget.currentItem()
        description_file = self.path + item.data(QtCore.Qt.UserRole) + '\\description'
        proc = subprocess.Popen(['notepad.exe', description_file])
        proc.wait()
        with open(description_file) as file_content:
            data = "".join(line.rstrip() for line in file_content)
            item.setToolTip(data)

    def editIcon(self):
        #execute editIcon tool
        item = self.listWidget.currentItem()
        icon_file = self.path + item.data(QtCore.Qt.UserRole) + '\\icon.svg'
        proc = subprocess.Popen(['C:/Program Files/Inkscape/inkscape.exe', icon_file])
        proc.wait()
        qIcon = QtGui.QIcon()
        qIcon.addPixmap(icon_file, QtGui.QIcon.Normal)
        qIcon.addPixmap(icon_file, QtGui.QIcon.Selected)
        item.setIcon(qIcon)

    def executeScript(self, item):
        # execute executeScript tool
        if self.listWidget.mouseButton == QtCore.Qt.MouseButton.LeftButton:
            ms_file = self.path + item.data(QtCore.Qt.UserRole) + '\\script.ms'
            MaxPlus.Core.EvalMAXScript('fileIn(@\"{0}\")'.format(ms_file))

    def update(self):
        self.currentlist = list()
        self.listWidget.clear()
        for file in os.listdir(self.path):
            hidden = os.path.isfile(self.path + file + '\\hidden')
            if (not hidden):
                self.currentlist.append(file.title())
                item = QtGui.QListWidgetItem(file.title().replace("_", " "), self.listWidget)
                item.setData(QtCore.Qt.UserRole, file)

                icon_file = self.path + file + '\\icon.svg'
                if (os.path.isfile(icon_file)):
                    qIcon = QtGui.QIcon()
                    qIcon.addPixmap(icon_file, QtGui.QIcon.Normal)
                    qIcon.addPixmap(icon_file, QtGui.QIcon.Selected)
                    item.setIcon(qIcon)

                description_file = self.path + file + '\\description'
                if (os.path.isfile(description_file)):
                    with open(description_file) as file_content:
                        data = "".join(line.rstrip() for line in file_content)
                        item.setToolTip(data)

                item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

    def contextMenuEvent(self, QPos):
        if len(self.listWidget.selectedItems()) > 0:
            menu = QtGui.QMenu(self)
            attachAction = menu.addAction("Edit script in PyCharm")
            attachAction.triggered.connect(self.editScript)
            attachAction = menu.addAction("Edit description")
            attachAction.triggered.connect(self.editDescription)
            attachAction = menu.addAction("Edit icon in Inkscape")
            attachAction.triggered.connect(self.editIcon)
            attachAction = menu.addAction("Open script folder")
            attachAction.triggered.connect(self.openScriptFolder)
            if QtGui.QApplication.keyboardModifiers() == QtCore.Qt.AltModifier:
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
        # execute rename tool
        item = self.listWidget.currentItem()
        self.listWidget.editItem(item)

    def duplicate(self):
        # execute selected tool
        item = self.listWidget.currentItem()
        newitem = QtGui.QListWidgetItem(item.text() + ' (Copy)', self.listWidget)
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
        # execute delete tool
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
        self.listWidget.clicked.connect(self.executeScript)

        self.listWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.contextMenuEvent)
        self.listWidget.itemChanged.connect(self.nameChanged)

        #connect refresh button
        #self.button.clicked.connect(self.update)

'''
def run():
    window = Toolbox()
    window.setParent(hou.qt.mainWindow(), QtCore.Qt.Window)
    window.show()
'''

global window
window = Toolbox()