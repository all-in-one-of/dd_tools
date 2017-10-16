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


fn maxToHoudiniTransform _t _prerotate = (
    if _prerotate == false then
        ( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] ) * _t * inverse( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] )
    else
        ( preRotateX ( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] ) -90 ) * _t * inverse( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] )
)


fn maxToHoudiniGetTransforms _o _prerotate:false _step:1 _substeps:1 = (
    _result = #()
    for _t = animationrange.start.frame to animationrange.end.frame by _step / _substeps do
    (
        append _result #( _t, ( maxToHoudiniTransform ( at time _t _o.transform )  _prerotate ) )
    )
    _result
)


fn normalizeName _name = (

    ( substituteString ( substituteString _name " " "_" ) "." "_" )
)


fn floatToString _float = (
    _split = FilterString ( _float as string ) "."
    if _split[2] as integer == 0 do _float = _float as integer
    _float as string
)


fn getPropertyValues _o _name _step:1 _substeps:1 _scale:1 = (

    _controller = getPropertyController _o _name
    _property = getProperty _o _name

    _result = #()
    if isController _controller then (
        for _t = animationrange.start.frame to animationrange.end.frame by _step / _substeps do (
            append _result #( _t, ( ( at time _t _controller.value  ) * _scale ) )
        )
    )
    else (
        append _result #( 0, ( _property * _scale ) )
    )
    _result
)


fn isAnimatedTuple _tuple = (

    _firstVal = _tuple[1][2]
    _isAnimated = false
    if _tuple.count > 1 do
    for i = 2 to _tuple.count do (
        --convert as string is needed for comparing two array values (maxscript issue...)
        if _tuple[i][2] as string != _firstVal as string do (
            _isAnimated = true
            exit
        )
    )
    _isAnimated
)


fn formatTuple _tuple = (

    _result = ""
    if ( isAnimatedTuple _tuple ) then (
        _result = "Keys("
        --for i in _tuple do _result += trimLeft( i as string ) "#" + ","
        for i in _tuple do _result += "(" + floatToString i[1] + ", " + floatToString i[2] + "), "
        _result = trimRight ( trimRight _result " " ) ","
        _result += ")"
    )else (
        --_result = _tuple[1][2] as string
        _result = floatToString _tuple[1][2]
    )
    _result
)


