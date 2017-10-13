import hou
import re
import os.path
import shutil

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    from Qt import QtWidgets, QtCore, QtGui

global re, setTimelineRange, parse_vrscene_file, import_scene_from_clipboard, get_vray_rop_node, try_parse_parm_value, normalize_name, try_create_node, try_set_parm, load_settings, load_cameras, load_lights, load_render_channels, get_render_channels_container, load_nodes, load_materials, try_set_input, get_material_output, add_plugin_node, revert_parms_to_default, load_environments, get_environment_settings, find_or_create_user_color, add_vray_objectid_param_template, add_scene_wirecolor_visualizer


def parse_vrscene_file(fname, plugins, cameras, lights, settings, renderChannels, nodes, environments, geometries):
    content = None

    with open(fname, 'r') as content_file:
        content = content_file.read()

    matches = re.finditer(r'\#include\ \"(.*?)\"\n', content, re.MULTILINE | re.DOTALL)
    for matchNum, match in enumerate(matches):
        fname = match.group(1).strip()

        if os.path.isfile(fname):
            with open(fname, 'r') as content_file:
                content += content_file.read()

    content = re.sub(re.compile('\#include\ \"(.*?)\"\n'), '', content)  # content without includes
    content = re.sub(re.compile('//.*?\n'), '', content)  # content without comments

    # print content

    matches = re.finditer(r'(.*?)\ (.*?)\ \{(.*?)\}', content, re.MULTILINE | re.DOTALL)

    for matchNum, match in enumerate(matches):
        type = match.group(1).strip()

        # do not catch parameters from GeomStaticMesh !
        if type != 'GeomStaticMesh' and type != 'RenderView' and type != 'Filter':

            name = match.group(2).strip()
            parms = list()

            for p in (i for i in match.group(3).split(';') if i.strip() != ''):
                split = p.strip().split('=', 1)
                if len(split) == 2:
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

            # catch geometries
            elif 'Geometry' in type:
                geometries.append({'Type': type, 'Name': name, 'Parms': parms})

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


def try_create_node(parent, type, name, message_stack):
    node = None
    old_node = parent.node(name)

    try:
        node = parent.createNode(type)
        if old_node != None:
            node.setPosition(old_node.position())
        else:
            node.moveToGoodPosition()
    except:
        message_stack.append('cannot create node name:' + name + ' type: ' + str(type))

    if node != None:
        if old_node != None:
            old_node.destroy()
        try:
            node.setName(name)
        except:
            message_stack.append('cannot set name:' + name)

    return node


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

    for child in render_channels_rop.children():
        if child.type().name() != 'VRayNodeRenderChannelsContainer':
            child.destroy()

    render_channels_container = get_render_channels_container(render_channels_rop)

    print '\n\n\n#############################################'
    print '#########  LOADING RENDER CHANNELS  #########'
    print '#############################################\n\n'

    for s in renderChannels:

        name = s['Name'].split('@', 1)[0]
        type = s['Type']

        print name + " ( " + s['Type'] + ' ) \n'

        render_channel = try_create_node(render_channels_rop, 'VRayNode' + s['Type'], name, message_stack)

        if render_channel != None:
            render_channels_container.setNextInput(render_channel)

            for p in s['Parms']:
                parm_name = p['Name']
                parm_val = try_parse_parm_value(s['Name'], parm_name, p['Value'], message_stack)

                if type == 'RenderChannelColor' and parm_name == 'alias':
                    parm_val -= 100  # item numbering from max starts at 100

                if type == 'RenderChannelZDepth' and (parm_name == 'depth_black' or parm_name == 'depth_white'):
                    parm_val *= 0.01  # metric values ! need convertion

                print parm_name + " = " + str(parm_val)
                try_set_parm(render_channel, parm_name, parm_val, message_stack)

        print '\n\n'

    render_channels_rop.layoutChildren()

    if len(message_stack) != 0:
        print '\n\n\nLoad Render Channels terminated with: ' + str(len(message_stack)) + ' errors:\n'

    for m in message_stack:
        print m


def add_vray_objectid_param_template(geo):
    parm_group = geo.parmTemplateGroup()
    parm_folder = hou.FolderParmTemplate('folder', 'V-Ray Object')
    parm_folder.addParmTemplate(hou.IntParmTemplate('vray_objectID', 'Object ID', 1))
    parm_group.append(parm_folder)
    geo.setParmTemplateGroup(parm_group)


