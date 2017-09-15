import hou
from vfh import vfh_rop


'''
('Atmosphere', 'Diffuse', 'Reflection', 'Refraction', 'Self Illumination', 'Shadow', 'Specular', 'Lighting', 'GI', 'Caust
ics', 'Raw GI', 'Raw Lightning', 'Raw Shadow', 'Velocity', 'Render ID', 'Material ID', 'Node ID', 'Z-Depth', 'Reflection 
Filter', 'Raw Reflection', 'Refraction Filter', 'Raw Refraction', 'Real Color', 'Normal', 'Background', 'Alpha', 'Color',
 'Wire Color', 'Matte / Shadow', 'Total Lightning', 'Raw Total Lightning', 'Bump / Normal', 'Samplerate', 'SSS', 'DR Buck
et', 'Reflection Glossiness', 'Reflection Hilights', 'Refraction Glossiness', 'Shademap Export', 'Reflection Alpha', 'Ref
lection IOR', 'Material Render ID', 'Noise Level')

2 cas particuliers pour l'instant:

'VRayNodeRenderChannelZDepth' --> 17
'VRayNodeRenderChannelBumpNormals' --> 31
'VRayNodeRenderChannelMultiMatte' --> 43
'VRayNodeRenderChannelRenderID' --> 14
'VRayNodeRenderChannelVelocity' --> 13
'VRayNodeRenderChannelExtraTex' --> 44
'''

