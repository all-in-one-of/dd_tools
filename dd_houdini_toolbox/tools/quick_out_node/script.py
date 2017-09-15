import hou

selectedNodes = hou.selectedNodes()

if len(selectedNodes) is not 0:
    for node in selectedNodes:
        outNode = node.parent().createNode('null', 'OUT')
        hou.node(outNode.path()).setInput(0, hou.node(node.path()))
        outNode.moveToGoodPosition()
        outNode.setColor(hou.Color([1, 0, 0]))
        outNode.setSelected(True, True)
        outNode.setDisplayFlag(True)
        outNode.setRenderFlag(True)
else:
    hou.ui.displayMessage("Please select a node")