def add_scene_wirecolor_visualizer():
    if len([visualizer for visualizer in
            hou.viewportVisualizers.visualizers(category=hou.viewportVisualizerCategory.Scene) if
            visualizer.name() == 'wirecolor']) == 0:
        wirecolor_vis = hou.viewportVisualizers.createVisualizer(hou.viewportVisualizers.types()[1],
                                                                 category=hou.viewportVisualizerCategory.Scene)
        wirecolor_vis.setName('wirecolor')
        wirecolor_vis.setLabel('Wirecolor')
        wirecolor_vis.setParm('attrib', 'wirecolor')
        wirecolor_vis.setParm('class', 3)
        geoviewport = hou.ui.paneTabOfType(hou.paneTabType.SceneViewer).curViewport()
        wirecolor_vis.setIsActive(True, viewport=geoviewport)


def load_nodes(nodes, geometries, materials):
    # loading nodes
    message_stack = list()
    obj = hou.node('/obj')

    geo_dir = hou.expandString('$HIP') + '/geo/'

    print '\n\n\n#############################################'
    print '###########  LOADING SCENE NODES  ###########'
    print '#############################################\n\n'

    for n in nodes:
        name = n['Name'].split('@', 1)[0]
        material = n['Parms'][[i for i, s in enumerate(n['Parms']) if 'material' in s['Name']][0]]['Value']

        material_name = normalize_name(material.split('@', 1)[0])
        materials.append({'Name': material_name, 'Codename': material})

        # here search for the corresponding geometry
        geometry = None
        for g in geometries:
            if g['Name'] == name:
                geometry = g
                break

        # if geometry exists getting parameters...
        if geometry != None:
            geo = try_create_node(obj, 'geo', normalize_name(name), message_stack)

            if geo != None:
                for child in geo.children():
                    child.destroy()

                add_vray_objectid_param_template(geo)
                geo.parm('shop_materialpath').set('/shop/' + material_name)

            # retrieving geometry parameters
            from_filename = ''
            object_id = 0
            wirecolor = (0.5, 0.5, 0.5)
            handle = 0
            for p in geometry['Parms']:
                parm_name = p['Name']
                parm_val = p['Value']

                if parm_name == 'filename':
                    from_filename = try_parse_parm_value(name, parm_name, parm_val, message_stack)
                elif parm_name == 'object_id':
                    object_id = try_parse_parm_value(name, parm_name, parm_val, message_stack)
                elif parm_name == 'wirecolor':
                    wirecolor = try_parse_parm_value(name, parm_name, parm_val, message_stack)
                elif parm_name == 'handle':
                    handle = try_parse_parm_value(name, parm_name, parm_val, message_stack)

            # copy cache file from temp location to .hip/geo dir
            if os.path.isfile(from_filename):
                to_filename = geo_dir + name + ".abc"
                try:
                    # shutil.move(from_filename, to_filename)
                    shutil.copy(from_filename, to_filename)
                except IOError:
                    os.chmod(to_filename, 777)  # ?? still can raise exception
                    shutil.move(from_filename, to_filename)

            geo.parm('vray_objectID').set(object_id)
            geo.parm('use_dcolor').set(True)
            geo.parm('dcolorr').set(wirecolor[0])
            geo.parm('dcolorg').set(wirecolor[1])
            geo.parm('dcolorb').set(wirecolor[2])

            alembic = geo.node('alembic1')
            if alembic == None:
                alembic = geo.createNode('alembic')
            alembic.parm('fileName').set('$HIP/geo/' + name + ".abc")
            alembic.parm('reload').pressButton()

            xform = geo.node('xform1')
            if xform == None:
                xform = alembic.createOutputNode('xform', 'xform1')
            xform.parm('scale').set(0.01)

            properties = geo.node('properties')
            if properties == None:
                properties = xform.createOutputNode('attribwrangle', 'properties')
                properties.parm('class').set(0)
                properties.setDisplayFlag(True)

            properties.parm('snippet').set(
                'v@wirecolor = set(' + str(wirecolor[0]) + ', ' + str(wirecolor[1]) + ', ' + str(
                    wirecolor[2]) + ');\ni@handle = ' + str(handle) + ';')

            vraypoxy = geo.node('vrayproxy1')
            if vraypoxy == None:
                vraypoxy = geo.createNode('VRayNodeVRayProxy', 'vrayproxy1')
                vraypoxy.moveToGoodPosition()

            vraypoxy.parm('file').setExpression('chs("../alembic1/fileName")')
            vraypoxy.parm('reload').pressButton()
            vraypoxy.parm('scale').setExpression('ch("../xform1/scale")')
            vraypoxy.parm('first_map_channel').set(1)
            vraypoxy.setRenderFlag(True)

            geo.layoutChildren()

        print name + ' ( ' + material_name + ' )'

    add_scene_wirecolor_visualizer()

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


