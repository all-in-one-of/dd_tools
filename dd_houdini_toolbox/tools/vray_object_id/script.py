import hou

def addVRayObjectIdParamTemplate(node):
    parm_group = node.parmTemplateGroup()
    parm_folder = hou.FolderParmTemplate('folder', 'V-Ray Object')
    parm_folder.addParmTemplate(hou.IntParmTemplate('vray_objectID', 'Object ID', 1))
    parm_group.append(parm_folder)
    node.setParmTemplateGroup(parm_group)


geoList = filter(lambda item: item.type().category().typeName() == 'OBJ' and item.type().name() == 'geo', hou.selectedNodes())
map(addVRayObjectIdParamTemplate, geoList)