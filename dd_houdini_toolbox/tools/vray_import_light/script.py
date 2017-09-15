import hou


obj = hou.node('/obj')
vrlight_name = vrlight_type = ''
vrlight = None

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

fname = hou.ui.selectFile(None, 'Select .parm file', False, hou.fileType.Any, '*.parm')
if fname != '':
    with open(fname) as f:
        for line in f:
            if line != '':
                ls = line.split(',', 1)
                if len(ls) == 2:
                    parm_name = ls[0]
                    parm_val = ls[1]

                    if parm_val.startswith('\'') and parm_val.endswith('\''):
                        parm_val = parm_val[1:-2]
                    else:
                        parm_val = eval(parm_val)

                    if line.startswith('#name'):
                        vrlight_name = parm_val

                    elif line.startswith('#type'):
                        vrlight_type = parm_val
                        vrlight = obj.node(vrlight_name)

                        if vrlight == None:
                            vrlight = obj.createNode(vrlight_type)
                            vrlight.setName(vrlight_name)
                            vrlight.setColor(hou.Color(1, 0.898039, 0))
                            vrlight.setUserData('nodeshape', 'light')
                            vrlight.moveToGoodPosition()

                            out_node = None
                            for n in vrlight.children():
                                if n.isGenericFlagSet(hou.nodeFlag.Render) == True:
                                    out_node = n
                            color = out_node.createOutputNode('color')
                            color.parm('colorr').set(1)
                            color.parm('colorg').set(0.898039)
                            color.parm('colorb').set(0)
                            color.setDisplayFlag(True)

                            if vrlight_type == 'VRayNodeLightSphere':
                                vrlight.node('sphere1').parm('type').set(4)
                                vrlight.node('sphere1').parm('imperfect').set(0)

                            if vrlight_type == 'VRayNodeLightRectangle':
                                vrlight.node('line1').parm('dist').setExpression(
                                    '(ch("../u_size") + ch("../v_size")) * 0.333')
                                vrlight.node('grid1').parm('type').set(2)
                                vrlight.node('grid1').parm('orderu').set(2)
                                vrlight.node('grid1').parm('orderv').set(2)
                                switch = vrlight.node('grid1').createOutputNode('switch')
                                switch.parm('input').setExpression('ch("../is_disc")')
                                circle = vrlight.createNode('circle')
                                circle.parm('type').set(2)
                                circle.parm('radx').setExpression('ch("../u_size") / 2')
                                circle.parm('rady').setExpression('ch("../v_size") / 2')
                                #vrlight.parm('v_size').setExpression('ch("u_size")')
                                switch.setNextInput(circle)
                                vrlight.node('merge1').setInput(0, switch)
                                #vrlight.layoutChildren()

                            if vrlight_type == 'VRayNodeSunLight':
                                '''
                                vrlight.node('transform1').parm('sx').setExpression('ch("../size_multiplier")')
                                vrlight.node('transform1').parm('sy').setExpression('ch("../size_multiplier")')
                                vrlight.node('transform1').parm('sz').setExpression('ch("../size_multiplier")')
                                '''

                                vrlight_target = obj.node(vrlight_name + '_target')
                                if vrlight_target == None:
                                    vrlight_target = obj.createNode('null', vrlight_name + '_target')
                                    vrlight_target.moveToGoodPosition()

                                    parm_group = vrlight_target.parmTemplateGroup()
                                    parm_group.insertBefore(parm_group.findFolder("Transform"),
                                                            hou.StringParmTemplate('light', 'Light', 1,
                                                                                   string_type=hou.stringParmType.NodeReference))
                                    vrlight_target.setParmTemplateGroup(parm_group)
                                    vrlight_target.parm('light').set(vrlight.path())

                                    parm_group = vrlight.parmTemplateGroup()
                                    parm_group.insertBefore(parm_group.findFolder("Transform"),
                                                            hou.StringParmTemplate('target', 'Target', 1,
                                                                                   string_type=hou.stringParmType.NodeReference))
                                    vrlight.setParmTemplateGroup(parm_group)
                                    vrlight.parm('target').set(vrlight_target.path())

                                    vrlight_target.parm('dcolorr').set(1)
                                    vrlight_target.parm('dcolorg').set(0.898039)
                                    vrlight_target.parm('dcolorb').set(0)
                                    vrlight_target.parm('geoscale').set(0.2)
                                    vrlight_target.parm('controltype').set(2)
                                    vrlight_target.setColor(hou.Color(1, 0.898039, 0))
                                    vrlight_target.setUserData('nodeshape', 'circle')


                                    addTargetNodeController(vrlight, vrlight_target)
                                    vrlight.node('constraints').node('lookat').parm('twist').setExpression(
                                        'ch("../../rz")')

                                    circle1 = vrlight.node('circle1')
                                    circle1.parm('type').set(2)

                                    transform4 = circle1.createOutputNode('xform')
                                    transform4.parm('scale').set(1.5)
                                    merge1 = vrlight.node('merge1')
                                    merge1.setInput(0, transform4)

                                    transform2 = vrlight.node('transform2')
                                    transform2.parm('tx').setExpression('ch("../transform4/scale")')
                                    transform2.parm('scale').deleteAllKeyframes()
                                    transform2.parm('scale').set(0.5)

                                    vrlight.node('transform1').parm('scale').setExpression('ch("../size_multiplier")')

                                    points = vrlight.createNode('add', 'points')
                                    points.parm('points').set(2)
                                    points.parm('usept0').set(1)
                                    points.parm('usept1').set(1)
                                    points.parm('pt0z').setExpression('-ch("../transform1/scale") * 0.66')
                                    points.parm('pt1z').setExpression(
                                        '-distance(ch("../../' + vrlight_name + '_target/tx"), ch("../../' + vrlight_name + '_target/ty"), ch("../../' + vrlight_name + '_target/tz"), ch("../tx"), ch("../ty"), ch("../tz"))')
                                    line = points.createOutputNode('add', 'line')
                                    line.parm('prim0').set('0-1')
                                    color1 = line.createOutputNode('color')
                                    color1.parm('colorr').set(0.099)
                                    color1.parm('colorg').set(0.45)
                                    color1.parm('colorb').set(0.9)

                                    color2 = vrlight.node('color1')
                                    merge1 = color2.createOutputNode('merge')
                                    merge1.setNextInput(color1)
                                    merge1.setDisplayFlag(True)
                                    # merge.setRenderFlag(True)
                                    #null = vrlight.createNode('null')
                                    #null.setRenderFlag(True)
                                    #null.moveToGoodPosition()
                                    #vrlight.layoutChildren()
                                    # camera.setDeleteScript('print("camera deleted")', language=hou.scriptLanguage.Python)

                            #color.parm('colorr').set(1)
                            #color.parm('colorg').set(0.898039)
                            #color.parm('colorb').set(0)
                            #color.setDisplayFlag(True)

                            null = vrlight.createNode('null')
                            null.setRenderFlag(True)
                            #null.moveToGoodPosition()
                            vrlight.layoutChildren()

                        else:
                            if vrlight.type().name() != vrlight_type:
                                vrlight.changeNodeType(vrlight_type)
                            for p in (vrlight.parms()):
                                p.revertToDefaults()

                    elif line.startswith('#targ'):
                        vrlight_target.parm(parm_name[5:]).set(parm_val)

                    elif line.startswith('#'):
                        vrlight.parm(parm_name[1:]).set(parm_val)
                    else:
                        try:
                            vrlight.parm(parm_name).set(parm_val)
                        except:
                            print('cannot setting parameter: ' + parm_name)