fn exportCameras _step:1 _substeps:1 = (
    _str = ""
    for _o in cameras where classOf _o != Targetobject and ( classOf _o == Freecamera or classOf _o == Targetcamera ) do (

        --if target
        if _o.target != undefined do (
            _str += "TargetNode " + normalizeName _o.target.name + " {\n"
            _t_t = maxToHoudiniGetTransforms _o.target _prerotate:false
            _t_p_x = for i in _t_t collect ( #( i[1], i[2].position.x / 100. ) )
            _t_p_y = for i in _t_t collect ( #( i[1], i[2].position.y / 100. ) )
            _t_p_z = for i in _t_t collect ( #( i[1], i[2].position.z / 100. ) )

            _t_r_x = for i in _t_t collect ( #( i[1], ( i[2].rotation as eulerangles ).x ) )
            _t_r_y = for i in _t_t collect ( #( i[1], ( i[2].rotation as eulerangles ).y ) )
            _t_r_z = for i in _t_t collect ( #( i[1], ( i[2].rotation as eulerangles ).z ) )

            _t_s_x = for i in _t_t collect ( #( i[1], i[2].scale.x ) )
            _t_s_y = for i in _t_t collect ( #( i[1], i[2].scale.y ) )
            _t_s_z = for i in _t_t collect ( #( i[1], i[2].scale.z ) )

            _str += "  tx=" + formatTuple _t_p_x  + ";\n"
            _str += "  ty=" + formatTuple _t_p_y  + ";\n"
            _str += "  tz=" + formatTuple _t_p_z  + ";\n"

            _str += "  rx=" + formatTuple _t_r_x  + ";\n"
            _str += "  ry=" + formatTuple _t_r_y  + ";\n"
            _str += "  rz=" + formatTuple _t_r_z  + ";\n"

            _str += "  sx=" + formatTuple _t_s_x  + ";\n"
            _str += "  sy=" + formatTuple _t_s_y  + ";\n"
            _str += "  sz=" + formatTuple _t_s_z  + ";\n"
            _str += "}\n\n"
        )




        _t = maxToHoudiniGetTransforms _o _prerotate:true

        _p_x = for i in _t collect ( #( i[1], i[2].position.x / 100. ) )
        _p_y = for i in _t collect ( #( i[1], i[2].position.y / 100. ) )
        _p_z = for i in _t collect ( #( i[1], i[2].position.z / 100. ) )

        _r_x = for i in _t collect ( #( i[1], ( i[2].rotation as eulerangles ).x ) )
        _r_y = for i in _t collect ( #( i[1], ( i[2].rotation as eulerangles ).y ) )
        _r_z = for i in _t collect ( #( i[1], ( i[2].rotation as eulerangles ).z ) )

        _s_x = for i in _t collect ( #( i[1], i[2].scale.x ) )
        _s_y = for i in _t collect ( #( i[1], i[2].scale.y ) )
        _s_z = for i in _t collect ( #( i[1], i[2].scale.z ) )


        _str += "Camera " + normalizeName  _o.name + " {\n"

        --position
        _str += "  tx=" + formatTuple _p_x + ";\n"
        _str += "  ty=" + formatTuple _p_y + ";\n"
        _str += "  tz=" + formatTuple _p_z + ";\n"

        --rotation
        if _o.target == undefined then (
            _str += "  rx=" + formatTuple _r_x + ";\n"
            _str += "  ry=" + formatTuple _r_y + ";\n"
            _str += "  rz=" + formatTuple _r_z + ";\n"
        )else (
            --only roll angle
            _roll = getPropertyValues _o.controller "roll_angle"
            _str += "  rz=" + formatTuple _roll + ";\n"
        )

        --scale
        _str += "  sx=" + formatTuple _s_x + ";\n"
        _str += "  sy=" + formatTuple _s_y + ";\n"
        _str += "  sz=" + formatTuple _s_z + ";\n"

        --parameters
        _fov = getPropertyValues _o "fov"
        _lens = for i in _fov collect ( #( i[1], 0.5 * ( GetRendApertureWidth() / tan( i[2]/2.0 ) ) ) )

        _str += "  focal=" + formatTuple _lens + ";\n"

        _str += "  projection=" + ( if _o.orthoProjection then 1 else 0 ) as string + ";\n"

        _str += "  aperture=" + (getRendApertureWidth()) as string + ";\n"
        _str += "  resx=" + renderWidth as string + ";\n"
        _str += "  resy=" + renderHeight as string + ";\n"
        _str += "  aspect=" + renderPixelAspect as string + ";\n"

        if _o.clipManually do (
            _str += "  near=" + formatTuple( getPropertyValues _o "nearclip" _scale:0.01 ) + ";\n"
            _str += "  far=" + formatTuple( getPropertyValues _o "farclip" _scale:0.01 ) + ";\n"
        )

        if _o.targetDistance.controller != undefined do
            _str += "  focus=" + formatTuple( getPropertyValues _o "targetDistance" _scale:0.01 ) + ";\n"

        --if target
        if _o.target != undefined do
            _str += "  target=" + normalizeName _o.target.name + ";\n"

        _str += "}\n\n"
    )
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


fn writeVRScenefiles = (

    _vrscenefile = sysinfo.tempdir + getFilenameFile maxfilename

    _script = "#scene_export\n\n"

    vrayExportRTScene ( _vrscenefile + ".vrscene" ) exportCompressed:false exportHEXFormatMesh:false exportHEXFormatTransf:false separateFiles:true exportView:false exportLights:false exportGeometry:false exportNodes:true exportMaterials:true exportTextures:true exportBitmaps:true prefix:"" stripPaths:false

    _script += "filename," + _vrscenefile + ".vrscene" + "\n"


    setclipboardText _script

    renderSceneDialog.commit()

    appendLineToFile ( _vrscenefile + ".vrscene" ) "#include \"%\"\n" (_vrscenefile + "_cameras.vrscene")
    appendLineToFile ( _vrscenefile + ".vrscene" ) "#include \"%\"\n" (_vrscenefile + "_geometries.vrscene")
    appendLineToFile ( _vrscenefile + ".vrscene" ) "#include \"%\"\n" (_vrscenefile + "_settings.vrscene")

    writeToFile ( _vrscenefile + "_settings.vrscene" ) (exportCustomSettings())
    writeToFile ( _vrscenefile + "_geometries.vrscene" ) (exportGeometries())
    writeToFile ( _vrscenefile + "_cameras.vrscene" ) (exportCameras())

    print "scene successfully exported"
)

writeVRScenefiles()
