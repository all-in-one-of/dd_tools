import hou

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    from Qt import QtWidgets, QtCore, QtGui





clipboard = QtWidgets.QApplication.clipboard()
text = clipboard.text()
lines = text.splitlines()
name = ''
type = ''
m = None
if len(hou.selectedNodes()) > 0:
    m = hou.selectedNodes()[0]

error_count = 0

if lines.count > 1:
    if lines[0] == '#parm_export':
        for line in lines[1:]:
            ls = line.split(',', 1)
            if len(ls) == 2:
                if ls[0] == 'type':
                    type = ls[1][1:-1]
                elif ls[0] == 'name':
                    name = ls[1][1:-1]
                    if m == None:
                        try:
                            parent = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor).pwd()
                            if parent != None:
                                m = parent.createNode(type, name)
                                m.moveToGoodPosition()
                                m.setSelected(True, True)
                        except:
                            pass
                    else:
                        if m.type().name() != type:
                            m.changeNodeType(type)
                        if m.name() != name:
                            m.setName(name)
                else:
                    try:
                        m.parm(ls[0]).set(eval(ls[1]))
                    except:
                        print('cannot setting parameter: ' + ls[0])
                        error_count += 1

        if error_count > 0:
            print('material/texmap parameters imported with: ' + str(error_count) + ' errors')
        else:
            print('material/texmap parameters successfully imported')
    else:
        print('cannot apply clipboad values, wrong type!')
else:
    print('nothing to import')
