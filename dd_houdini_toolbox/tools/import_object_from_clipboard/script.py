import hou
import shutil
import os

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    from Qt import QtWidgets, QtCore, QtGui

error_count = 0

clipboard = QtWidgets.QApplication.clipboard()
text = clipboard.text()
lines = text.splitlines()

filename = ""
name = ""
object_id = 0
wirecolor = (0,0,0)
handle = 0

if lines.count > 1:
    if lines[0].startswith('#'):
        type = lines[0][1:]

    if type == 'abc_export':
        for line in lines[1:]:
            if line.startswith('filename='):
                filename = line[9:]
            elif line.startswith('name='):
                name = line[5:]
            elif line.startswith('object_id='):
                object_id = eval( line[10:] )
            elif line.startswith('wirecolor='):
                wirecolor = eval( line[10:] )
            elif line.startswith('handle='):
                handle = eval( line[7:] )

        #copy file to $HIP folder
        geo_dir = hou.expandString('$HIP') + '/geo/'

        if not os.path.exists(geo_dir):
            os.makedirs(geo_dir)

        hip_filename = geo_dir + os.path.basename(filename) + ".abc"

        shutil.copyfile(filename, hip_filename)
        
        obj = hou.node('/obj')
        geo = obj.createNode('geo', name)
        geo.moveToGoodPosition()
        file = geo.node('file1')
        file.parm('file').set(hip_filename)
        file.parm('delayload').set(True)

        print( filename )
        print( hip_filename )
        print( name )
        print( object_id )
        print( wirecolor )
        print( handle )

    else:
        print('cannot import object from clipboad, wrong type!')
else:
    print('nothing to import')

