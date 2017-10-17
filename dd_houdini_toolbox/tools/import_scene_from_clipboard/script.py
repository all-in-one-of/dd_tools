import hou
import re
import os.path
import shutil

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    from Qt import QtWidgets, QtCore, QtGui

global re, set_timeline_range, parse_vrscene_file, import_scene_from_clipboard, get_vray_rop_node, try_parse_parm_value, normalize_name, try_create_node, try_set_parm, load_settings, load_cameras, load_lights, load_render_channels, get_render_channels_container, load_nodes, load_materials, try_set_input, get_material_output, add_plugin_node, revert_parms_to_default, load_environments, get_environment_settings, find_or_create_user_color, add_vray_objectid_param_template, add_scene_wirecolor_visualizer, try_find_or_create_node, try_find_or_create_target_object, init_constraint, format_value


def parse_vrscene_file(fname, plugins, cameras, lights, settings, renderChannels, nodes, environments, geometries,
                       targetObjects, black_listed_parms=()):
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

                    if not parm_name in black_listed_parms:
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

            # catch target objects
            elif 'Target' in type:
                targetObjects.append({'Type': type, 'Name': name, 'Parms': parms})

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


def try_parse_parm_value(name, type, parm_name, parm_val, message_stack):
    metric_parms = (('SettingsCameraDof', 'aperture'), ('SettingsCameraDof', 'focal_dist'))

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

        elif parm_val.startswith('Keys'):
            # Transform(Matrix(Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1)), Vector(0, 0, 0))
            result = re.match(r"Keys\((.*?.*)\)", parm_val)
            result = eval('(' + result.group(1).replace('Keys', '') + ')')

        elif parm_val.startswith('Matrix'):
            # Transform(Matrix(Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1)), Vector(0, 0, 0))
            result = re.match(r"Matrix\((.*?.*)\)", parm_val)
            result = hou.Matrix3(eval('(' + result.group(1).replace('Vector', '') + ')'))

        elif parm_val.startswith('Transform'):
            # Transform(Matrix(Vector(1, 0, 0), Vector(0, 1, 0), Vector(0, 0, 1)), Vector(0, 0, 0))
            result = re.match(r"Transform\(Matrix\((.*?.*)\), (.*?.*)\)", parm_val)
            result = (hou.Matrix3(eval('(' + result.group(1).replace('Vector', '') + ')')),
                      hou.Vector3(eval(result.group(2).replace('Vector', ''))))

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

            if (parm_name) in metric_parms:
                result /= 100

    except:
        if not '@' in str(parm_val) and not 'bitmapBuffer' in str(parm_val):
            message_stack.append('Warning - cannot parsing value: ' + str(
                parm_val) + ' on parameter: ' + parm_name + ' on node: ' + name)

    return result


def try_set_parm(node, parm_name, parm_val, message_stack):
    try:
        if isinstance(parm_val, tuple):
            for k in parm_val:
                setKey = hou.Keyframe()
                setKey.setFrame(k[0])
                setKey.setValue(k[1])
                node.parm(parm_name).setKeyframe(setKey)

        elif isinstance(parm_val, hou.Vector3) or isinstance(parm_val, hou.Vector4):
            node.parmTuple(parm_name).set(parm_val)

        elif isinstance(parm_val, hou.Matrix3):
            node.parmTuple(parm_name).set(parm_val.asTuple())

        else:
            node.parm(parm_name).set(parm_val)

    except:
        message_stack.append('Cannot set parm on ' + node.name() + ' ' + parm_name + ' = ' + str(
            parm_val))


def set_timeline_range(start, end):
    setGobalFrangeExpr = 'tset `(%d-1)/$FPS` `%d/$FPS`' % (start, end)
    hou.hscript(setGobalFrangeExpr)
    hou.playbar.setPlaybackRange(start, end)


