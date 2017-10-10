import hou
import re

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    from Qt import QtWidgets, QtCore, QtGui

global re, setTimelineRange, parse_vrscene_file, import_scene_from_clipboard, get_vray_rop_node, try_parse_parm_value, normalize_name, try_set_parm, load_settings, load_cameras, load_lights, load_render_channels, get_render_channels_container, load_nodes, load_materials, try_set_input, get_material_output, add_plugin_node, revert_parms_to_default, load_environments, get_environment_settings, find_or_create_user_color


def parse_vrscene_file(fname, plugins, cameras, lights, settings, renderChannels, nodes, environments):
    regex = r"(.*?)\ (.*?)\ {(.*?)\}"
    content = None

    with open(fname, 'r') as content_file:
        content = re.sub(re.compile("//.*?\n"), "", content_file.read())  # load content without comments

    matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)

    for matchNum, match in enumerate(matches):
        type = match.group(1).strip()

        # do not catch parameters from GeomStaticMesh !
        if type != 'GeomStaticMesh' and type != 'RenderView' and type != 'Filter':

            name = match.group(2).strip()
            parms = list()

            for p in (i for i in match.group(3).split(';') if i.strip() != ''):
                split = p.strip().split('=', 1)
                parm_name = split[0]
                parm_val = split[1]
                parms.append({'Name': parm_name, 'Value': parm_val})

            if type == 'Node':
                nodes.append({'Type': type, 'Name': name, 'Parms': parms})

            # catch vray environment
            elif 'SettingsEnvironment' in type:
                for p in parms:
                    if '_tex' in p['Name']:
                        environments.append(p)

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


def get_vray_rop_node():
    from vfh import vfh_rop

    vray_rop = vfh_rop._getVrayRop()

    if vray_rop == None:
        out = hou.node('/out')
        vray_rop = out.createNode('vray_renderer')

    return vray_rop


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

        elif parm_val.startswith('Transform'):
            # Transform(Matrix(Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1)), Vector(0, 0, 0))
            result = re.match(r"Transform\(Matrix\((.*?.*)\), (.*?.*)\)", parm_val)
            result = (hou.Matrix3(eval('(' + result.group(1).replace('Vector', '') + ')')),
                      hou.Vector3(eval(result.group(2).replace('Vector', ''))))
            print result

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
        if not '@' in str(parm_val) and not 'bitmapBuffer' in str(parm_val):
            message_stack.append('Warning - cannot parsing value: ' + str(
                parm_val) + ' on parameter: ' + parm_name + ' on node: ' + name)

    return result


def try_set_parm(node, parm_name, parm_val, message_stack):
    global black_listed_parms

    if not parm_name in black_listed_parms:
        try:
            if isinstance(parm_val, hou.Vector3) or isinstance(parm_val, hou.Vector4):
                node.parmTuple(parm_name).set(parm_val)
            else:
                node.parm(parm_name).set(parm_val)

        except:
            message_stack.append('Cannot set parm on ' + node.name() + ' ' + parm_name + ' = ' + str(
                parm_val))


def setTimelineRange(start, end):
    setGobalFrangeExpr = 'tset `(%d-1)/$FPS` `%d/$FPS`' % (start, end)
    hou.hscript(setGobalFrangeExpr)
    hou.playbar.setPlaybackRange(start, end)


def load_settings(settings):
    # loading settings
    message_stack = list()

    vray_rop = get_vray_rop_node()
    revert_parms_to_default(vray_rop.parms(),
                            ('render_camera', 'render_network_render_channels', 'render_network_environment'))

    print '\n\n\n#############################################'
    print '#########  LOADING RENDER SETTINGS  #########'
    print '#############################################\n\n'

    for s in settings:
        for p in s['Parms']:
            parm_name = p['Name']
            parm_val = try_parse_parm_value(s['Name'], parm_name, p['Value'], message_stack)

            if s['Type'] == 'CustomSettings':
                print parm_name + " = " + str(parm_val)

                if parm_name == 'camera':
                    if parm_val != '':
                        try_set_parm(vray_rop, 'render_camera', '/obj/' + parm_val, message_stack)
                elif parm_name == 'fps':
                    hou.setFps(parm_val)
                elif parm_name == 'range':
                    setTimelineRange(parm_val[0], parm_val[1])

            else:
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

    vray_rop = get_vray_rop_node()
    render_channels_rop = hou.node(vray_rop.parm('render_network_render_channels').eval())

    if render_channels_rop == None:
        out = hou.node('/out')
        render_channels_rop = out.createNode('vray_render_channels', 'render_elements')
        render_channels_rop.moveToGoodPosition()
        vray_rop.parm('render_network_render_channels').set(render_channels_rop.path())

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
            revert_parms_to_default(render_channel.parms())

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


