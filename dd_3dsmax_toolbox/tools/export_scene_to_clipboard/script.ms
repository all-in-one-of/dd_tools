fn filter_kernel_convert _val = case classOf _val of (Area : 1;VRayBoxFilter : 2;Catmull_Rom : 3;Cook_Variable : 4;Soften : 5;VRayLanczosFilter : 6;Mitchell_Netravali : 7;VRayMitNetFilter : 7;VRaySincFilter : 8;VRayTriangleFilter : 9;default : 6)


fn appendLineToFile _f _str _var = (

    try(
        _lines = (dotNetClass "System.IO.File").ReadAllLines _f
        while _lines[_lines.count] == "" do deleteItem _lines (_lines.count)
        append _lines (substituteString _str "%" _var)
        (dotNetClass "System.IO.File").WriteAllLines _f _lines
    )catch(print "cannot append line to file...")
)


fn writeToFile _f _str = (

    (dotNetClass "System.IO.File").WriteAllText _f _str
)


fn getHierarchy _o _opath:"" = (
	_opath = "/" + _o.name + _opath
	if _o.parent != undefined do
	(
		_opath = getHierarchy _o.parent _opath:_opath
	)
	_opath
)

fn getListenerCurrentPos = (
    setListenerSel #(-1,-1)
    _pos = (getListenerSel())[1]
    _pos
)

fn clearListnerFromPos _from = (
    setListenerSel #(-1,-1)
    _to = (getListenerSel())[2]
    setListenerSel #(_from,_to)
    setListenerSelText ""
    --uiaccessor.closedialog (windows.getchildhwnd 0 "MAXScript Listener")[1]

)

fn exportGeometries _step:1 _substeps:1 = (
    _str = ""
    for _o in geometry do (
        _animated = ( _o.isAnimated or isDeformable _o )
        _name = substituteString ( substituteString _o.name " " "_" ) "." "_"
        _abcfile = sysinfo.tempdir + _name + ".abc"
        _frange = [0,100]
        _opath = getHierarchy _o
        if _animated == false then _frange = [currenttime.frame, currenttime.frame] else _frange = [animationrange.start.frame, animationrange.end.frame]

        if classOf _o != HairObject and classOf _o != GuidesObject then (
            _job = "filename=" + _abcfile
            _job += ";in=" + (_frange[1] as string)
            _job += ";out=" + (_frange[2] as string)
            _job += ";step=" + (_step as string)
            _job += ";substep=" + (_substeps as string)
            _job += ";purepointcache=false"
            _job += ";normals=true"
            _job += ";uvs=true"
            _job += ";materialids=true"
            _job += ";exportselected=false"
            _job += ";objects=" + getHierarchy _o
            _job += ";flattenhierarchy=true"
            _job += ";automaticinstancing=true"
            _job += ";facesets=partitioningFacesetsOnly"
            _job += ";transformCache=false"
            _job += ";validateMeshTopology=false"
            _job += ";renameConflictingNodes=false"
            _job += ";mergePolyMeshSubtree=true"
            _job += ";particlesystemtomeshconversion=true"
            --_job += ";dynamictopology=true"
            _job += ";transformCache=true"
            _job += ";storageFormat=hdf5"

            --_from = getListenerCurrentPos()

            _result = ExocortexAlembic.createExportJobs( _job )

            --clearListnerFromPos _from

            if( _result != 0 ) do (
                messageBox "Failure - See Maxscript Listener for details." title:"Exocortex Alembic Export"
                _abcfile = undefined
            )
        )else (
            --https://ephere.com/plugins/autodesk/max/ornatrix/docs/4/Alembic_Export.html#Examples
            --OxAlembicExport [string filePath] [bool exportSelectedHairs] [int startFrame] [int endFrame] [bool exportRenderVersion] [int upDirection] [int format]
            try(
                _result = OxAlembicExport _abcfile true _frange[1] _frange[2]-- false 1 0
            )catch(_abcfile = undefined)
        )

        if _abcfile != undefined do
        (
            _str += "AlembicGeometry " + _name + " {\n"
            _str += "  filename=\"" + _abcfile + "\";\n"
            _str += "  object_id=" + _o.gbufferChannel  as string + ";\n"
            _str += "  wirecolor=Color(" + ( _o.wirecolor.r / 255. ) as string + "," + ( _o.wirecolor.g/ 255. ) as string + "," + ( _o.wirecolor.b / 255. ) as string + ");\n"
            _str += "  handle=" + _o.inode.handle as string + ";\n"
            --here add user properties...
            for _line in (FilterString (getUserPropBuffer _o) "\n") do
            (
                _prop_str = substituteString (trimLeft (trimRight _line)) " = " "="
                _prop_split = FilterString _prop_str "="
                _prop_name = substituteString (toLower _prop_split[1]) "vray_" ""
                _prop_val = substituteString (substituteString _prop_split[2] "[" "Color(") "]" ")"
	            _str += "  " + _prop_name + "=" + _prop_val + ";\n"
	        )
            _str += "}\n\n"
        )
    )
    clearListener()
	_str
)


fn exportCustomSettings = (
    _rendercam = if getActiveCamera() != undefined then (getActiveCamera()).name else ""
    _fps = (framerate as float) as string
    _range = [animationrange.start.frame as integer , animationrange.end.frame as integer] as string

    _str = "CustomSettings scene_settings {\n  camera=\"" + _rendercam + "\";\n  fps=" + _fps + ";\n  range=" + _range + ";\n}\n"

    _aa_filter = if renderers.current.filter_on == false then 0 else filter_kernel_convert renderers.current.filter_kernel as string

    _str += "\nSettingsImageSampler aa_filter {\n  filter_type=" + _aa_filter + ";\n}\n"

    _str
)


fn writeVRScenefiles _start:currentframe _end:currentframe = (

    _vrscenefile = sysinfo.tempdir + getFilenameFile maxfilename

    _script = "#scene_export\n\n"

    if _start != currentframe and _end != currentframe then
            vrayExportRTScene ( _vrscenefile + ".vrscene" ) exportCompressed:false exportHEXFormatMesh:false exportHEXFormatTransf:false separateFiles:true exportView:false exportLights:false exportGeometry:false exportNodes:true exportMaterials:true exportTextures:true exportBitmaps:true prefix:"" startFrame:_start endFrame:_end stripPaths:false
        else
            vrayExportRTScene ( _vrscenefile + ".vrscene" ) exportCompressed:false exportHEXFormatMesh:false exportHEXFormatTransf:false separateFiles:true exportView:false exportLights:false exportGeometry:false exportNodes:true exportMaterials:true exportTextures:true exportBitmaps:true prefix:"" stripPaths:false

        _script += "filename," + _vrscenefile + ".vrscene" + "\n"


    setclipboardText _script

    renderSceneDialog.commit()

    appendLineToFile ( _vrscenefile + ".vrscene" ) "#include \"%\"\n" (_vrscenefile + "_cameras.vrscene")
    appendLineToFile ( _vrscenefile + ".vrscene" ) "#include \"%\"\n" (_vrscenefile + "_geometries.vrscene")
    appendLineToFile ( _vrscenefile + ".vrscene" ) "#include \"%\"\n" (_vrscenefile + "_settings.vrscene")

    writeToFile ( _vrscenefile + "_settings.vrscene" ) (exportCustomSettings())
    writeToFile ( _vrscenefile + "_geometries.vrscene" ) (exportGeometries())

    print "scene successfully exported"
)

writeVRScenefiles()
