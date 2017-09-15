import hou


try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    from Qt import QtWidgets, QtCore, QtGui

error_count = 0
selectedNodes = hou.selectedNodes()
if len(selectedNodes) != 0:
    m = selectedNodes[0]

    clipboard = QtWidgets.QApplication.clipboard()
    text = clipboard.text()
    lines = text.splitlines()
    if len(lines) == 9:
        for line in lines:
            ls = line.split(',', 1)
            if len(ls) == 2:
                try:
                    m.parm(ls[0]).set(eval(ls[1]))
                except:
                    print('cannot setting parameter: ' + ls[0])
                    error_count += 1

        if error_count > 0:
            print('transform values imported with: ' + str(error_count) + ' errors')
        else:
            print('all transform values successfully imported')
else:
    print('nothing selected')