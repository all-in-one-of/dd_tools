import hou

selectedNodes = hou.selectedNodes()

if len(selectedNodes) is not 0:
    for node in selectedNodes:
        outputs = node.outputs()
        transformNode = node.createOutputNode('xform', 'pivot_to_bottom')
        #hou.node(transformNode.path()).setInput(0, hou.node(node.path()))



        transformNode.moveToGoodPosition()
        transformNode.parm('ty').setExpression(
            '-$YMIN', language=hou.exprLanguage.Hscript)
        transformNode.parm('py').setExpression(
            '$YMIN', language=hou.exprLanguage.Hscript)

        '''
        for i in range(0, len(outputs)):
            transformNode.setOutput(i, transformNode.path())
        '''

        for output in outputs:
            output.setFirstInput(transformNode)


        if (len(outputs) == 0):
            transformNode.setSelected(True, True)
            transformNode.setDisplayFlag(True)
            transformNode.setRenderFlag(True)
else:
    hou.ui.displayMessage("Please select a node")