def load_nodes(nodes, materials):
    # loading nodes
    message_stack = list()
    obj = hou.node('/obj')

    print '\n\n\n#############################################'
    print '###########  LOADING SCENE NODES  ###########'
    print '#############################################\n\n'

    for n in nodes:
        name = n['Name'].split('@', 1)[0]
        material = n['Parms'][[i for i, s in enumerate(n['Parms']) if 'material' in s['Name']][0]]['Value']

        material_name = normalize_name(material.split('@', 1)[0])
        materials.append({'Name': material_name, 'Codename': material})

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


def get_material_output(material):
    material_output = None
    result = [child for child in material.children() if child.type().name() == 'vray_material_output']
    if len(result) > 0:
        material_output = result[0]
    else:
        material_output = material.createNode('vray_material_output')
        material_output.moveToGoodPosition()
    return material_output


def revert_parms_to_default(parms, exclude_parm_list=()):
    for i in range(len(parms), 0, -1):
        if not parms[i - 1].name() in exclude_parm_list:
            parms[i - 1].revertToDefaults()


def try_set_input(output_node, input_name, node, message_stack):
    input_index = output_node.inputIndex(input_name)

    if input_index != -1:
        try:
            output_node.setInput(input_index, node)
        except:
            message_stack.append('cannot set input: ' + str(
                input_name) + ' from node: ' + output_node.name() + ' to node: ' + node.name())
    else:
        message_stack.append('cannot find input: ' + str(input_name) + ' on node: ' + output_node.name())


def add_plugin_node(plugins, material, output_node, input_name, node_name, node_type, node_parms, message_stack):
    node = material.node(normalize_name(node_name))
    if node == None:
        node = material.createNode('VRayNode' + node_type)
        node.setName(normalize_name(node_name))
    else:
        revert_parms_to_default(node.parms())

    try_set_input(output_node, input_name, node, message_stack)

    print '\n\n( ' + normalize_name(node_name) + ' )'

    for p in node_parms:
        parm_name = p['Name']
        parm_val = p['Value']
        parm_val = try_parse_parm_value(node_name, parm_name, p['Value'], message_stack)

        if node_type == 'BRDFBump' and parm_name == 'bump_tex':
            parm_name = 'bump_tex_color'  # to test !...

        if node_type == 'UVWGenChannel' and parm_name == 'uvw_transform':
            matrix4 = hou.Matrix4(parm_val[0])
            result = matrix4.explode(transform_order='srt', rotate_order='xyz', pivot=parm_val[1])

            xform = material.node(output_node.name() + '_makexform')
            if xform == None:
                xform = material.createNode('makexform')
                xform.setName(output_node.name() + '_makexform')

            try_set_parm(xform, 'trans', result['translate'], message_stack)
            try_set_parm(xform, 'rot', result['rotate'], message_stack)
            try_set_parm(xform, 'scale', result['scale'], message_stack)
            try_set_parm(xform, 'pivot', result['shear'], message_stack)

            try_set_input(node, 'uvw_transform', xform, message_stack)

        elif node_type == 'MtlMulti':

            if parm_name == 'mtls_list':

                # insert mtlid_gen // necessary for material_ids generation
                mtlid_gen = material.node(output_node.name() + '_mtlid_gen')
                if mtlid_gen == None:
                    mtlid_gen = node.insertParmGenerator('mtlid_gen', hou.vopParmGenType.Parameter, False)
                    mtlid_gen.setName(output_node.name() + '_mtlid_gen')

                try_set_parm(node, 'mtl_count', len(parm_val), message_stack)

                for i in range(0, len(parm_val)):
                    for nn in plugins:
                        if nn['Name'] == parm_val[i]:
                            add_plugin_node(plugins, material, node, 'mtl_' + str(i + 1), nn['Name'], nn['Type'],
                                            nn['Parms'], message_stack)

            elif parm_name == 'ids_list':

                pass

        elif node_type == 'BRDFLayered':

            if parm_name == 'brdfs':

                try_set_parm(node, 'brdf_count', len(parm_val), message_stack)

                parm_val = parm_val[::-1]  # reversed

                for i in range(0, len(parm_val)):
                    for nn in plugins:
                        if nn['Name'] == parm_val[i]:
                            add_plugin_node(plugins, material, node, 'brdf_' + str(i + 1), nn['Name'], nn['Type'],
                                            nn['Parms'], message_stack)

            elif parm_name == 'weights':

                parm_val = parm_val[::-1]  # reversed

                for i in range(0, len(parm_val)):
                    for nn in plugins:
                        if nn['Name'] == parm_val[i]:
                            add_plugin_node(plugins, material, node, 'weight_' + str(i + 1), nn['Name'], nn['Type'],
                                            nn['Parms'], message_stack)

        elif '@' in str(parm_val) or 'bitmapBuffer' in str(parm_val):
            for nn in plugins:
                if nn['Name'] == str(parm_val):
                    add_plugin_node(plugins, material, node, parm_name, nn['Name'], nn['Type'], nn['Parms'],
                                    message_stack)

        else:

            print parm_name + " = " + str(parm_val)
            try_set_parm(node, parm_name, parm_val, message_stack)