def format_value(value):
    result = str(value)
    if isinstance(value, (str, unicode)):
        result = '"' + str(value) + '"'
    return result


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
            parm_val = try_parse_parm_value(s['Name'], s['Type'], parm_name, p['Value'], message_stack)

            print s['Type'] + '_' + parm_name + ' = ' + format_value(parm_val)

            if s['Type'] == 'CustomSettings':
                if parm_name == 'name':
                    hou.hipFile.setName(parm_val)
                elif parm_name == 'camera':
                    cam = hou.node('/obj/' + parm_val)
                    if cam != None:
                        try_set_parm(vray_rop, 'render_camera', cam.path(), message_stack)
                        hou.ui.paneTabOfType(hou.paneTabType.SceneViewer).curViewport().setCamera(cam)
                elif parm_name == 'fps':
                    hou.setFps(parm_val)
                elif parm_name == 'range':
                    set_timeline_range(parm_val[0], parm_val[1])

            else:
                if s['Type'] == 'SettingsGI':
                    if parm_name == 'primary_engine' or parm_name == 'secondary_engine':
                        if parm_val == 2:
                            parm_val = 1
                        elif parm_val == 3:
                            parm_val = 2

                try_set_parm(vray_rop, s['Type'] + '_' + parm_name, parm_val, message_stack)

    if len(message_stack) != 0:
        print '\n\n\nLoad Render Settings terminated with: ' + str(len(message_stack)) + ' errors:\n'

    for m in message_stack:
        print m


def init_constraint(node, target):
    constraints = node.createNode('chopnet', 'constraints')

    parm_group = constraints.parmTemplateGroup()
    parm_group.addParmTemplate(hou.IntParmTemplate('chopnet_rate', 'CHOP Rate', 1))
    parm_group.addParmTemplate(hou.IntParmTemplate('motionsamples', 'CHOP Motion Samples', 1))
    constraints.setParmTemplateGroup(parm_group)

    constraints.parm('chopnet_rate').setExpression('$FPS * ch("motionsamples")')
    constraints.parm('motionsamples').setExpression('$CHOPMOTIONSAMPLES')
    constraints.moveToGoodPosition()

    node.parm('constraints_on').set(1)
    node.parm('constraints_path').set('constraints')

    constraintlookat = constraints.createNode('constraintlookat', 'lookat')
    constraintlookat.parm('vex_range').set(1)
    constraintlookat.parm('vex_rate').setExpression('ch("../chopnet_rate")')
    constraintlookat.parm('export').set('../..')
    constraintlookat.parm('gcolorr').set(0)
    constraintlookat.parm('gcolorg').set(0)
    constraintlookat.parm('gcolorb').set(0.9)

    constraintgetworldspace = constraints.createNode('constraintgetworldspace', 'getworldspace')
    constraintgetworldspace.parm('obj_path').set('../..')
    constraintgetworldspace.parm('vex_range').set(1)
    constraintgetworldspace.parm('vex_rate').setExpression('ch("../chopnet_rate")')
    constraintgetworldspace.parm('export').set('../..')
    constraintgetworldspace.parm('gcolorr').set(0.9)
    constraintgetworldspace.parm('gcolorg').set(0)
    constraintgetworldspace.parm('gcolorb').set(0)

    constraintobject = constraints.createNode('constraintobject', 'target_node')
    constraintobject.parm('obj_path').setExpression('chsop("../../lookat_target")')
    constraintobject.parm('vex_range').set(1)
    constraintobject.parm('vex_rate').setExpression('ch("../chopnet_rate")')
    constraintobject.parm('export').set('../..')
    constraintobject.parm('gcolorr').set(0.9)
    constraintobject.parm('gcolorg').set(0.9)
    constraintobject.parm('gcolorb').set(0)

    constraintlookat.setInput(0, constraintgetworldspace)
    constraintlookat.setInput(1, constraintobject)
    constraints.layoutChildren()