vrayRopNode = vfh_rop._getVrayRop()
if vrayRopNode != None:
    render_elmt_node = hou.node(vrayRopNode.parm('render_network_render_channels').eval())
    if render_elmt_node == None:
        rop = hou.node('/out')
        render_elmt_node = rop.createNode('vray_render_channels', 'render_elements')
        vrayRopNode.parm('render_network_render_channels').set(render_elmt_node.path())
        rop.layoutChildren()

    out_container = render_elmt_node.children()[0]

    default_choices = list()
    render_elmts = out_container.inputs()
    for i in range(0, len(render_elmts)):
        if render_elmts[i] != None:
            if render_elmts[i].type().name() == 'VRayNodeRenderChannelZDepth':
                default_choices.append(17)
            elif render_elmts[i].type().name() == 'VRayNodeRenderChannelBumpNormals':
                default_choices.append(31)
            elif render_elmts[i].type().name() == 'VRayNodeRenderChannelMultiMatte':
                default_choices.append(43)
            elif render_elmts[i].type().name() == 'VRayNodeRenderChannelRenderID':
                default_choices.append(14)
            elif render_elmts[i].type().name() == 'VRayNodeRenderChannelVelocity':
                default_choices.append(13)
            elif render_elmts[i].type().name() == 'VRayNodeRenderChannelExtraTex':
                if render_elmts[i].inputs()[0].type().name() == 'VRayNodeTexDirt':
                    default_choices.append(44)
            else:
                default_choices.append(render_elmts[i].parm('alias').eval())

    # getting the render elements list with a temporary colorchannel node
    render_elmt = render_elmt_node.createNode('VRayNodeRenderChannelColor', 'colorchannel')
    menu_items = list(render_elmt.parm('alias').menuItems())
    menu_items.append('MultiMatte')
    menu_items.append('Dirt')
    render_elmt.destroy()

    result = hou.ui.selectFromList(menu_items, default_choices=default_choices, exclusive=False, message=None,
                                   title='Render Elements',
                                   column_header='', num_visible_rows=10)

    # removing old elements
    render_elmts = out_container.inputs()
    for i in range(len(render_elmts) - 1, -1, -1):
        if render_elmts[i] != None:
            if render_elmts[i].type().name() == 'VRayNodeRenderChannelZDepth':
                if result.__contains__(17) == False:
                    render_elmts[i].destroy()
            elif render_elmts[i].type().name() == 'VRayNodeRenderChannelBumpNormals':
                if result.__contains__(31) == False:
                    render_elmts[i].destroy()
            elif render_elmts[i].type().name() == 'VRayNodeRenderChannelMultiMatte':
                if result.__contains__(43) == False:
                    render_elmts[i].destroy()
            elif render_elmts[i].type().name() == 'VRayNodeRenderChannelRenderID':
                if result.__contains__(14) == False:
                    render_elmts[i].destroy()
            elif render_elmts[i].type().name() == 'VRayNodeRenderChannelVelocity':
                if result.__contains__(13) == False:
                    render_elmts[i].destroy()
            elif render_elmts[i].type().name() == 'VRayNodeRenderChannelExtraTex':
                if render_elmts[i].inputs()[0].type().name() == 'VRayNodeTexDirt':
                    if result.__contains__(44) == False:
                        render_elmts[i].inputs()[0].destroy()
                        render_elmts[i].destroy()
            else:
                if result.__contains__(render_elmts[i].parm('alias').eval()) == False:
                    render_elmts[i].destroy()

    # adding new elements
    for i in range(0, len(result)):
        if default_choices.__contains__(result[i]) == False:
            if result[i] == 17:
                render_elmt = render_elmt_node.createNode('VRayNodeRenderChannelZDepth',
                                                      menu_items[result[i]].replace(' / ', '_').replace(" ", "_").replace("-", "_"))
            elif result[i] == 31:
                render_elmt = render_elmt_node.createNode('VRayNodeRenderChannelBumpNormals',
                                                      menu_items[result[i]].replace(' / ', '_').replace(" ", "_").replace("-", "_"))
            elif result[i] == 43:
                render_elmt = render_elmt_node.createNode('VRayNodeRenderChannelMultiMatte',
                                                      menu_items[result[i]].replace(' / ', '_').replace(" ", "_").replace("-", "_"))
            elif result[i] == 14:
                render_elmt = render_elmt_node.createNode('VRayNodeRenderChannelRenderID',
                                                      menu_items[result[i]].replace(' / ', '_').replace(" ", "_").replace("-", "_"))
            elif result[i] == 13:
                render_elmt = render_elmt_node.createNode('VRayNodeRenderChannelVelocity',
                                                      menu_items[result[i]].replace(' / ', '_').replace(" ", "_").replace("-", "_"))
            elif result[i] == 44:
                render_elmt = render_elmt_node.createNode('VRayNodeRenderChannelExtraTex',
                                                      menu_items[result[i]].replace(' / ', '_').replace(" ", "_").replace("-", "_"))
                texDirt = render_elmt_node.createNode('VRayNodeTexDirt', 'TexDirt')
                texDirt.setGenericFlag(hou.nodeFlag.InOutDetailLow, True)
                render_elmt.setInput(0, texDirt)
            else:
                render_elmt = render_elmt_node.createNode('VRayNodeRenderChannelColor',
                                                      menu_items[result[i]].replace(' / ', '_').replace(" ", "_").replace("-", "_"))
                render_elmt.parm('alias').set(result[i])

            #render_elmt.parm('name').set('`chs("alias")`')
            render_elmt.parm('name').set(menu_items[result[i]].replace(' / ', ' ').replace("-", " "))
            out_container.setNextInput(render_elmt)


    #reordering by name !EXPERIMENTAL!
    render_elmts = out_container.inputs()
    render_elmts_tuple = list()
    for i in range(0, len(render_elmts)):
        if render_elmts[i] != None:
            render_elmts_tuple.append((i, render_elmts[i].parm('name').eval()))
    render_elmts_tuple = sorted(render_elmts_tuple, key=lambda x: x[1])
    for i in range(0, len(render_elmts_tuple)):
        out_container.setInput(i, render_elmts[render_elmts_tuple[i][0]], 0)

    render_elmt_node.layoutChildren()

else:
    hou.ui.displayMessage("No VRay Rop node finded")
