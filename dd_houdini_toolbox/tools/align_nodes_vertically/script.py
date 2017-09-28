import hou

selectedNodes = hou.selectedNodes()
selectedNodes = sorted(selectedNodes, key=lambda x: -x.position()[1])

if len(selectedNodes) > 1:
    pos = selectedNodes[0].position()
    for i in range(1, len(selectedNodes)):
        pos[1] -= 1
        selectedNodes[i].setPosition(pos)
else:
    hou.ui.displayMessage("Please select nodes")
