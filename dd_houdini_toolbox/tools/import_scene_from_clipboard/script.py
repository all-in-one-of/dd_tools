import hou
import re

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    from Qt import QtWidgets, QtCore, QtGui

# black_listed_parms = ('roughness_model', 'option_use_roughness', 'subdivs_as_samples')

global re, parse_vrscene_file, import_scene_from_clipboard, get_vray_rop_node, try_parse_parm_value, normalize_name, try_set_parm, load_settings, load_cameras, load_lights, load_render_channels, get_render_channels_container, load_nodes, load_materials, try_set_input, get_material_output


def parse_vrscene_file(fname, plugins, cameras, lights, settings, renderChannels, nodes):
    regex = r"(.*?)\ (.*?)\ {(.*?)\}"
    content = None

    with open(fname, 'r') as content_file:
        content = re.sub(re.compile("//.*?\n"), "", content_file.read())  # load content without comments

    matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)

    for matchNum, match in enumerate(matches):
        type = match.group(1).strip()

        # do not catch parameters from GeomStaticMesh !
        if type != 'GeomStaticMesh' and type != 'RenderView' and type != 'Filter' and type != 'SettingsEnvironment':

            name = match.group(2).strip()
            parms = list()

            for p in (i for i in match.group(3).split(';') if i.strip() != ''):
                split = p.strip().split('=', 1)
                parm_name = split[0]
                parm_val = split[1]
                parms.append({'Name': parm_name, 'Value': parm_val})

            if type == 'Node':
                nodes.append({'Type': type, 'Name': name, 'Parms': parms})

            # catch vray render channels
            elif 'RenderChannel' in type:
                renderChannels.append({'Type': type, 'Name': name, 'Parms': parms})

            # catch vray render settings
            elif 'Settings' in type:
                settings.append({'Type': type, 'Name': name, 'Parms': parms})

            # catch lights
            elif 'Light' in type:
                lights.append({'Type': type, 'Name': name, 'Parms': parms})

            # catch cameras
            elif 'Camera' in type:
                cameras.append({'Type': type, 'Name': name, 'Parms': parms})

            else:
                # plugins.append({'Type': 'VRayNode' + type, 'Name': name, 'Parms': parms})
                plugins.append({'Type': type, 'Name': name, 'Parms': parms})


def normalize_name(name):
    return "_".join(filter(None, name.replace('@', '_').split('_')))


def get_vray_rop_node(message_stack):
    from vfh import vfh_rop

    vrayRopNode = vfh_rop._getVrayRop()

    if vrayRopNode == None:
        message_stack.append('Warning - cannot find vray rop node...')

    return vrayRopNode


def try_parse_parm_value(name, parm_name, parm_val, message_stack):
    result = parm_val

    try:
        if parm_val.startswith('"') and parm_val.endswith('"'):
            result = parm_val[1:-1]
            if type == 'UVWGenEnvironment' and parm_name == 'mapping_type':
                if parm_val == 'mirror_ball':
                    result = 3
                if parm_val == 'cubic':
                    result = 1
                if parm_val == 'angular':
                    result = 3
                if parm_val == 'spherical_vray':
                    result = 6

        elif parm_val.startswith('Color'):
            result = hou.Vector3(eval(parm_val[5:]))

        elif parm_val.startswith('AColor'):
            result = hou.Vector4(eval(parm_val[6:]))

        elif parm_val.startswith('ListInt'):
            result = (re.match(r"ListInt\((.*?)\)", parm_val, re.MULTILINE | re.DOTALL)).group(
                1).replace(' ', '').replace('\n', '').split(',')

        elif parm_val.startswith('List'):
            result = (re.match(r"List\((.*?)\)", parm_val, re.MULTILINE | re.DOTALL)).group(
                1).replace(' ', '').replace('\n', '').split(',')

        elif parm_val.startswith('Vector'):
            result = hou.Vector3(eval(parm_val[6:]))

        else:
            result = eval(parm_val)

    except:

        message_stack.append('Warning - cannot evaluating value: ' + str(
            parm_val) + ' on parameter: ' + parm_name + ' on node: ' + name)

    return result


def try_set_parm(node, parm_name, parm_val, message_stack):
    try:
        if isinstance(parm_val, hou.Vector3) or isinstance(parm_val, hou.Vector4):
            node.parmTuple(parm_name).set(parm_val)
        else:
            node.parm(parm_name).set(parm_val)

    except:
        message_stack.append('Cannot set parm on ' + node.name() + ' ' + parm_name + ' = ' + str(
            parm_val))


