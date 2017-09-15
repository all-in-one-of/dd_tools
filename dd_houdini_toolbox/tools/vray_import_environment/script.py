import hou
from vfh import vfh_rop

'''('Angular', 'Cubic', 'Spherical', 'Mirror Ball', 'Screen', 'Spherical (3ds max)', 'Spherical (V-Ray)', 'Cylindrical (3ds max)'
, 'Shrink Wrap (3ds max)')'''

vrayRopNode = vfh_rop._getVrayRop()
if vrayRopNode != None:
    env_node = hou.node(vrayRopNode.parm('render_network_environment').eval())
    if env_node == None:
        rop = hou.node('/out')
        env_node = rop.createNode('vray_environment', 'env')
        vrayRopNode.parm('render_network_environment').set(env_node.path())
        rop.layoutChildren()
        hou.node(vrayRopNode.parm('render_network_environment').set(env_node.path()))

        menu_items = (
        'Angular', 'Cubic', 'Spherical', 'Mirror Ball', 'Screen', 'Spherical (3ds max)', 'Spherical (V-Ray)',
        'Cylindrical (3ds max)', 'Shrink Wrap (3ds max)')

        env_node.addSpareParmTuple(hou.StringParmTemplate("file", "File", 1, (), hou.parmNamingScheme.Base1, hou.stringParmType.FileReference))

        env_node.addSpareParmTuple(hou.MenuParmTemplate("mapping_type", "Mapping Type", menu_items, menu_items, 2))
        env_node.addSpareParmTuple(hou.FloatParmTemplate('h_rotation', 'Horiz. Rotation', 1, (0,), 0.0, 360.0))
        #env_node.addSpareParmTuple(hou.FloatParmTemplate('v_rotation', 'Vert. Rotation', 1, (0,), 0.0, 360.0))
        env_node.addSpareParmTuple(hou.ToggleParmTemplate('h_flip', 'Flip Horizontally', 0))
        #env_node.addSpareParmTuple(hou.ToggleParmTemplate('v_flip', 'Flip Vertically', 0))

        env_node.addSpareParmTuple(hou.ToggleParmTemplate('ground_on', 'Ground Projection', 0))
        env_node.addSpareParmTuple(
            hou.FloatParmTemplate('ground_radius', 'Radius', 1, (1000,), 0.0, 1000000.0, False, False,
                                  hou.parmLook.Regular, hou.parmNamingScheme.XYZW, '{ground_on 0}'))

        env_node.addSpareParmTuple(hou.FloatParmTemplate('overall_mult', 'Overall Mult', 1, (1,), 0.0, 100.0))
        env_node.addSpareParmTuple(hou.FloatParmTemplate('inverse_gamma', 'Inverse Gamma', 1, (1,), 0.0, 100.0))


    out_env_settings = env_node.children()[0]

    imageFile = env_node.node('imagefile')
    imageFile.parm('filter_type').set(2) #a verifier !
    imageFile.parm('filter_blur').set(0.1) #a verifier !
    imageFile.parm('color_space').set(1) # ou .set(0) a verifier !
    #imageFile.parm('gamma').setExpression('ch("../inverse_gamma")')
    imageFile.parm('file').set('`chs("../file")`')

    envMapping = env_node.node('environment_mapping')
    envMapping.parm('mapping_type').setExpression('ch("../mapping_type")')
    envMapping.parm('ground_on').setExpression('ch("../ground_on")')
    envMapping.parm('ground_radius').setExpression('ch("../ground_radius") / 100.')

    imageTexture = env_node.node('imagetexture')
    imageTexture.parm('color_multr').setExpression('ch("../overall_mult")')
    imageTexture.parm('color_multg').setExpression('ch("../overall_mult")')
    imageTexture.parm('color_multb').setExpression('ch("../overall_mult")')

    rotation = env_node.node('rotation')
    if (rotation == None):
        rotation = env_node.createNode('makexform' ,'rotation')

        '''for p in (rotation.parmTuples()):
            parm_templ = p.parmTemplate()
            parm_templ.hide(True)
            rotation.replaceSpareParmTuple(p.name(), parm_templ)'''

        #rotation.addSpareParmTuple(hou.FloatParmTemplate('rotation', 'Rotation', 1, (0,), 0.0, 360.0))
        rotation.parm('trans1').setExpression('0.25 + ch("../h_rotation") / 360.')
        rotation.parm('scale1').setExpression('if(ch("../h_flip")==0,-1,1)')
        rotation.setGenericFlag(hou.nodeFlag.InOutDetailLow, True)

        rotation.updateParmStates()

        envMapping.setInput(1, rotation)
        env_node.layoutChildren()

    inversegamma = env_node.node('inversegamma')
    if (inversegamma == None):
        inversegamma = env_node.createNode('VRayNodeTexMaxGamma', 'inversegamma')
        inversegamma.parm('color_space').set(1)
        inversegamma.parm('gamma').setExpression('ch("../inverse_gamma")')
        inversegamma.setInput(0, imageTexture)
        out_env_settings.setInput(0, inversegamma)
        out_env_settings.setInput(1, inversegamma)
        out_env_settings.setInput(2, inversegamma)
        out_env_settings.setInput(3, inversegamma)
        out_env_settings.setInput(4, inversegamma)
        env_node.layoutChildren()

else:
    hou.ui.displayMessage("No VRay Rop node finded")
