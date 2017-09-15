import hou
from vfh import vfh_rop

vrayRopNode = vfh_rop._getVrayRop()
cam = hou.node(vrayRopNode.parm('render_camera').eval())
if cam != None:
    hou.ui.paneTabOfType(hou.paneTabType.SceneViewer).curViewport().setCamera(cam)
