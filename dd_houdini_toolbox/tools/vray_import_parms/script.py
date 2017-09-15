import hou

error_count = 0
selectedNodes = hou.selectedNodes()
if len(selectedNodes) != 0:
    m = selectedNodes[0]

    fname = hou.ui.selectFile(None, 'Select .parm file', False, hou.fileType.Any, '*.parm')
    if fname != "":
        for p in (m.parms()):
            p.revertToDefaults()
        with open(fname) as f:
            for line in f:
                ls = line.split(',', 1)
                if len(ls) == 2:
                    try:
                        if ls[1].startswith('\'') and ls[1].endswith('\''):
                            m.parm(ls[0]).set(ls[1][1:-2])
                        else:
                            m.parm(ls[0]).set(eval(ls[1]))
                    except:
                        print('cannot setting parameter: ' + ls[0])
                        error_count += 1

            if error_count > 0:
                print('parameters imported with: ' + str(error_count) + ' errors')
            else:
                print('all parameters successfully imported')