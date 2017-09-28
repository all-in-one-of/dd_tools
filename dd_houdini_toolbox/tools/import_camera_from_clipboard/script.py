import hou

try:
    from PyQt5 import QtWidgets, QtCore, QtGui
except ImportError:
    from Qt import QtWidgets, QtCore, QtGui

global addTargetNodeController, createCameraTarget


def addTargetNodeController(camera, camera_target):
    constraints = camera.createNode('chopnet', 'constraints')

    parm_group = constraints.parmTemplateGroup()
    parm_group.addParmTemplate(hou.IntParmTemplate('chopnet_rate', 'CHOP Rate', 1))
    parm_group.addParmTemplate(hou.IntParmTemplate('motionsamples', 'CHOP Motion Samples', 1))
    constraints.setParmTemplateGroup(parm_group)

    constraints.parm('chopnet_rate').setExpression('$FPS * ch("motionsamples")')
    constraints.parm('motionsamples').setExpression('$CHOPMOTIONSAMPLES')
    constraints.moveToGoodPosition()

    camera.parm('constraints_on').set(1)
    camera.parm('constraints_path').set('constraints')

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

    constraintobject = constraints.createNode('constraintobject', camera_target.name())
    constraintobject.parm('obj_path').set('../../../' + camera_target.name())
    constraintobject.parm('vex_range').set(1)
    constraintobject.parm('vex_rate').setExpression('ch("../chopnet_rate")')
    constraintobject.parm('export').set('../..')
    constraintobject.parm('gcolorr').set(0.9)
    constraintobject.parm('gcolorg').set(0.9)
    constraintobject.parm('gcolorb').set(0)

    constraintlookat.setInput(0, constraintgetworldspace)
    constraintlookat.setInput(1, constraintobject)
    constraints.layoutChildren()


