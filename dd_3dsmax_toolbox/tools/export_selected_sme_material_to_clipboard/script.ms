fn getsmeselectedmaterials =
(
	viewNode = sme.GetView (sme.activeView)
	smeSelMats = #()
	for n = 1 to trackViewNodes[#sme][(sme.activeView)].numSubs do (
		m = trackViewNodes[#sme][(sme.activeView)][n].reference
		b = viewNode.GetNodeByRef m
		if b.selected and superclassof m == material do append smeSelMats m
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
	lib_dir = getparentfolder( trimRight ( getFilenamePath ( getThisScriptFilename() ) ) "\\/" ) + "\\lib\\"
	if n != undefined then
	(
		if findstring ((classof n) as string) "VRay" != undefined or findstring ((classof n) as string) "V_Ray" != undefined then
		(
			pc_fname = lib_dir + "\\" + tolower((classOf n) as string) + ".pc"
			if doesfileexist pc_fname then
			(
			    _type = ""

				_name = ""
				try(_name = "_" + n.name)catch()
				_name = substituteString _name " - " "_"
				_name = substituteString _name " " "_"
				_name = substituteString _name "-" "_"

                file = openFile pc_fname
                script = ""
                while not eof file do
                (
                    _r =  readLine file --read the first line and store as a string it in _r
                    if substring _r 1 1 == "#" then
                    (
                        _type = substring _r 2 -1
                        script += "#" + _type + "\n"
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


                        parmval = (execute (" glob_n." + parmfrom)) as string

                        if convert_fn != undefined do
                            parmval = ( execute ( convert_fn + " glob_n." + parmfrom ) ) as string
                        if type == "Boolean" do
                            parmval = upperfirst parmval

                        if type == "String" do
                            parmval = "'" + parmval + "'"

                        script += parmto + "," + parmval + "\n"
                    )
                )
                seek file 0    -- reset position to beginning
                close file -- closes the file

                setclipboardText script
	            print( "Material successfully exported to clipboard" )

			)else (messagebox "Conversion file not found for this node type!")
		)else (messagebox "This node is not a VRay type!")
	)else (messagebox "Nothing to export!")
)

smeselection = getsmeselectedmaterials()

if smeselection.count == 1 then
    exportselectednodeparameters smeselection[1]
else
    if smeselection.count == 0 then
        messageBox("Nothing to export")
    else
        messageBox("More then one object selected")
