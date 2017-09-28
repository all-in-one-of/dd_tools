import hou

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    from Qt import QtWidgets, QtCore, QtGui

global addTargetNodeController, createLightTarget


def addTargetNodeController(light, light_target):
    constraints = light.createNode('chopnet', 'constraints')

    parm_group = constraints.parmTemplateGroup()
    parm_group.addParmTemplate(hou.IntParmTemplate('chopnet_rate', 'CHOP Rate', 1))
    parm_group.addParmTemplate(hou.IntParmTemplate('motionsamples', 'CHOP Motion Samples', 1))
    constraints.setParmTemplateGroup(parm_group)

    constraints.parm('chopnet_rate').setExpression('$FPS * ch("motionsamples")')
    constraints.parm('motionsamples').setExpression('$CHOPMOTIONSAMPLES')
    constraints.moveToGoodPosition()

    light.parm('constraints_on').set(1)
    light.parm('constraints_path').set('constraints')

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

    constraintobject = constraints.createNode('constraintobject', light_target.name())
    constraintobject.parm('obj_path').set('../../../' + light_target.name())
    constraintobject.parm('vex_range').set(1)
    constraintobject.parm('vex_rate').setExpression('ch("../chopnet_rate")')
    constraintobject.parm('export').set('../..')
    constraintobject.parm('gcolorr').set(0.9)
    constraintobject.parm('gcolorg').set(0.9)
    constraintobject.parm('gcolorb').set(0)

    constraintlookat.setInput(0, constraintgetworldspace)
    constraintlookat.setInput(1, constraintobject)
    constraints.layoutChildren()


def createLightTarget(parent, light):
    _light_target = parent.createNode('null', light.name() + '_target')

    parm_group = _light_target.parmTemplateGroup()
    parm_group.insertBefore(parm_group.findFolder("Transform"), hou.StringParmTemplate('light', 'Light', 1,
                                                                                       string_type=hou.stringParmType.NodeReference))
    _light_target.setParmTemplateGroup(parm_group)
    _light_target.parm('light').set(light.path())

    parm_group = light.parmTemplateGroup()
    parm_group.insertBefore(parm_group.findFolder("Transform"),
                            hou.StringParmTemplate('target', 'Target', 1,
                                                   string_type=hou.stringParmType.NodeReference))

    light.setParmTemplateGroup(parm_group)
    light.parm('target').set(_light_target.path())

    _light_target.parm('dcolorr').set(1)
    _light_target.parm('dcolorg').set(0.898039)
    _light_target.parm('dcolorb').set(0)
    _light_target.parm('geoscale').set(0.2)
    _light_target.parm('controltype').set(2)
    _light_target.setColor(hou.Color(1, 0.898039, 0))
    _light_target.setUserData('nodeshape', 'circle')
    #_light_target.setDisplayFlag(False)
    #_light_target.moveToGoodPosition()
    cam_pos = light.position()
    cam_pos[1] -= 1
    _light_target.setPosition(cam_pos)

    addTargetNodeController(light, _light_target)

    light.node('constraints').node('lookat').parm('twist').setExpression('ch("../../rz")')


    circle1 = light.node('circle1')
    circle1.parm('type').set(2)

    transform4 = circle1.createOutputNode('xform')
    transform4.parm('scale').set(1)
    merge1 = light.node('merge1')
    merge1.setInput(0, transform4)

    transform2 = light.node('transform2')
    transform2.parm('tx').setExpression('ch("../transform4/scale")')
    transform2.parm('scale').deleteAllKeyframes()
    transform2.parm('scale').set(0.5)

    light.node('transform1').parm('scale').setExpression('ch("../size_multiplier") / 2 / $PI')

    # draw lookat line
    add = light.createNode('add')
    add.parm('points').set(2)
    add.parm('usept0').set(1)
    add.parm('usept1').set(1)
    add.parm('pt0z').setExpression('-ch("../transform1/scale") * 0.66')
    add.parm('pt1z').setExpression(
        '-distance(ch("../tx"), ch("../ty"), ch("../tz"), ch(chs("../target") + "/tx"), ch(chs("../target") + "/ty"), ch(chs("../target") + "/tz"))')

    add.parm('prim0').set('0-1')

    color1 = add.createOutputNode('color')
    color1.parm('colorr').set(0.099)
    color1.parm('colorg').set(0.45)
    color1.parm('colorb').set(0.9)

    color2 = light.node('color1')
    merge1 = color2.createOutputNode('merge')
    merge1.setNextInput(color1)
    merge1.setDisplayFlag(True)
    merge1.moveToGoodPosition()

    light.layoutChildren()
    # light.setDeleteScript('print("light deleted")', language=hou.scriptLanguage.Python)
    return _light_target


