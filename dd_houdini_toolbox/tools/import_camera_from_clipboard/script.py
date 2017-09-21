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
    camera.setParmTemplateGroup(parm_group)
    camera.parm('target').set(_camera_target.path())

    _camera_target.parm('dcolorr').set(0)
    _camera_target.parm('dcolorg').set(0)
    _camera_target.parm('dcolorb').set(0.5)
    _camera_target.parm('geoscale').set(0.2)
    _camera_target.parm('controltype').set(2)
    _camera_target.setColor(hou.Color(0.298039, 0.54902, 0.74902))
    _camera_target.setUserData('nodeshape', 'circle')
    _camera_target.setDisplayFlag(False)
    _camera_target.moveToGoodPosition()

    addTargetNodeController(camera, _camera_target)

    camera.node('constraints').node('lookat').parm('twist').setExpression('ch("../../rz")')
    camera.parm('focus').setExpression(
        'distance(ch("tx"), ch("ty"), ch("tz"), ch("../' + camera.name() + '_target/tx"), ch("../' + camera.name() + '_target/ty"), ch("../' + camera.name() + '_target/tz"))')

    points = camera.createNode('add', 'points')
    points.parm('points').set(2)
    points.parm('usept0').set(1)
    points.parm('usept1').set(1)
    points.parm('pt1z').setExpression(
        '-distance(ch("../../' + camera.name() + '_target/tx"), ch("../../' + camera.name() + '_target/ty"), ch("../../' + camera.name() + '_target/tz"), ch("../tx"), ch("../ty"), ch("../tz"))')

    line = points.createOutputNode('add', 'line')
    line.parm('prim0').set('0-1')

    color1 = line.createOutputNode('color')
    color1.parm('colorr').set(0.099)
    color1.parm('colorg').set(0.45)
    color1.parm('colorb').set(0.9)

    merge = color1.createOutputNode('merge')

    xform = camera.node('xform1')

    color2 = xform.createOutputNode('color')
    color2.parm('colorr').set(0.11172)
    color2.parm('colorg').set(0.342342)
    color2.parm('colorb').set(0.84)

    merge.setNextInput(color2)
    merge.setDisplayFlag(True)
    # merge.setRenderFlag(True)

    null = camera.createNode('null')
    null.setRenderFlag(True)
    null.moveToGoodPosition()

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

                elif parm_name == 'type':
                    camera_type = parm_val
                    if camera_type == 'target':
                        camera_target = obj.node(camera_name + '_target')
                        if camera_target == None:
                            camera_target = createCameraTarget(obj, camera)
                        else:
                            for p in (camera_target.parms()):
                                p.deleteAllKeyframes()

                elif line.startswith('target_'):
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

    else:
        print('cannot apply clipboad values, wrong type!')


importCameraFromClipboard()
