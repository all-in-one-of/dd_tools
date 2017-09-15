import hou


def setupObjIdParameters():


    def findRenderNodeInChildren(node):
        """scan node tree to return node with renderFlag activated
        """
        for n in node.children():
            if (n.isRenderFlagSet() == True):
                return n

    def createOutNode(node):
        """create null "OUT" node
        """
        if (node.name().find('OUT') == -1):
            outNode = node.parent().createNode('null', 'OUT')
            outNode.setInput(0, hou.node(node.path()))
            outNode.moveToGoodPosition()
            outNode.setColor(hou.Color([1, 0, 0]))
            # outNode.setSelected(True, True)
            outNode.setDisplayFlag(True)
            outNode.setRenderFlag(True)
            return outNode

    colors = ['{1, 0, 0}', '{0, 1, 0}', '{0, 0, 1}']
    mask_count = 0
    color_id = 0

    selectedNodes = hou.selectedNodes()
    if len(selectedNodes) is not 0:
        for node in selectedNodes:

            renderNode = findRenderNodeInChildren(node)
            if (renderNode.name().find('OUT') == -1):
                renderNode = createOutNode(renderNode)

            if (node.node('ObjId') == None):
                objectIdNode = node.createNode('attribwrangle', 'ObjId')
                objectIdNode.setInput(0, hou.node(renderNode.inputs()[0].path()))
            else:
                objectIdNode = node.node('ObjId')




            if color_id == 0:
                mask_count += 1

            objectIdNode.parm('snippet').set('v@objId' + str(mask_count) + ' = ' + str(colors[color_id]) + ';')
            color_id += 1
            if (color_id > 2):
                color_id = 0

            renderNode.setInput(0, hou.node(objectIdNode.path()))

            objectIdNode.moveToGoodPosition()
            renderNode.moveToGoodPosition()

            material = hou.node(node.parm('shop_materialpath').eval())

            networkBox = material.findNetworkBox('ObjIdParms')
            if networkBox != None:
                networkBox.setMinimized(False)


            for i in range(0, mask_count):
                if (material.node('ObjId' + str(i+1)) == None):
                    objectIdBindNode = material.createNode('bind', 'ObjId' + str(i+1))
                    objectIdBindNode.moveToGoodPosition()

                    if networkBox == None:
                        networkBox = material.createNetworkBox('ObjIdParms')
                        networkBox.setComment('Export ObjId Parameters')
                        networkBox.setColor(hou.Color([1, 0, 0]))
                        networkBox.setPosition(hou.Vector2(objectIdBindNode.position().x(), objectIdBindNode.position().y()))

                    networkBox.addNode(objectIdBindNode)

                    objectIdBindNode.parm('parmname').set('objId' + str(i+1))
                    objectIdBindNode.parm('parmtype').set(7)
                    objectIdBindNode.parm('exportparm').set(1)

            #material.layoutChildren(networkBox.nodes())
            networkBox.fitAroundContents()
            networkBox.resize(hou.Vector2(-1, 0))
            networkBox.setMinimized(True)

    return mask_count

def setupObjIdImagePlanes(mask_count):

    def getOutputNodes():
        """returns the rop nodes in the scene
        """
        ropContext = hou.node('/out')

        # get the children
        outNodes = ropContext.children()

        exclude_node_types = [
            hou.nodeType(hou.nodeTypeCategories()["Driver"], "wedge")
        ]

        # remove nodes in type in exclude_node_types list
        new_out_nodes = [node for node in outNodes
                         if node.type() not in exclude_node_types]

        return new_out_nodes

    output_nodes = getOutputNodes()
    if len(output_nodes) is not 0:
        for mantra in output_nodes:

            numAux = mantra.parm('vm_numaux').eval()

            for i in range(0, mask_count):
                found = False

                for j in range(0, numAux):
                    if (mantra.parm('vm_variable_plane' + str(j + 1)).eval() == 'objId' + str(i+1)):
                        found = True

                if found == False:
                    numAux += 1
                    mantra.parm('vm_numaux').set(numAux)
                    mantra.parm('vm_variable_plane' + str(numAux)).set('objId' + str(i + 1))
                    mantra.parm('vm_channel_plane' + str(numAux)).set('ObjId' + str(i + 1))

mask_count = setupObjIdParameters()
setupObjIdImagePlanes(mask_count)