def importLightFromClipboard():
    obj = hou.node('/obj')
    light = None
    light_name = ''
    light_type = ''
    light_target = None
    is_tuple = False
    clipboard = QtWidgets.QApplication.clipboard()
    text = clipboard.text()
    lines = text.splitlines()

    error_count = 0

    if lines[0].startswith('#light_export'):
        ls = lines[0].split(',',2)
        fps = ls[1]
        range = ls[2]

        if fps != str(hou.fps()):
            print('warning: fps differs from export')
        if range != str(hou.playbar.timelineRange()):
            print('warning: animation range differs from export')

        for line in lines[1:]:
            ls = line.split(',', 1)
            if len(ls) == 2:
                parm_name = ls[0]
                parm_val = ls[1]
                if parm_val.startswith('\'') and parm_val.endswith('\''):
                    parm_val = parm_val[1:-1]
                else:
                    parm_val = eval(parm_val)

                is_tuple = isinstance(parm_val, tuple)
                if parm_name == 'name':
                    light_name = parm_val
                elif line.startswith('type'):
                    light_type = parm_val
                    light = obj.node(light_name)
                    if light == None:
                        light = obj.createNode(light_type)
                        light.setName(light_name)
                        light.setColor(hou.Color(1, 0.898039, 0))
                        light.setUserData('nodeshape', 'light')
                        light.moveToGoodPosition()

                        out_node = None
                        for n in light.children():
                            if n.isGenericFlagSet(hou.nodeFlag.Render) == True:
                                out_node = n
                        color = out_node.createOutputNode('color')
                        color.parm('colorr').set(1)
                        color.parm('colorg').set(0.898039)
                        color.parm('colorb').set(0)
                        color.setDisplayFlag(True)

                        if light_type == 'VRayNodeLightSphere':
                            light.node('sphere1').parm('type').set(4)
                            light.node('sphere1').parm('imperfect').set(0)

                        if light_type == 'VRayNodeLightRectangle':
                            light.node('line1').parm('dist').setExpression(
                                '(ch("../u_size") + ch("../v_size")) * 0.333')
                            light.node('grid1').parm('type').set(2)
                            light.node('grid1').parm('orderu').set(2)
                            light.node('grid1').parm('orderv').set(2)
                            switch = light.node('grid1').createOutputNode('switch')
                            switch.parm('input').setExpression('ch("../is_disc")')
                            circle = light.createNode('circle')
                            circle.parm('type').set(2)
                            circle.parm('radx').setExpression('ch("../u_size") / 2')
                            circle.parm('rady').setExpression('ch("../v_size") / 2')
                            # light.parm('v_size').setExpression('ch("u_size")')
                            switch.setNextInput(circle)
                            light.node('merge1').setInput(0, switch)
                            # light.layoutChildren()

                        if light_type == 'VRayNodeSunLight':
                            '''
                            light.node('transform1').parm('sx').setExpression('ch("../size_multiplier")')
                            light.node('transform1').parm('sy').setExpression('ch("../size_multiplier")')
                            light.node('transform1').parm('sz').setExpression('ch("../size_multiplier")')
                            '''

                            light_target = obj.node(light_name + '_target')
                            if light_target == None:
                                light_target = createLightTarget(obj, light)
                            else:
                                for p in (light_target.parms()):
                                    p.deleteAllKeyframes()

                        null = light.createNode('null')
                        null.setRenderFlag(True)
                        # null.moveToGoodPosition()
                        light.layoutChildren()

                    else:
                        if light.type().name() != light_type:
                            light.changeNodeType(light_type)
                        for p in (light.parms()):
                            p.deleteAllKeyframes()
                            p.revertToDefaults()

                        light.parm('constraints_on').set(1)
                        light.parm('constraints_path').set('constraints')

                elif line.startswith('target_'):
                    light_target = obj.node(light_name + '_target')
                    if light_target == None:
                        light_target = createLightTarget(obj, light)
                    else:
                        for p in (light_target.parms()):
                            p.deleteAllKeyframes()

                    if is_tuple:
                        for k in parm_val:
                            setKey = hou.Keyframe()
                            setKey.setFrame(k[0])
                            setKey.setValue(k[1])
                            light_target.parm(parm_name[7:]).setKeyframe(setKey)
                    else:
                        light_target.parm(parm_name[7:]).set(parm_val)

                else:
                    try:
                        if is_tuple:
                            for k in parm_val:
                                setKey = hou.Keyframe()
                                setKey.setFrame(k[0])
                                setKey.setValue(k[1])
                                light.parm(parm_name).setKeyframe(setKey)
                        else:
                            light.parm(parm_name).set(parm_val)
                    except:
                        print('cannot setting parameter: ' + parm_name)
                        error_count += 1

        if error_count == 0:
            print('light successfully imported')
        else:
            print('light imported with ' + str(error_count) + " errors")

    else:
        print('cannot apply clipboad values, wrong type!')


importLightFromClipboard()