def try_find_or_create_target_object(parent, node, name, target_objects, message_stack):
    print '\n\n' + name + ' ( TargetObject ) \n'

    target = try_create_node(parent, 'null', name, message_stack)

    if target != None:

        parm_group = target.parmTemplateGroup()
        parm_group.insertBefore(parm_group.findFolder("Transform"), hou.StringParmTemplate('lookat_parent', 'Parent', 1,
                                                                                           string_type=hou.stringParmType.NodeReference))
        target.setParmTemplateGroup(parm_group)
        target.parm('lookat_parent').set(node.path())

        parm_group = node.parmTemplateGroup()
        parm_group.insertBefore(parm_group.findFolder("Transform"), hou.StringParmTemplate('lookat_target', 'Target', 1,
                                                                                           string_type=hou.stringParmType.NodeReference))

        node.setParmTemplateGroup(parm_group)
        node.parm('lookat_target').set(target.path())

        init_constraint(node, target)
        node.node('constraints').node('lookat').parm('twist').setExpression('ch("../../rz")')

        # target.parmTuple('dcolor').set(hou.Vector3(node.color().rgb()))
        target.parmTuple('dcolor').set(hou.Vector3())
        target.parm('geoscale').set(0.2)
        target.parm('controltype').set(2)
        target.setUserData('nodeshape', 'circle')
        target.setColor(node.color())
        target.setPosition(node.position() + hou.Vector2(0, -1))

        for t in target_objects:
            if t['Name'] == name:

                for p in t['Parms']:
                    parm_val = try_parse_parm_value(name, 'TargetObject', p['Name'], p['Value'], message_stack)

                    print p['Name'] + " = " + str(parm_val)
                    try_set_parm(target, p['Name'], parm_val, message_stack)

                break


def load_cameras(cameras, target_objects):
    # loading settings
    message_stack = list()
    obj = hou.node('/obj')

    print '\n\n\n#############################################'
    print '#############  LOADING CAMERAS  #############'
    print '#############################################\n\n'

    for c in cameras:

        print c['Name'] + ' ( ' + c['Type'] + ' ) \n'

        camera = try_create_node(obj, 'cam', c['Name'], message_stack)

        if camera != None:
            for p in c['Parms']:
                parm_name = p['Name']
                parm_val = try_parse_parm_value(c['Name'], c['Type'], parm_name, p['Value'], message_stack)

                if parm_name == 'target':
                    try_find_or_create_target_object(obj, camera, parm_val, target_objects, message_stack)
                else:
                    print parm_name + " = " + str(parm_val)
                    try_set_parm(camera, parm_name, parm_val, message_stack)

        print '\n\n'

    if len(message_stack) != 0:
        print '\n\n\nLoad cameras terminated with: ' + str(len(message_stack)) + ' errors:\n'

    for m in message_stack:
        print m


def load_lights(lights, target_objects):
    # loading settings
    message_stack = list()
    obj = hou.node('/obj')

    print '\n\n\n#############################################'
    print '##############  LOADING LIGHTS  #############'
    print '#############################################\n\n'

    for l in lights:

        # particular case for 'Max' types, need conversion
        '''if l['Type'] == 'LightOmniMax':
            l['Type'] = 'LightOmni'''

        print l['Name'] + ' ( ' + l['Type'] + ' ) \n'

        light = try_create_node(obj, 'VRayNode' + l['Type'], l['Name'], message_stack)

        if light != None:
            light.setColor(hou.Color(1, 0.898039, 0))
            light.setUserData('nodeshape', 'light')

            for p in l['Parms']:
                parm_name = p['Name']
                parm_val = try_parse_parm_value(l['Name'], l['Type'], parm_name, p['Value'], message_stack)

                if parm_name == 'target':
                    try_find_or_create_target_object(obj, light, parm_val, target_objects, message_stack)
                else:
                    print parm_name + " = " + str(parm_val)
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
        message_stack.append('cannot create node name:' + name + ' type: ' + str(type) + ' parent: ' + parent.name())

    if node != None:
        if old_node != None:
            old_node.destroy()
        try:
            node.setName(name)
        except:
            message_stack.append('cannot set name:' + name)

    return node