def createCameraTarget(parent, camera):
    _camera_target = parent.createNode('null', camera.name() + '_target')

    parm_group = _camera_target.parmTemplateGroup()
    parm_group.insertBefore(parm_group.findFolder("Transform"), hou.StringParmTemplate('camera', 'Camera', 1,
                                                                                       string_type=hou.stringParmType.NodeReference))
    _camera_target.setParmTemplateGroup(parm_group)
    _camera_target.parm('camera').set(camera.path())

    parm_group = camera.parmTemplateGroup()
    parm_group.insertBefore(parm_group.findFolder("Transform"),
                            hou.StringParmTemplate('target', 'Target', 1,
                                                   string_type=hou.stringParmType.NodeReference))

    parm_group.insertBefore(parm_group.findFolder("Transform"),
                            hou.ToggleParmTemplate('showcone', 'Show Cone', 0, script_callback='kwargs["node"].parm("switch1/input").set(0) if not kwargs["node"].parm("showcone").eval() else kwargs["node"].parm("switch1/input").set(1) if not kwargs["node"].parm("showclipplanes").eval() else kwargs["node"].parm("switch1/input").set(2)', script_callback_language=hou.scriptLanguage.Python))

    parm_group.insertBefore(parm_group.findFolder("Transform"),
                            hou.ToggleParmTemplate('showclipplanes', 'Show Clip Planes', 0, disable_when='{ showcone != 1 }', script_callback='kwargs["node"].parm("switch1/input").set(2) if kwargs["node"].parm("showclipplanes").eval() else kwargs["node"].parm("switch1/input").set(1)', script_callback_language=hou.scriptLanguage.Python))

    camera.setParmTemplateGroup(parm_group)
    camera.parm('target').set(_camera_target.path())

    _camera_target.parm('dcolorr').set(0)
    _camera_target.parm('dcolorg').set(0)
    _camera_target.parm('dcolorb').set(0.5)
    _camera_target.parm('geoscale').set(0.2)
    _camera_target.parm('controltype').set(2)
    _camera_target.setColor(hou.Color(0.298039, 0.54902, 0.74902))
    _camera_target.setUserData('nodeshape', 'circle')
    #_camera_target.setDisplayFlag(False)
    #_camera_target.moveToGoodPosition()
    cam_pos = camera.position()
    cam_pos[1] -= 1
    _camera_target.setPosition(cam_pos)

    addTargetNodeController(camera, _camera_target)

    camera.node('constraints').node('lookat').parm('twist').setExpression('ch("../../rz")')
    camera.parm('focus').setExpression('distance(ch("tx"), ch("ty"), ch("tz"), ch(chs("target") + "/tx"), ch(chs("target") + "/ty"), ch(chs("target") + "/tz"))')


    #draw lookat line
    add = camera.createNode('add')
    add.parm('points').set(2)
    add.parm('usept0').set(1)
    add.parm('usept1').set(1)
    add.parm('pt1z').setExpression('-ch("../focus")')
    add.parm('prim0').set('0-1')

    color1 = add.createOutputNode('color')
    color1.parm('colorr').set(0.099)
    color1.parm('colorg').set(0.45)
    color1.parm('colorb').set(0.9)





    xform = camera.node('xform1')

    color2 = xform.createOutputNode('color')
    color2.parm('colorr').set(0.11172)
    color2.parm('colorg').set(0.342342)
    color2.parm('colorb').set(0.84)



    #draw full cone
    add2 = camera.createNode('add')
    add2.parm('points').set(5)
    add2.parm('usept0').set(1)
    add2.parm('usept1').set(1)
    add2.parm('usept2').set(1)
    add2.parm('usept3').set(1)
    add2.parm('usept4').set(1)
    add2.parm('pt1x').setExpression('ch("../focus") / ch("../focal") * ch("../aperture") / 2')
    add2.parm('pt1y').setExpression('ch("../focus") / ch("../focal") * ch("../resy") * ch("../aperture") / ch("../resx") * ch("../aspect") / 2')
    add2.parm('pt1z').setExpression( '-ch("../focus")')
    add2.parm('pt2x').setExpression('-ch("pt1x")')
    add2.parm('pt2y').setExpression('ch("pt1y")')
    add2.parm('pt2z').setExpression('ch("pt1z")')
    add2.parm('pt3x').setExpression( 'ch("pt1x")')
    add2.parm('pt3y').setExpression( '-ch("pt1y")')
    add2.parm('pt3z').setExpression( 'ch("pt1z")')
    add2.parm('pt4x').setExpression('-ch("pt1x")')
    add2.parm('pt4y').setExpression('-ch("pt1y")')
    add2.parm('pt4z').setExpression('ch("pt1z")')
    add2.parm('prims').set(8)
    add2.parm('prim0').set('0 1')
    add2.parm('prim1').set('0 2')
    add2.parm('prim2').set('0 3')
    add2.parm('prim3').set('0 4')
    add2.parm('prim4').set('1 2')
    add2.parm('prim5').set('2 4')
    add2.parm('prim6').set('4 3')
    add2.parm('prim7').set('3 1')

    color3 = add2.createOutputNode('color')
    color3.parm('colorr').set(0.6)
    color3.parm('colorg').set(0.8)
    color3.parm('colorb').set(0.898039)





    #draw cone lines extended to farclip
    add3 = camera.createNode('add')
    add3.parm('points').set(5)
    add3.parm('usept0').set(1)
    add3.parm('usept1').set(1)
    add3.parm('usept2').set(1)
    add3.parm('usept3').set(1)
    add3.parm('usept4').set(1)
    add3.parm('pt1x').setExpression('ch("../far") / ch("../focal") * ch("../aperture") / 2')
    add3.parm('pt1y').setExpression(
        'ch("../far") / ch("../focal") * ch("../resy") * ch("../aperture") / ch("../resx") * ch("../aspect") / 2')
    add3.parm('pt1z').setExpression('-ch("../far")')
    add3.parm('pt2x').setExpression('-ch("pt1x")')
    add3.parm('pt2y').setExpression('ch("pt1y")')
    add3.parm('pt2z').setExpression('ch("pt1z")')
    add3.parm('pt3x').setExpression('-ch("pt1x")')
    add3.parm('pt3y').setExpression('-ch("pt1y")')
    add3.parm('pt3z').setExpression('ch("pt1z")')
    add3.parm('pt4x').setExpression('ch("pt1x")')
    add3.parm('pt4y').setExpression('-ch("pt1y")')
    add3.parm('pt4z').setExpression('ch("pt1z")')
    add3.parm('prims').set(4)
    add3.parm('prim0').set('0 1')
    add3.parm('prim1').set('0 2')
    add3.parm('prim2').set('0 3')
    add3.parm('prim3').set('0 4')

    color4 = add3.createOutputNode('color')
    color4.parm('colorr').set(0.6) #0.898039
    color4.parm('colorg').set(0.8) #0.8
    color4.parm('colorb').set(0.898039) #0.6



    #draw clip planes (red)
    add4 = camera.createNode('add')
    add4.parm('points').set(8)
    add4.parm('usept0').set(1)
    add4.parm('usept1').set(1)
    add4.parm('usept2').set(1)
    add4.parm('usept3').set(1)
    add4.parm('usept4').set(1)
    add4.parm('usept5').set(1)
    add4.parm('usept6').set(1)
    add4.parm('usept7').set(1)
    add4.parm('pt0x').setExpression('ch("../near") / ch("../focal") * ch("../aperture") / 2')
    add4.parm('pt0y').setExpression('ch("../near") / ch("../focal") * ch("../resy") * ch("../aperture") / ch("../resx") * ch("../aspect") / 2')
    add4.parm('pt0z').setExpression('-ch("../near")')
    add4.parm('pt1x').setExpression('-ch("pt0x")')
    add4.parm('pt1y').setExpression('ch("pt0y")')
    add4.parm('pt1z').setExpression('ch("pt0z")')
    add4.parm('pt2x').setExpression('-ch("pt0x")')
    add4.parm('pt2y').setExpression('-ch("pt0y")')
    add4.parm('pt2z').setExpression('ch("pt0z")')
    add4.parm('pt3x').setExpression('ch("pt0x")')
    add4.parm('pt3y').setExpression('-ch("pt0y")')
    add4.parm('pt3z').setExpression('ch("pt0z")')
    add4.parm('pt4x').setExpression('ch("../far") / ch("../focal") * ch("../aperture") / 2')
    add4.parm('pt4y').setExpression(
        'ch("../far") / ch("../focal") * ch("../resy") * ch("../aperture") / ch("../resx") * ch("../aspect") / 2')
    add4.parm('pt4z').setExpression('-ch("../far")')
    add4.parm('pt5x').setExpression('-ch("pt4x")')
    add4.parm('pt5y').setExpression('ch("pt4y")')
    add4.parm('pt5z').setExpression('ch("pt4z")')
    add4.parm('pt6x').setExpression('-ch("pt4x")')
    add4.parm('pt6y').setExpression('-ch("pt4y")')
    add4.parm('pt6z').setExpression('ch("pt4z")')
    add4.parm('pt7x').setExpression('ch("pt4x")')
    add4.parm('pt7y').setExpression('-ch("pt4y")')
    add4.parm('pt7z').setExpression('ch("pt4z")')
    add4.parm('prims').set(6)
    add4.parm('closed0').set(True)
    add4.parm('closed1').set(True)
    add4.parm('prim0').set('0 1 2 3')
    add4.parm('prim1').set('4 5 6 7')
    add4.parm('prim2').set('0 2')
    add4.parm('prim3').set('1 3')
    add4.parm('prim4').set('4 6')
    add4.parm('prim5').set('5 7')

    color5 = add4.createOutputNode('color')
    color5.parm('colorr').set(0.898039) #0.447059
    color5.parm('colorg').set(0.2) #0.4
    color5.parm('colorb').set(0.2) #0.298039

    null = camera.createNode('null')

    merge = color4.createOutputNode('merge')
    merge.setNextInput(color5)

    switch = null.createOutputNode('switch')

    switch.setNextInput(color3)
    switch.setNextInput(merge)

    merge2 = color1.createOutputNode('merge')
    merge2.setNextInput(color2)
    merge2.setNextInput(switch)
    merge2.setDisplayFlag(True)
    # merge.setRenderFlag(True)

    null2 = camera.createNode('null')
    null2.setRenderFlag(True)
    null2.moveToGoodPosition()

    camera.layoutChildren()
    # camera.setDeleteScript('print("camera deleted")', language=hou.scriptLanguage.Python)
    return _camera_target


