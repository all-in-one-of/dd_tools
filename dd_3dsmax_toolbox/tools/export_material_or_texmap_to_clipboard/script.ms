fn getsmeselectednode =
(
    smeSelMats = #()
    if (sme.IsOpen()) do
    (
        viewNode = sme.GetView ( sme.activeView )
        for n = 1 to trackViewNodes[#sme][( sme.activeView )].numSubs do
        (
            m = trackViewNodes[#sme][( sme.activeView )][n].reference
            b = viewNode.GetNodeByRef m
            if b.selected and ( superClassOf m == material or  superClassOf m == textureMap ) do append smeSelMats m
        )
	)
	smeSelMats
)

fn getparentfolder _f =
(
    for i = _f.count to 1 by -1 do
    (
        if _f[i] == "\\" do
        (
            _f = substring _f 1 (i-1)
            exit
        )
    )
    _f
)

fn upperfirst s = ((toUpper s[1]) + (substring s 2 s.count))

fn exportselectednodeparameters n =
(
	global glob_n
	glob_n = n
	lib_dir = getparentfolder( trimRight ( getfilenamePath ( getThisScriptfilename() ) ) "\\/" ) + "\\lib\\"
	if n != undefined then
	(
		if findstring ((classOf n) as string) "VRay" != undefined or findstring ((classOf n) as string) "V_Ray" != undefined then
		(
			pc_fname = lib_dir + "\\" + tolower((classOf n) as string) + ".pc"
			if doesFileExist pc_fname then
			(
			    _type = ""

				_name = ""
				try(_name = n.name)catch()
				_name = substituteString _name " - " "_"
				_name = substituteString _name " " "_"
				_name = substituteString _name "-" "_"
                --_name = toLower( _name )

                _file = openfile pc_fname
                _script = "#parm_export\n\n"
                while not eof _file do
                (
                    _r =  readLine _file --read the first line and store as a string it in _r
                    if substring _r 1 1 == "#" then
                    (
                        _type = substring _r 2 -1
                        _script += "type,'" + _type + "'\n"
                        _script += "name,'" + _name + "'\n"
                    )
                    else if substring _r 1 3 == "fn " then
                        execute _r
                    else if _r != "" and _r[1] != "!" do
                    (
                        split1 = filterString _r ":"
                        split2 = filterString split1[1] "/"
                        split3 = filterString split2[1] ">"

                        convert_fn = split1[2]
                        type = split2[2]
                        parmfrom = split3[1] as string
                        parmto = split3[2] as string

                        if substring parmfrom 1 1 != "[" then
                            parmval = ( execute ( " glob_n." + parmfrom ) ) as string
                        else
                        (
                           parmval = substring parmfrom 2 ( parmfrom.count-2 )
                           print( parmval )
                        )


                        if convert_fn != undefined do
                            parmval = ( execute ( convert_fn + " glob_n." + parmfrom ) ) as string
                        if type == "Boolean" do
                            parmval = upperfirst parmval

                        if type == "String" do
                            parmval = "'" + parmval + "'"

                        _script += parmto + "," + parmval + "\n"
                    )
                )
                seek _file 0    -- reset position to beginning
                close _file -- closes the _file

                setclipboardText _script
	            print( "Material/Texmap successfully exported to clipboard" )

			)else (messageBox "Conversion file not found for this node type!")
		)else (messageBox "This node is not a VRay type!")
	)else (messageBox "Nothing to export!")
)

_o = undefined
_sme = getsmeselectednode()

if _sme.count == 1 then
    _o = _sme[1]
else if selection.count == 1 then
    if selection[1].material != undefined do
        _o = selection[1].material

if _o != undefined then
    exportselectednodeparameters _o
else
    if _sme.count == 0 then
        messageBox("Nothing to export")
    else
        messageBox("More then one object selected")