def try_find_or_create_node(parent, type, name, message_stack):
    node = parent.node(name)

    if node != None:
        for p in (node.parms()):
            p.deleteAllKeyframes()
    else:
        try:
            node = parent.createNode(type)
            node.moveToGoodPosition()
        except:
            message_stack.append(
                'cannot create node name:' + name + ' type: ' + str(type) + ' parent: ' + parent.name())

        if node != None:
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

        print name + ' ( ' + s['Type'] + ' ) \n'

        render_channel = try_create_node(render_channels_rop, 'VRayNode' + s['Type'], name, message_stack)

        if render_channel != None:
            render_channels_container.setNextInput(render_channel)

            for p in s['Parms']:
                parm_name = p['Name']
                parm_val = try_parse_parm_value(s['Name'], s['Type'], parm_name, p['Value'], message_stack)

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
                    from_filename = try_parse_parm_value(name, n['Type'], parm_name, parm_val, message_stack)
                elif parm_name == 'object_id':
                    object_id = try_parse_parm_value(name, n['Type'], parm_name, parm_val, message_stack)
                elif parm_name == 'wirecolor':
                    wirecolor = try_parse_parm_value(name, n['Type'], parm_name, parm_val, message_stack)
                elif parm_name == 'handle':
                    handle = try_parse_parm_value(name, n['Type'], parm_name, parm_val, message_stack)

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
    node = try_find_or_create_node(parent, 'VRayNode' + node_type, normalize_name(node_name), message_stack)

    print '\n\n( ' + normalize_name(node_name) + ' )'

    if node != None:

        try_set_input(output_node, input_name, node, message_stack)

        for p in node_parms:
            parm_name = p['Name']
            parm_val = p['Value']
            parm_val = try_parse_parm_value(node_name, node_type, parm_name, p['Value'], message_stack)

            if node_type == 'BRDFBump' and parm_name == 'bump_tex':
                parm_name = 'bump_tex_color'  # to test !...

            if node_type == 'BitmapBuffer' and parm_name == 'interpolation':
                if parm_val == 3: parm_val = 0  # need this conversion because of out of range error with value of 3

            if node_type == 'BRDFVRayMtl' and parm_name == 'brdf_type':
                if parm_val == 4: parm_val = 3  # need this conversion because of the difference between max and houdini menu list

            if node_type == 'UVWGenEnvironment' and parm_name == 'mapping_type':
                if parm_val == 'angular':
                    parm_val = 0
                elif parm_val == 'cubic':
                    parm_val = 1
                elif parm_val == 'spherical_vray':
                    parm_val = 6
                elif parm_val == 'mirror_ball':
                    parm_val = 3
                else:
                    message_stack.append('unknown mapping_type value: "' + str(parm_val) + '" on node: ' + node.name())
                    parm_val = 2

                    # if (node_type == 'UVWGenChannel' or node_type == 'UVWGenEnvironment') and parm_name == 'uvw_transform':
            if parm_name == 'uvw_transform':

                makexform = try_find_or_create_node(parent, 'makexform', node.name() + '_transform', message_stack)

                if makexform != None:
                    result = hou.Matrix4(parm_val[0]).explode(transform_order='trs', rotate_order='xyz',
                                                              pivot=hou.Vector3(0.5, 0.5, 0))  # , pivot=parm_val[1])

                    # try_set_parm(xform, 'trans', result['translate'], message_stack)
                    try_set_parm(makexform, 'trans', parm_val[1], message_stack)
                    try_set_parm(makexform, 'rot', result['rotate'], message_stack)
                    try_set_parm(makexform, 'scale', result['scale'], message_stack)
                    try_set_parm(makexform, 'pivot', result['shear'], message_stack)

                    try_set_input(node, 'uvw_transform', makexform, message_stack)

            # if (node_type == 'UVWGenChannel' or node_type == 'UVWGenEnvironment') and parm_name == 'uvw_matrix':
            elif parm_name == 'uvw_matrix':

                matrix = try_find_or_create_node(parent, 'parameter', node.name() + '_matrix', message_stack)

                if matrix != None:
                    '''(preRotateX(matrix3[1, 0, 0][0, 0, 1][0, -1, 0][0, 0, 0]) - 90) * _t * inverse(
                        matrix3[1, 0, 0][0, 0, 1][0, -1, 0][0, 0, 0])'''

                    rot = parm_val.extractRotates()
                    quat = hou.Quaternion(hou.hmath.buildRotate((rot[0] - 90, rot[2], rot[1]), "xyz"))
                    m3 = quat.extractRotationMatrix3().transposed()

                    try_set_parm(matrix, 'parmname', 'uvw_matrix', message_stack)
                    try_set_parm(matrix, 'parmtype', 13, message_stack)
                    try_set_parm(matrix, 'float9def', m3, message_stack)
                    try_set_parm(matrix, 'invisible', 1, message_stack)
                    try_set_parm(matrix, 'exportparm', 1, message_stack)

                    try_set_input(node, 'uvw_matrix', matrix, message_stack)


            elif node_type == 'MtlMulti':

                if parm_name == 'mtls_list':

                    # insert mtlid_gen // necessary for material_ids generation
                    '''mtlid_gen = parent.node(output_node.name() + '_mtlid_gen')
                    if mtlid_gen == None:
                        mtlid_gen = node.insertParmGenerator('mtlid_gen', hou.vopParmGenType.Parameter, False)
                        mtlid_gen.setName(output_node.name() + '_mtlid_gen')'''
                    mtlid_gen = try_find_or_create_node(parent, 'parameter', output_node.name() + '_mtlid_gen',
                                                        message_stack)

                    if mtlid_gen != None:
                        try_set_parm(mtlid_gen, 'parmname', 'mtlid_gen', message_stack)
                        try_set_parm(mtlid_gen, 'parmtype', 1, message_stack)
                        try_set_parm(mtlid_gen, 'intdef', 0, message_stack)
                        try_set_parm(mtlid_gen, 'invisible', 1, message_stack)
                        try_set_parm(mtlid_gen, 'exportparm', 1, message_stack)

                        try_set_input(node, 'mtlid_gen', mtlid_gen, message_stack)

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