def importCameraFromClipboard():
    obj = hou.node('/obj')
    camera = None
    camera_name = ''
    camera_type = ''
    camera_target = None
    is_tuple = False
    clipboard = QtWidgets.QApplication.clipboard()
    text = clipboard.text()
    lines = text.splitlines()

    error_count = 0

    if lines[0].startswith('#camera_export'):
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
                    camera_name = parm_val
                    camera = obj.node(camera_name)
                    if camera == None:
                        camera = obj.createNode('cam')
                        camera.setName(camera_name)
                        camera.moveToGoodPosition()
                    else:
                        for p in (camera.parms()):
                            p.deleteAllKeyframes()
                            p.revertToDefaults()

                        camera.parm('constraints_on').set(1)
                        camera.parm('constraints_path').set('constraints')

                # elif parm_name == 'type':
                #     camera_type = parm_val
                #     if camera_type == 'target':
                #         camera_target = obj.node(camera_name + '_target')
                #         if camera_target == None:
                #             camera_target = createCameraTarget(obj, camera)
                #         else:
                #             for p in (camera_target.parms()):
                #                 p.deleteAllKeyframes()

                elif line.startswith('target_'):
                    camera_target = obj.node(camera_name + '_target')
                    if camera_target == None:
                        camera_target = createCameraTarget(obj, camera)
                    else:
                        for p in (camera_target.parms()):
                            p.deleteAllKeyframes()

                    if is_tuple:
                        for k in parm_val:
                            setKey = hou.Keyframe()
                            setKey.setFrame(k[0])
                            setKey.setValue(k[1])
                            camera_target.parm(parm_name[7:]).setKeyframe(setKey)
                    else:
                        camera_target.parm(parm_name[7:]).set(parm_val)

                else:
                    try:
                        if is_tuple:
                            for k in parm_val:
                                setKey = hou.Keyframe()
                                setKey.setFrame(k[0])
                                setKey.setValue(k[1])
                                camera.parm(parm_name).setKeyframe(setKey)
                        else:
                            camera.parm(parm_name).set(parm_val)
                    except:
                        print('cannot setting parameter: ' + parm_name)
                        error_count += 1

        if error_count == 0:
            print('camera successfully imported')
        else:
            print('camera imported with ' + str(error_count) + " errors")

    else:
        print('cannot apply clipboad values, wrong type!')


importCameraFromClipboard()