def load_settings(settings):
    # loading settings
    message_stack = list()
    vray_rop = get_vray_rop_node(message_stack)

    if vray_rop == None:
        out = hou.node('/out')
        vray_rop = out.createNode('vray_renderer')
    else:
        for p in (vray_rop.parms()):
            p.revertToDefaults()

        print '\n\n\n#############################################'
        print '#########  LOADING RENDER SETTINGS  #########'
        print '#############################################\n\n'

        for s in settings:
            for p in s['Parms']:
                parm_name = p['Name']
                parm_val = try_parse_parm_value(s['Name'], parm_name, p['Value'], message_stack)

                print s['Type'] + '_' + parm_name + " = " + str(parm_val)
                try_set_parm(vray_rop, s['Type'] + '_' + parm_name, parm_val, message_stack)

    if len(message_stack) != 0:
        print '\n\n\nLoad Render Settings terminated with: ' + str(len(message_stack)) + ' errors:\n'

    for m in message_stack:
        print m


def load_cameras(cameras):
    # loading settings
    message_stack = list()
    obj = hou.node('/obj')

    print '\n\n\n#############################################'
    print '#############  LOADING CAMERAS  #############'
    print '#############################################\n\n'

    for c in cameras:
        name = c['Name'].split('@', 1)[0]

        print name + " ( " + c['Type'] + ' ) \n'

        '''for p in c['Parms']:
            parm_name = p['Name']
            parm_val = try_parse_parm_value(c['Name'], parm_name, p['Value'], message_stack)

            print c['Type'] + '_' + parm_name + " = " + str(parm_val)
            try_set_parm(vray_rop, s['Type'] + '_' + parm_name, parm_val, message_stack)'''

        print '\n\n'

    if len(message_stack) != 0:
        print '\n\n\nLoad cameras terminated with: ' + str(len(message_stack)) + ' errors:\n'

    for m in message_stack:
        print m


def load_lights(lights):
    # loading settings
    message_stack = list()
    obj = hou.node('/obj')

    print '\n\n\n#############################################'
    print '##############  LOADING LIGHTS  #############'
    print '#############################################\n\n'

    for l in lights:
        name = l['Name'].split('@', 1)[0]

        # particular case for 'Max' types, need conversion
        if l['Type'] == 'LightOmniMax':
            l['Type'] = 'LightOmni'

        print name + " ( " + l['Type'] + ' ) \n'

        light = obj.node(name)
        if light == None:
            light = obj.createNode('VRayNode' + l['Type'])
            light.setName(name)

        for p in l['Parms']:
            parm_name = p['Name']
            parm_val = try_parse_parm_value(l['Name'], parm_name, p['Value'], message_stack)

            print l['Type'] + '_' + parm_name + " = " + str(parm_val)
            try_set_parm(light, parm_name, parm_val, message_stack)

        print '\n\n'

    if len(message_stack) != 0:
        print '\n\n\nLoad lights terminated with: ' + str(len(message_stack)) + ' errors:\n'

    for m in message_stack:
        print m


def get_render_channels_container(render_channels_rop):
    render_channel_container = None
    result = [child for child in render_channels_rop.children() if
              child.type().name() == 'VRayNodeRenderChannelsContainer']
    if len(result) > 0:
        render_channel_container = result[0]
    else:
        render_channel_container = render_channels_rop.createNode('VRayNodeRenderChannelsContainer')
        render_channel_container.moveToGoodPosition()
    return render_channel_container


def load_render_channels(renderChannels):
    # loading render channels
    message_stack = list()

    vray_rop = get_vray_rop_node(message_stack)
    render_channels_rop = hou.node(vray_rop.parm('render_network_render_channels').eval())

    if render_channels_rop == None:
        out = hou.node('/out')
        render_channels_rop = out.createNode('vray_render_channels', 'render_elements')
        render_channels_rop.moveToGoodPosition()

    render_channels_container = get_render_channels_container(render_channels_rop)

    print '\n\n\n#############################################'
    print '#########  LOADING RENDER CHANNELS  #########'
    print '#############################################\n\n'

    for s in renderChannels:

        name = s['Name'].split('@', 1)[0]

        print name + " ( " + s['Type'] + ' ) \n'

        render_channel = render_channels_rop.node(name)
        if render_channel == None:
            render_channel = render_channels_rop.createNode('VRayNode' + s['Type'])
            render_channel.setName(name)
            render_channels_container.setNextInput(render_channel)
        else:
            for p in (render_channel.parms()):
                p.revertToDefaults()

        for p in s['Parms']:
            parm_name = p['Name']
            parm_val = try_parse_parm_value(s['Name'], parm_name, p['Value'], message_stack)
            print parm_name + " = " + str(parm_val)
            try_set_parm(render_channel, parm_name, parm_val, message_stack)

        print '\n\n'

    render_channels_rop.layoutChildren()

    if len(message_stack) != 0:
        print '\n\n\nLoad Render Channels terminated with: ' + str(len(message_stack)) + ' errors:\n'

    for m in message_stack:
        print m


