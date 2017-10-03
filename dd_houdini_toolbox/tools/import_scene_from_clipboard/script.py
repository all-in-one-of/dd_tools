import hou

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    from Qt import QtWidgets, QtCore, QtGui

'''elif parm_val.startswith('Transform'):
    match2 = re.match(r"Transform\(Matrix\(Vector(.*?), Vector(.*?), Vector(.*?)\), Vector(.*?.*)\)",
                      parm_val)
    trans = hou.Vector3(eval(match2.group(1)))
    rot = hou.Vector3(eval(match2.group(2)))
    scale = hou.Vector3(eval(match2.group(3)))
    pivot = hou.Vector3(eval(match2.group(4)))
    plugins.append({'Type': 'makexform', 'Name': name + '_makexform', 'Parms': (
        {'Name': 'trans', 'Value': trans}, {'Name': 'rot', 'Value': rot},
        {'Name': 'scale', 'Value': scale},
        {'Name': 'pivot', 'Value': pivot})})
    connections.append({'From': name, 'Input': parm_name, 'To': name + '_makexform'})

elif parm_val.startswith('interpolate'):
    pass'''


def parse_vrscene_file(fname, plugins, connections):
    import re

    regex = r"(.*?)\ (.*?)\ {(.*?)\}"
    content = ''

    with open(fname, 'r') as content_file:
        content = content_file.read()

    matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)
    for matchNum, match in enumerate(matches):
        type = 'VRayNode' + match.group(1).strip()
        name = match.group(2).strip().replace('@', '_')
        split = match.group(3).split(';')
        parms = list()
        for p in (i for i in split if i.strip() != ''):
            parm = p.strip().split('=', 1)
            parm_name = parm[0]
            parm_val = parm[1]

            if (parm_val).__contains__('@') or parm_val.__contains__('bitmapBuffer'):
                connections.append({'From': name, 'Input': parm_name, 'To': parm_val.replace('@', '_')})
            else:

                if parm_val.startswith('Transform') or parm_val.startswith('interpolate'):
                    pass

                else:
                    try:
                        if parm_val.startswith('\"') and parm_val.endswith('\"'):
                            parm_val = parm_val[1:-1]

                        elif parm_val.startswith('Color'):
                            parm_val = hou.Vector3(eval(parm_val[5:]))

                        elif parm_val.startswith('AColor'):
                            parm_val = hou.Vector4(eval(parm_val[6:]))

                        else:
                            parm_val = eval(parm_val)

                    except:
                        print 'cannot evaluate parm: ' + parm_val

                    parms.append({'Name': parm_name, 'Value': parm_val})

        plugins.append({'Type': type, 'Name': name, 'Parms': parms})


shop = hou.node('/shop')
clipboard = QtWidgets.QApplication.clipboard()
text = clipboard.text()
lines = text.splitlines()

plugins = list()
connections = list()

error_count = 0

if lines.count > 1:
    if lines[0] == '#material_export':
        for line in lines[1:]:
            ls = line.split(',', 1)
            if len(ls) == 2:
                if ls[0] == 'filename':
                    parse_vrscene_file(ls[1], plugins, connections)

mat = shop.createNode('vray_material')
mat.node('VRayNodeBRDFVRayMtl1').destroy()


def trySetParm(node, parm_name, parm_val):
    error_count = 0
    try:
        '''isinstance(parm_val, hou.Color) or'''
        if isinstance(parm_val, hou.Vector3) or isinstance(parm_val, hou.Vector4):
            node.parmTuple(parm_name).set(parm_val)
        else:
            node.parm(parm_name).set(parm_val)

    except:
        print('cannot setting value: ' + str(parm_val) + ' on parameter: ' + parm_name + ' on node: ' + node.name())
        error_count += 1
    return error_count


for plugin in plugins:
    node = mat.createNode(plugin['Type'])
    try:
        node.setName(plugin['Name'])
    except:
        print('cannot setting name: ' + plugin['Name'])
        error_count += 1

    for parm in plugin['Parms']:
        error_count += trySetParm(node, parm['Name'], parm['Value'])

for connection in connections:
    node = mat.node(connection['From'])
    input_node = mat.node(connection['To'])
    input_index = node.inputIndex(connection['Input'])

    if connection['Input'] == 'normal_uvwgen':
        input_node.destroy()

    else:

        if input_node.type().name() == 'VRayNodeTexCombineFloat':
            colortofloat = input_node.createOutputNode('VRayNodeTexColorToFloat')
            node.setInput(input_index, colortofloat)
        else:
            node.setInput(input_index, input_node)

material_output = mat.node('vray_material_output1')
if material_output == None:
    material_output = mat.createNode('vray_material_output')

for child in (c for c in mat.children() if
              len(c.outputConnections()) == 0 and c.name().__contains__(
                  '_mtl_')):  # and c.type().name() != 'vray_material_output'):
    material_output.setInput(0, child)

mat.layoutChildren()

if error_count > 0:
    print('material imported with: ' + str(error_count) + ' errors')
else:
    print('material successfully imported')
