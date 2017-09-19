import hou
from vfh import vfh_rop

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    from Qt import QtWidgets, QtCore, QtGui

error_count = 0
vrayRopNode = vfh_rop._getVrayRop()
if vrayRopNode != None:
    type = ''

    clipboard = QtWidgets.QApplication.clipboard()
    text = clipboard.text()
    lines = text.splitlines()

    if len(lines) > 1:
        if lines[0].startswith('#') == True:
            type = lines[0][1:]
            if vrayRopNode.type().name() == type:
                vrayRopNode.parm('f1').deleteAllKeyframes()
                vrayRopNode.parm('f2').deleteAllKeyframes()
                for line in lines[1:]:
                    ls = line.split(',', 1)
                    if len(ls) == 2:
                        try:
                            if ls[1].startswith('\'') and ls[1].endswith('\''):
                                vrayRopNode.parm(ls[0]).set(ls[1][1:-1])#.set(ls[1][1:-2])
                            else:
                                vrayRopNode.parm(ls[0]).set(eval(ls[1]))
                        except:
                            print('cannot setting parameter: ' + ls[0])
                            error_count+=1

                if error_count > 0:
                    print('renderer parameters imported with: ' + str(error_count) + ' errors')
                else:
                    print('all renderer parameters successfully imported')
            else:
                print('cannot apply clipboad values, wrong type!')
        else:
            print('cannot apply clipboad values, wrong type!')
    else:
        print('nothing to import')
else:
    print('cannot find VRay ropnode')
