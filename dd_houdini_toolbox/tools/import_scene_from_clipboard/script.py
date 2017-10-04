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
        content = re.sub(re.compile("//.*?\n"), "", content_file.read())  # load content without comments

    matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)

    error_count = 0

    black_listed_parms = ('roughness_model', 'option_use_roughness', 'subdivs_as_samples')

    for matchNum, match in enumerate(matches):
        # print 'match:' + match.group(1).strip()
        type = match.group(1).strip()

        if type != 'SettingsRTEngine' and not type.startswith(
                'RenderChannel') and type != 'GeomStaticMesh' and type != 'Node' and not type.startswith(
            'Light') and not type.startswith('Settings') and type != 'FilterLanczos' and not type.startswith(
            'Camera') and type != 'RenderView':

            name = match.group(2).strip().replace('@', '_').replace('__', '_')
            split = match.group(3).split(';')
            parms = list()
            for p in (i for i in split if i.strip() != ''):
                parm = p.strip().split('=', 1)
                parm_name = parm[0]
                parm_val = parm[1]

                if type == 'BRDFBump' and parm_name == 'bump_tex':
                    parm_name = 'bump_tex_color' # ou 'bump_tex_float' je sais pas trop...

                if (parm_val).__contains__('@') or parm_val.__contains__('bitmapBuffer') or parm_val.startswith('List'):

                    if type == 'MtlMulti' and parm_name == 'mtls_list':

                        mtls_list = (re.match(r"List\((.*?)\)", parm_val, re.MULTILINE | re.DOTALL)).group(1).replace(
                            '@', '_').replace('__', '_').replace(' ', '').replace('\n', '').split(',')
                        parms.append({'Name': 'mtl_count', 'Value': len(mtls_list)})
                        for i in range(0, len(mtls_list)):
                            if mtls_list[i] != '0':
                                connections.append({'From': name, 'Input': 'mtl_' + str(i + 1), 'To': mtls_list[i]})

                    elif type == 'BRDFLayered':
                        if parm_name == 'brdfs':
                            brdfs = (re.match(r"List\((.*?)\)", parm_val, re.MULTILINE | re.DOTALL)).group(
                                1).replace(
                                '@', '_').replace('__', '_').replace(' ', '').replace('\n', '').split(',')[::-1]  # reversed
                            parms.append({'Name': 'brdf_count', 'Value': len(brdfs)})
                            for i in range(0, len(brdfs)):
                                connections.append({'From': name, 'Input': 'brdf_' + str(i + 1), 'To': brdfs[i]})

                        elif parm_name == 'weights':
                            weights = (re.match(r"List\((.*?)\)", parm_val, re.MULTILINE | re.DOTALL)).group(
                                1).replace(
                                '@', '_').replace('__', '_').replace(' ', '').replace('\n', '').split(',')[::-1]  # reversed
                            for i in range(0, len(weights)):
                                connections.append({'From': name, 'Input': 'weight_' + str(i + 1), 'To': weights[i]})
                    else:
                        connections.append({'From': name, 'Input': parm_name, 'To': parm_val.replace('@', '_').replace('__', '_')})
                else:

                    if any(n in parm_name for n in black_listed_parms) or parm_val.startswith(
                            'Transform') or parm_val.startswith('interpolate') or parm_val.startswith(
                                'Matrix' or parm_val.startswith('List')):

                        print 'parameter type: ' + parm_name + ' ingnored'


                    else:
                        try:
                            if parm_val.startswith('\"') and parm_val.endswith('\"'):
                                parm_val = parm_val[1:-1]
                                if type == 'UVWGenEnvironment' and parm_name == 'mapping_type':
                                    if parm_val == 'mirror_ball':
                                        parm_val = 3
                                    if parm_val == 'cubic':
                                        parm_val = 1
                                    if parm_val == 'angular':
                                        parm_val = 3
                                    if parm_val == 'spherical_vray':
                                        parm_val = 6

                            elif parm_val.startswith('Color'):
                                parm_val = hou.Vector3(eval(parm_val[5:]))

                            elif parm_val.startswith('AColor'):
                                parm_val = hou.Vector4(eval(parm_val[6:]))

                            else:
                                parm_val = eval(parm_val)

                        except:
                            print 'cannot setting value: ' + str(
                                parm_val) + ' on parameter: ' + parm_name + ' on node: ' + name
                            error_count += 1

                        parms.append({'Name': parm_name, 'Value': parm_val})

            plugins.append({'Type': 'VRayNode' + type, 'Name': name, 'Parms': parms})

        else:
            print 'node type: ' + type + ' ingnored'

    return error_count


shop = hou.node('/shop')
clipboard = QtWidgets.QApplication.clipboard()
text = clipboard.text()
lines = text.splitlines()

plugins = list()
connections = list()

error_count = 0

if lines.count > 1:
    if lines[0] == '#scene_export':
        for line in lines[1:]:
            ls = line.split(',', 1)
            if len(ls) == 2:
                if ls[0] == 'filename':
                    error_count += parse_vrscene_file(ls[1], plugins, connections)

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
        print 'cannot setting value: ' + str(
            parm_val) + ' on parameter: ' + parm_name + ' on node: ' + node.name()  # + ' ( ' + node.type().name() + ' ) '
        error_count += 1
    return error_count


for plugin in plugins:
    node = None

    try:
        node = mat.createNode(plugin['Type'])
    except:
        print('cannot creating node type: ' + plugin['Type'])
        error_count += 1
    if node != None:
        try:
            node.setName(plugin['Name'])
        except:
            print('cannot setting name: ' + plugin['Name'])
            error_count += 1

        for parm in plugin['Parms']:
            error_count += trySetParm(node, parm['Name'], parm['Value'])


def trySetInput(node, input, input_node):
    error_count = 0
    input_index = None

    try:
        input_index = node.inputIndex(input)
    except:
        print 'cannot find input: ' + str(input) + ' on node: ' + node.name()
        error_count += 1

    if input_index != None:
        try:
            node.setInput(input_index, input_node)
        except:
            print 'cannot set input: ' + str(input) + ' from node: ' + node.name() + ' to node: ' + input_node.name()
            error_count += 1

    return error_count


for connection in connections:
    node = mat.node(connection['From'])
    input_node = mat.node(connection['To'])
    input = connection['Input']

    if connection['Input'] == 'normal_uvwgen':
        # input_node.destroy()
        error_count += trySetInput(node, input, input_node)  # temp
    else:
        if node != None and input_node != None:

            if input_node.type().name() == 'VRayNodeTexCombineFloat':
                colortofloat = input_node.createOutputNode('VRayNodeTexColorToFloat')
                error_count += trySetInput(node, input, colortofloat)
            else:
                error_count += trySetInput(node, input, input_node)

material_output = mat.node('vray_material_output1')
if material_output == None:
    material_output = mat.createNode('vray_material_output')

for child in (c for c in mat.children() if
              len(c.outputConnections()) == 0 and c.name().__contains__(
                  '_mtl_')):  # and c.type().name() != 'vray_material_output'):
    # material_output.setInput(0, child)
    error_count += trySetInput(material_output, 'Material', child)

mat.layoutChildren()

if error_count > 0:
    print('material imported with: ' + str(error_count) + ' errors')
else:
    print('material successfully imported')
