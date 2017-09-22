import hou

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    from Qt import QtWidgets, QtCore, QtGui


def importTransformFromClipboard(_o):
    error_count = 0
    is_tuple = False
    clipboard = QtWidgets.QApplication.clipboard()
    text = clipboard.text()
    lines = text.splitlines()

    if lines[0].startswith('#copytransform'):
        ls = lines[0].split(',', 2)
        fps = ls[1]
        range = ls[2]

        if fps != str(hou.fps()):
            print('warning: fps differs from export')
        if range != str(hou.playbar.timelineRange()):
            print('warning: animation range differs from export')

        for p in (_o.parms()):
            p.deleteAllKeyframes()

        for line in lines[1:]:
            ls = line.split(',', 1)
            if len(ls) == 2:
                parm_name = ls[0]
                parm_val = eval(ls[1])
                is_tuple = isinstance(parm_val, tuple)
                try:
                    if is_tuple:
                        for k in parm_val:
                            setKey = hou.Keyframe()
                            setKey.setFrame(k[0])
                            setKey.setValue(k[1])
                            _o.parm(parm_name).setKeyframe(setKey)
                    else:
                        _o.parm(parm_name).set(parm_val)

                except:
                    print('cannot setting parameter: ' + ls[0])
                    error_count += 1

        if error_count > 0:
            print('transform values imported with: ' + str(error_count) + ' errors')
        else:
            print('all transform values successfully imported')
    else:
        print('cannot apply clipboad values, wrong type!')


selectedNodes = hou.selectedNodes()
if len(selectedNodes) == 1:
    _o = selectedNodes[0]
    importTransformFromClipboard(_o)
else:
    if len(selectedNodes) == 0:
        print('nothing selected')
    else:
        print('more then one object selected')