def load_nodes(nodes):
    # loading nodes
    message_stack = list()
    obj = hou.node('/obj')

    material_list = list()

    print '\n\n\n#############################################'
    print '###########  LOADING SCENE NODES  ###########'
    print '#############################################\n\n'

    for n in nodes:
        name = n['Name'].split('@', 1)[0]
        material = n['Parms'][[i for i, s in enumerate(n['Parms']) if 'material' in s['Name']][0]]['Value']

        material_name = normalize_name(material.split('@', 1)[0])
        material_list.append({'Name': material_name, 'Codename': material})

        node = obj.node(normalize_name(name))
        if node == None:
            node = obj.createNode('geo')
            node.setName(normalize_name(name))
            node.moveToGoodPosition()

        # here load corresponding .abc

        node.parm('shop_materialpath').set('/shop/' + material_name)

        print name + ' ( ' + material_name + ' )'

        '''for p in n['Parms']:
            parm_name = p['Name']
            parm_val = p['Value']'''

    if len(message_stack) != 0:
        print '\n\n\nLoad Scene Nodes terminated with: ' + str(len(message_stack)) + ' errors:\n'

    for m in message_stack:
        print m

    return material_list


def get_material_output(material):
    material_output = None
    result = [child for child in material.children() if child.type().name() == 'vray_material_output']
    if len(result) > 0:
        material_output = result[0]
    else:
        material_output = material.createNode('vray_material_output')
        material_output.moveToGoodPosition()
    return material_output


def try_set_input(node, input, input_node):
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


def load_materials(plugins, material_list):
    # loading materials
    message_stack = list()
    shop = hou.node('/shop')

    print '\n\n\n#############################################'
    print '#########  LOADING SCENE MATERIALS  #########'
    print '#############################################\n\n'

    for m in material_list:

        material = shop.node(m['Name'])
        if material == None:
            material = shop.createNode('vray_material')
            for n in material.children(): n.destroy()
            material.setName(m['Name'])
            material.moveToGoodPosition()

        for n in plugins:
            if n['Name'] == m['Codename']:

                node = material.node(normalize_name(n['Name']))
                if node == None:
                    node = material.createNode('VRayNode' + n['Type'])
                    node.setName(normalize_name(n['Name']))
                else:
                    for p in (node.parms()):
                        p.revertToDefaults()

                material_output = get_material_output(material)
                try_set_input(material_output, 'Material', node)

                for p in n['Parms']:
                    parm_name = p['Name']
                    parm_val = p['Value']

                    if '@' in parm_val or 'bitmapBuffer' in parm_val:
                        for nn in plugins:
                            if nn['Name'] == p['Name']:
                                pass

                    else:
                        parm_val = try_parse_parm_value(n['Name'], parm_name, p['Value'], message_stack)

                        print n['Type'] + '_' + parm_name + " = " + str(parm_val)
                        try_set_parm(node, parm_name, parm_val, message_stack)

                break

    if len(message_stack) != 0:
        print '\n\n\nLoad Scene materials terminated with: ' + str(len(message_stack)) + ' errors:\n'

    for m in message_stack:
        print m


def import_scene_from_clipboard():
    clipboard = QtWidgets.QApplication.clipboard()
    text = clipboard.text()
    lines = text.splitlines()

    plugins = list()
    connections = list()
    cameras = list()
    lights = list()
    settings = list()
    renderChannels = list()
    nodes = list()

    if lines.count > 1:
        if lines[0] == '#scene_export':
            for line in lines[1:]:
                ls = line.split(',', 1)
                if len(ls) == 2:
                    if ls[0] == 'filename':
                        parse_vrscene_file(ls[1], plugins, cameras, lights, settings, renderChannels, nodes)

                        load_settings(settings)
                        load_render_channels(renderChannels)
                        load_cameras(cameras)
                        load_lights(lights)
                        material_list = load_nodes(nodes)
                        load_materials(plugins, material_list)

            print '\nscene was successfully imported'

        else:
            print '\nnothing to import...'


import_scene_from_clipboard()