def find_or_create_user_color(output_node, parent, input_name, parm_val, message_stack):
    node = None

    for child in parent.children():
        if child.type().name() == 'VRayNodeTexUserColor':
            if hou.Vector4(child.parmTuple('default_color').eval()) == parm_val:
                node = child
                break

    if node == None:
        node = parent.createNode('VRayNodeTexUserColor')

        count = 1
        while parent.node('usercolor_' + str(count)) != None: count += 1
        node.setName('usercolor_' + str(count))

        try_set_parm(node, 'default_color', parm_val, message_stack)

    try_set_input(output_node, input_name, node, message_stack)


def load_environments(plugins, environments):
    # loading environment
    message_stack = list()

    vray_rop = get_vray_rop_node()
    parent = hou.node(vray_rop.parm('render_network_environment').eval())

    if parent == None:
        out = hou.node('/out')
        parent = out.createNode('vray_environment', 'env')
        parent.moveToGoodPosition()
        vray_rop.parm('render_network_environment').set(parent.path())

    for child in parent.children():
        if child.type().name() != 'VRayNodeSettingsEnvironment':
            child.destroy()

    output_node = get_environment_settings(parent)

    print '\n\n\n#############################################'
    print '########  LOADING SCENE ENVIRONMENT  ########'
    print '#############################################\n\n'

    for p in environments:
        parm_name = p['Name']
        parm_val = try_parse_parm_value(output_node, 'SettingsEnvironment', parm_name, p['Value'], message_stack)

        print parm_name + " = " + str(parm_val)

        if isinstance(parm_val, hou.Vector4):
            find_or_create_user_color(output_node, parent, parm_name, parm_val, message_stack)

        for nn in plugins:
            if nn['Name'] == str(parm_val):
                add_plugin_node(plugins, parent, output_node, parm_name, nn['Name'], nn['Type'], nn['Parms'],
                                message_stack)

    print '\n\n'

    parent.layoutChildren()

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
    render_channels = list()
    nodes = list()
    materials = list()
    environments = list()
    geometries = list()
    target_objects = list()

    # some black listed parameters, sometimes not yet implemented, or no need to be implemented...
    black_listed_parms = (
        ('', 'roughness_model'), ('', 'option_use_roughness'), ('', 'subdivs_as_samples'), ('', 'enableDeepOutput'),
        ('', 'adv_exposure_mode'), ('', 'adv_printer_lights_per'), ('SettingsRTEngine, low_gpu_thread_priority'),
        ('SettingsRTEngine', 'interactive'), ('SettingsRTEngine', 'enable_cpu_interop'),
        ('SettingsUnitsInfo', 'meters_scale'),
        ('SettingsUnitsInfo', 'photometric_scale'), ('SettingsUnitsInfo', 'scene_upDir'),
        ('SettingsUnitsInfo', 'seconds_scale'),
        ('SettingsUnitsInfo', 'frames_scale'),
        ('SettingsUnitsInfo', 'rgb_color_space'), ('SettingsImageSampler', 'progressive_effectsUpdate'),
        ('SettingsImageSampler', 'render_mask_clear'), ('SettingsLightCache', 'premultiplied'),
        ('SettingsIrradianceMap', 'detail_enhancement'), ('SettingsPhotonMap', 'bounces'),
        ('SettingsPhotonMap', 'max_photons'),
        ('SettingsPhotonMap', 'prefilter'), ('SettingsPhotonMap', 'prefilter_samples'), ('SettingsPhotonMap', 'mode'),
        ('SettingsPhotonMap', 'auto_search_distance'), ('SettingsPhotonMap', 'search_distance'),
        ('SettingsPhotonMap', 'convex_hull_estimate'), ('SettingsPhotonMap', 'dont_delete'),
        ('SettingsPhotonMap', 'auto_save'),
        ('SettingsPhotonMap', 'auto_save_file'), ('SettingsPhotonMap', 'store_direct_light'),
        ('SettingsPhotonMap', 'multiplier'),
        ('SettingsPhotonMap', 'max_density'), ('SettingsPhotonMap', 'retrace_corners'),
        ('SettingsPhotonMap', 'retrace_bounces'),
        ('SettingsPhotonMap', 'show_calc_phase'), ('SettingsDMCSampler', 'path_sampler_type'),
        ('SettingsVFB', 'bloom_on'),
        ('SettingsVFB', 'bloom_fill_edges'), ('SettingsVFB', 'bloom_weight'), ('SettingsVFB', 'bloom_size'),
        ('SettingsVFB', 'bloom_shape'),
        ('SettingsVFB', 'bloom_mode'), ('SettingsVFB', 'bloom_mask_intensity_on'),
        ('SettingsVFB', 'bloom_mask_intensity'),
        ('SettingsVFB', 'bloom_mask_objid_on'), ('SettingsVFB', 'bloom_mask_objid'),
        ('SettingsVFB', 'bloom_mask_mtlid_on'),
        ('SettingsVFB', 'bloom_mask_mtlid'), ('SettingsVFB', 'glare_on'), ('SettingsVFB', 'glare_fill_edges'),
        ('SettingsVFB', 'glare_weight'), ('SettingsVFB', 'glare_size'), ('SettingsVFB', 'glare_type'),
        ('SettingsVFB', 'glare_mode'),
        ('SettingsVFB', 'glare_image_path'), ('SettingsVFB', 'glare_obstacle_image_path'),
        ('SettingsVFB', 'glare_diffraction_on'),
        ('SettingsVFB', 'glare_use_obstacle_image'), ('SettingsVFB', 'glare_cam_blades_on'),
        ('SettingsVFB', 'glare_cam_num_blades'),
        ('SettingsVFB', 'glare_cam_rotation'), ('SettingsVFB', 'glare_cam_fnumber'),
        ('SettingsVFB', 'glare_mask_intensity_on'),
        ('SettingsVFB', 'glare_mask_intensity'), ('SettingsVFB', 'glare_mask_objid_on'),
        ('SettingsVFB', 'glare_mask_objid'),
        ('SettingsVFB', 'glare_mask_mtlid_on'), ('SettingsVFB', 'glare_mask_mtlid'), ('SettingsVFB', 'interactive'),
        ('SettingsVFB', 'hardware_accelerated'), ('SettingsVFB', 'display_srgb')
    )

    # clear console
    print '\n' * 5000

    if lines.count > 1:
        if lines[0] == '#scene_export':

            for line in lines[1:]:
                ls = line.split(',', 1)
                if len(ls) == 2:
                    if ls[0] == 'filename':
                        parse_vrscene_file(ls[1], plugins, cameras, lights, settings, render_channels, nodes,
                                           environments, geometries, target_objects, black_listed_parms)

                        load_render_channels(render_channels)
                        load_cameras(cameras, target_objects)
                        load_lights(lights, target_objects)
                        load_nodes(nodes, geometries, materials)
                        load_materials(plugins, materials)
                        load_environments(plugins, environments)
                        load_settings(settings)

            print '\nScene import finished'

        else:
            print '\nNothing to import...'


import_scene_from_clipboard()
