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
o = None
if len(hou.selectedNodes()) > 0:
    o = hou.selectedNodes()[0]

inputs = []
error_count = 0

if lines.count > 1:
    if lines[0] == '#material_export':
        for line in lines[1:]:
            ls = line.split(',', 1)
            if len(ls) == 2:
                parm_name = ls[0]
                parm_val = ls[1]

                if parm_val.startswith('\'') and parm_val.endswith('\''):
                    parm_val = parm_val[1:-1]

                elif parm_val.startswith('Color'):
                    parm_val = eval(parm_val[5:])

                elif parm_val.startswith('AColor'):
                    parm_val = eval(parm_val[6:])

                elif parm_val.startswith('@'):
                    pass

                elif parm_val.startswith('Transform'):
                    pass

                else:
                    parm_val = eval(parm_val)

                if parm_name == 'type':
                    type = 'VRayNode' + parm_val
                    o = None

                elif parm_name == 'name':
                    name = parm_val

                    if o == None:
                        try:
                            parent = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor).pwd()
                            if parent != None:
                                o = parent.createNode(type)

                                try:
                                    o.setName(name)
                                except:
                                    print('cannot setting name: ' + name)

                                o.moveToGoodPosition()
                                o.setSelected(True, True)
                        except:
                            print('cannot create node type: ' + type)

                    else:
                        if o.type().name() != type:
                            o.changeNodeType(type)
                        if o.name() != name:
                            o.setName(name)



                elif parm_name == 'uvw_transform':
                    pass

                elif (str(parm_val)).startswith('@'):
                    inputs.append((name, parm_name, parm_val[1:]))

                else:
                    try:
                        # if type(parm_val).__name__ == 'tuple':
                        #    o.parmTuple(parm_name).set(parm_val)
                        #    pass
                        # else:
                        #    o.parm(parm_name).set(parm_val)
                        if isinstance(parm_val, tuple):
                            o.parm(parm_name + 'r').set(parm_val[0])
                            o.parm(parm_name + 'g').set(parm_val[1])
                            o.parm(parm_name + 'b').set(parm_val[2])
                            if len(parm_val) == 4:
                                o.parm(parm_name + 'a').set(parm_val[3])
                        else:
                            o.parm(parm_name).set(parm_val)



                    except Exception, e:
                        # print(str(e))
                        print('cannot setting value: ' + str(
                            parm_val) + ' on parameter: ' + parm_name + ' on node: ' + o.name())
                        error_count += 1

        parent = hou.ui.paneTabOfType(hou.paneTabType.NetworkEditor).pwd()

        for input in inputs:
            #(name, parm_name, parm_val)
            node = parent.node(input[0])
            input_index = node.inputIndex(input[1])
            input_node = parent.node(input[2])
            node.setInput(input_index, input_node)

        parent.layoutChildren()

        if error_count > 0:
            print('material imported with: ' + str(error_count) + ' errors')
        else:
            print('material successfully imported')
    else:
        print('cannot apply clipboad values, wrong type!')
else:
    print('nothing to import')
