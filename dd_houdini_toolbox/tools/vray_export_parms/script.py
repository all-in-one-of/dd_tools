import hou

class cfile(file):
    #subclass file to have a more convienient use of writeline
    def __init__(self, name, mode = 'r'):
        self = file.__init__(self, name, mode)

    def wl(self, string):
        self.writelines(string + '\n')
        return None

selectedNodes = hou.selectedNodes()
if len(selectedNodes) != 0:
    m = selectedNodes[0]
    fname = hou.ui.selectFile('', '', False, hou.fileType.Any, '*.txt', 'hou_vray_' + m.type().name().lower() + '_params.txt')
    if (fname != ''):
        fid = cfile(fname, 'w')
        parameters = m.parms()
        parameters = sorted(parameters, key=lambda x: x.name())
        for i in range(0, len(parameters)):
                fid.wl("name: " + parameters[i].name() + " - type: " + parameters[i].parmTemplate().type().name() + " - value: " + str(parameters[i].eval()))
        fid.close()
    else:
        hou.ui.displayMessage("Enter a valid filename")
else:
    hou.ui.displayMessage("Nothing to export")