def add_plugin_node(plugins, parent, output_node, input_name, node_name, node_type, node_parms, message_stack):
    node = try_create_node(parent, 'VRayNode' + node_type, normalize_name(node_name), message_stack)

    print '\n\n( ' + normalize_name(node_name) + ' )'

    if node != None:

        try_set_input(output_node, input_name, node, message_stack)

        for p in node_parms:
            parm_name = p['Name']
            parm_val = p['Value']
            parm_val = try_parse_parm_value(node_name, parm_name, p['Value'], message_stack)

            if node_type == 'BRDFBump' and parm_name == 'bump_tex':
                parm_name = 'bump_tex_color'  # to test !...

            if node_type == 'BRDFVRayMtl' and parm_name == 'brdf_type':
                if parm_val == 4: parm_val = 3  # need this conversion because of the difference between max and houdini menu list

            if node_type == 'UVWGenChannel' and parm_name == 'uvw_transform':
                m4 = hou.Matrix4(parm_val[0])
                result = m4.explode(transform_order='trs', rotate_order='xyz', pivot=hou.Vector3(0.5, 0.5, 0)) #, pivot=parm_val[1])

                xform = parent.node(output_node.name() + '_makexform')
                if xform == None:
                    xform = parent.createNode('makexform')
                    xform.setName(output_node.name() + '_uvwgen_makexform')

                #try_set_parm(xform, 'trans', result['translate'], message_stack)
                try_set_parm(xform, 'trans', parm_val[1], message_stack)
                try_set_parm(xform, 'rot', result['rotate'], message_stack)
                try_set_parm(xform, 'scale', result['scale'], message_stack)
                try_set_parm(xform, 'pivot', result['shear'], message_stack)

                try_set_input(node, 'uvw_transform', xform, message_stack)

            elif node_type == 'MtlMulti':

                if parm_name == 'mtls_list':

                    # insert mtlid_gen // necessary for material_ids generation
                    mtlid_gen = parent.node(output_node.name() + '_mtlid_gen')
                    if mtlid_gen == None:
                        mtlid_gen = node.insertParmGenerator('mtlid_gen', hou.vopParmGenType.Parameter, False)
                        mtlid_gen.setName(output_node.name() + '_mtlid_gen')

                    try_set_parm(node, 'mtl_count', len(parm_val), message_stack)

                    for i in range(0, len(parm_val)):
                        for nn in plugins:
                            if nn['Name'] == parm_val[i]:
                                add_plugin_node(plugins, parent, node, 'mtl_' + str(i + 1), nn['Name'], nn['Type'],
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
                                add_plugin_node(plugins, parent, node, 'brdf_' + str(i + 1), nn['Name'], nn['Type'],
                                                nn['Parms'], message_stack)

                elif parm_name == 'weights':

                    parm_val = parm_val[::-1]  # reversed

                    for i in range(0, len(parm_val)):
                        for nn in plugins:
                            if nn['Name'] == parm_val[i]:
                                add_plugin_node(plugins, parent, node, 'weight_' + str(i + 1), nn['Name'], nn['Type'],
                                                nn['Parms'], message_stack)

            elif '@' in str(parm_val) or 'bitmapBuffer' in str(parm_val):
                for nn in plugins:
                    if nn['Name'] == str(parm_val):
                        add_plugin_node(plugins, parent, node, parm_name, nn['Name'], nn['Type'], nn['Parms'],
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

        material = try_create_node(shop, 'vray_material', normalize_name(m['Name']), message_stack)

        if material != None:
            for child in material.children():
                child.destroy()

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

    for child in environment_rop.children():
        if child.type().name() != 'VRayNodeSettingsEnvironment':
            child.destroy()

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

        for n in plugins:
            # print 'n[\'Name\']: ' + n['Name'] + ' - p[\'Value\']: ' + str(p['Value'])
            if n['Name'] == p['Value']:
                # print '/////////////////MATCH////////////////'*10
                # add_plugin_node(plugins, parent, output_node, input_name, node_name, node_type, node_parms, message_stack)
                # problem below !!!!!!!!!!!!
                add_plugin_node(plugins, environment_settings, environment_rop, p['Name'], normalize_name(n['Name']),
                                n['Type'], n['Parms'],
                                message_stack)
                break

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
    geometries = list()

    global black_listed_parms

    # some black listed parameters, sometimes not yet implemented, or no need to be implemented...
    black_listed_parms = (
        'roughness_model', 'option_use_roughness', 'subdivs_as_samples', 'enableDeepOutput', 'adv_exposure_mode',
        'adv_printer_lights_per', 'SettingsRTEngine_low_gpu_thread_priority', 'SettingsRTEngine_interactive',
        'SettingsRTEngine_enable_cpu_interop', 'SettingsUnitsInfo_meters_scale', 'SettingsUnitsInfo_photometric_scale',
        'SettingsUnitsInfo_scene_upDir', 'SettingsUnitsInfo_seconds_scale', 'SettingsUnitsInfo_frames_scale',
        'SettingsUnitsInfo_rgb_color_space', 'SettingsImageSampler_progressive_effectsUpdate',
        'SettingsImageSampler_render_mask_clear', 'SettingsLightCache_premultiplied',
        'SettingsIrradianceMap_detail_enhancement', 'SettingsPhotonMap_bounces', 'SettingsPhotonMap_max_photons',
        'SettingsPhotonMap_prefilter', 'SettingsPhotonMap_prefilter_samples', 'SettingsPhotonMap_mode',
        'SettingsPhotonMap_auto_search_distance', 'SettingsPhotonMap_search_distance',
        'SettingsPhotonMap_convex_hull_estimate', 'SettingsPhotonMap_dont_delete', 'SettingsPhotonMap_auto_save',
        'SettingsPhotonMap_auto_save_file', 'SettingsPhotonMap_store_direct_light', 'SettingsPhotonMap_multiplier',
        'SettingsPhotonMap_max_density', 'SettingsPhotonMap_retrace_corners', 'SettingsPhotonMap_retrace_bounces',
        'SettingsPhotonMap_show_calc_phase', 'SettingsDMCSampler_path_sampler_type', 'SettingsVFB_bloom_on',
        'SettingsVFB_bloom_fill_edges', 'SettingsVFB_bloom_weight', 'SettingsVFB_bloom_size', 'SettingsVFB_bloom_shape',
        'SettingsVFB_bloom_mode', 'SettingsVFB_bloom_mask_intensity_on', 'SettingsVFB_bloom_mask_intensity',
        'SettingsVFB_bloom_mask_objid_on', 'SettingsVFB_bloom_mask_objid', 'SettingsVFB_bloom_mask_mtlid_on',
        'SettingsVFB_bloom_mask_mtlid', 'SettingsVFB_glare_on', 'SettingsVFB_glare_fill_edges',
        'SettingsVFB_glare_weight', 'SettingsVFB_glare_size', 'SettingsVFB_glare_type', 'SettingsVFB_glare_mode',
        'SettingsVFB_glare_image_path', 'SettingsVFB_glare_obstacle_image_path', 'SettingsVFB_glare_diffraction_on',
        'SettingsVFB_glare_use_obstacle_image', 'SettingsVFB_glare_cam_blades_on', 'SettingsVFB_glare_cam_num_blades',
        'SettingsVFB_glare_cam_rotation', 'SettingsVFB_glare_cam_fnumber', 'SettingsVFB_glare_mask_intensity_on',
        'SettingsVFB_glare_mask_intensity', 'SettingsVFB_glare_mask_objid_on', 'SettingsVFB_glare_mask_objid',
        'SettingsVFB_glare_mask_mtlid_on', 'SettingsVFB_glare_mask_mtlid', 'SettingsVFB_interactive',
        'SettingsVFB_hardware_accelerated', 'SettingsVFB_display_srgb')

    # clear console
    print '\n' * 5000

    if lines.count > 1:
        if lines[0] == '#scene_export':

            for line in lines[1:]:
                ls = line.split(',', 1)
                if len(ls) == 2:
                    if ls[0] == 'filename':
                        parse_vrscene_file(ls[1], plugins, cameras, lights, settings, renderChannels, nodes,
                                           environments, geometries)

                        load_settings(settings)
                        load_render_channels(renderChannels)
                        # load_cameras(cameras)
                        # load_lights(lights)
                        load_nodes(nodes, geometries, materials)
                        load_materials(plugins, materials)
                        load_environments(plugins, environments)

            print '\nScene import finished'

        else:
            print '\nNothing to import...'


import_scene_from_clipboard()