def load_materials(plugins, materials):
    # loading materials
    message_stack = list()
    shop = hou.node('/shop')

    print '\n\n\n#############################################'
    print '#########  LOADING SCENE MATERIALS  #########'
    print '#############################################\n\n'

    for m in materials:

        material = shop.node(m['Name'])
        if material == None:
            material = shop.createNode('vray_material')
            for n in material.children(): n.destroy()
            material.setName(m['Name'])
            material.moveToGoodPosition()

        for n in plugins:
            if n['Name'] == m['Codename']:
                material_output = get_material_output(material)
                input_name = 'Material'

                add_plugin_node(plugins, material, material_output, input_name, n['Name'], n['Type'], n['Parms'],
                                message_stack)

                material.layoutChildren()

                break

    if len(message_stack) != 0:
        print '\n\n\nLoad Scene materials terminated with: ' + str(len(message_stack)) + ' errors:\n'

    for m in message_stack:
        print m


def get_environment_settings(environment_rop):
    render_environment = None
    result = [child for child in environment_rop.children() if
              child.type().name() == 'VRayNodeSettingsEnvironment']

    if len(result) > 0:
        render_environment = result[0]
    else:
        render_environment = environment_rop.createNode('VRayNodeSettingsEnvironment')
        render_environment.moveToGoodPosition()
    return render_environment


def find_or_create_user_color(environment_settings, environment_rop, parm_name, parm_val, message_stack):
    user_color = None

    for child in environment_rop.children():
        if child.type().name() == 'VRayNodeTexUserColor':
            if hou.Vector4(child.parmTuple('default_color').eval()) == parm_val:
                user_color = child
                break

    if user_color == None:
        user_color = environment_rop.createNode('VRayNodeTexUserColor')
        try_set_parm(user_color, 'default_color', parm_val, message_stack)

    try_set_input(environment_settings, parm_name, user_color, message_stack)


def load_environments(plugins, environments):
    # loading environment
    message_stack = list()

    vray_rop = get_vray_rop_node()
    environment_rop = hou.node(vray_rop.parm('render_network_environment').eval())

    if environment_rop == None:
        out = hou.node('/out')
        environment_rop = out.createNode('vray_environment', 'env')
        environment_rop.moveToGoodPosition()
        vray_rop.parm('render_network_environment').set(environment_rop.path())

    environment_settings = get_environment_settings(environment_rop)

    print '\n\n\n#############################################'
    print '########  LOADING SCENE ENVIRONMENT  ########'
    print '#############################################\n\n'

    for p in environments:
        parm_name = p['Name']
        parm_val = try_parse_parm_value(environment_settings, parm_name, p['Value'], message_stack)
        print parm_name + " = " + str(parm_val)
        if isinstance(parm_val, hou.Vector4):
            find_or_create_user_color(environment_settings, environment_rop, parm_name, parm_val, message_stack)

    print '\n\n'

    environment_rop.layoutChildren()


    if len(message_stack) != 0:
        print '\n\n\nLoad Scene environment terminated with: ' + str(len(message_stack)) + ' errors:\n'

    for m in message_stack:
        print m


def import_scene_from_clipboard():
    clipboard = QtWidgets.QApplication.clipboard()
    text = clipboard.text()
    lines = text.splitlines()

    plugins = list()
    cameras = list()
    lights = list()
    settings = list()
    renderChannels = list()
    nodes = list()
    materials = list()
    environments = list()

    global black_listed_parms
    black_listed_parms = (
        'roughness_model', 'option_use_roughness', 'subdivs_as_samples', 'enableDeepOutput', 'adv_exposure_mode',
        'adv_printer_lights_per')

    # clear console
    print '\n' * 5000

    if lines.count > 1:
        if lines[0] == '#scene_export':

            for line in lines[1:]:
                ls = line.split(',', 1)
                if len(ls) == 2:
                    if ls[0] == 'filename':
                        parse_vrscene_file(ls[1], plugins, cameras, lights, settings, renderChannels, nodes,
                                           environments)

                        load_settings(settings)
                        load_render_channels(renderChannels)
                        # load_cameras(cameras)
                        # load_lights(lights)
                        load_nodes(nodes, materials)
                        load_materials(plugins, materials)
                        load_environments(plugins, environments)

            print '\nScene import finished'

        else:
            print '\nNothing to import...'


import_scene_from_clipboard()
