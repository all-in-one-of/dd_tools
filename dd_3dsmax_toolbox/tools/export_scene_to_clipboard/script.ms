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
    re = dotnetObject "System.Text.RegularExpressions.Regex" "[^a-zA-Z0-9@]"
    re.Replace _name "_"
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
        for i in _tuple do _result += "(" + floatToString i[1] + "," + floatToString i[2] + "),"
        _result = trimRight ( trimRight _result " " ) ","
        _result += ")"
    )else (
        --_result = _tuple[1][2] as string
        _result = floatToString _tuple[1][2]
    )
    _result
)


fn formatBoolean _bool = (

    if _bool == false or _bool == 0 then return "False" else return "True"
)


fn formatColor _color = (

    "Color(" + floatToString( _color.r / 255. ) + "," + floatToString( _color.g / 255. ) + "," + floatToString( _color.b / 255. ) + ")"
)


fn formatAColor _acolor = (

    "AColor(" + floatToString( _acolor.r / 255. ) + "," + floatToString( _acolor.g / 255. ) + "," + floatToString( _acolor.b / 255. ) + "," + floatToString( _acolor.a / 255. ) + ")"
)


fn getValidGeometries = (
    _result = for _o in geometry where _o.isHidden == false and _o.renderable == true collect _o
	_result = for i = _result.count to 1 by -1 collect _result[i] --reverse array
    for _o in _result do (
        _instances = #()
        _count = InstanceMgr.GetInstances _o &_instances
		_instances = for i = _instances.count to 1 by -1 collect _instances[i] --reverse array
        while _count > 1 do (
            for i = _result.count to 1 by -1 do (
                if _result[i] == _instances[_count] do (
                    deleteItem _result i
                    _count -= 1
                )
            )
        )
    )
    _result
)


fn exportGeometries _dir _step:1 _substeps:1 = (
    _str = ""
    _validGeometries = getValidGeometries()
    for _o in _validGeometries do (
        _animated = ( _o.isAnimated or isDeformable _o )
        _name = normalizeName _o.name
        _abcfile = _dir + _name + ".abc"
        _frange = [0,100]
        _opath = getHierarchy _o
        if _animated == false then _frange = [currenttime.frame, currenttime.frame] else _frange = [animationrange.start.frame, animationrange.end.frame]

        --do a copy reset transforms
        _copy = instance _o
        _copy.name = _name + "_mesh"
        _copy.transform.controller.position.controller = Position_XYZ()
        _copy.transform.controller.rotation.controller = Euler_XYZ()
        _copy.transform.controller.scale.controller = bezier_scale()
        _copy.transform = matrix3 1
        _o = _copy

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
            --_job += ";transformCache=true"
            _job += ";transformCache=false" --TEST
            _job += ";storageFormat=hdf5"

            _result = ExocortexAlembic.createExportJobs( _job )

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

            _instances = #()
            _count = InstanceMgr.GetInstances _o &_instances
            if _count > 1 do (
                _instances = for i = _instances.count to 1 by -1 where _instances[i] != _o collect _instances[i] --reverse array and exlude _o
		    )

            for _o in _instances do (

                if classOf _o != HairObject and classOf _o != GuidesObject then
                    _str += "AlembicGeometry " +  normalizeName _o.name + " {\n"
                else
                    _str += "OxAlembicExport " + normalizeName _o.name + " {\n"

                -- object transforms here...
                _t_t = maxToHoudiniGetTransforms _o _prerotate:false
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


                _str += "  filename=\"" + _abcfile + "\";\n"
                _str += "  object_id=" + _o.gbufferChannel  as string + ";\n"
                _str += "  wirecolor=Color(" + ( _o.wirecolor.r / 255. ) as string + "," + ( _o.wirecolor.g/ 255. ) as string + "," + ( _o.wirecolor.b / 255. ) as string + ");\n"
                _str += "  handle=" + _o.inode.handle as string + ";\n"
                --user properties here...
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

            --delete the copy
            delete _o
        )
    )
    clearListener()
	_str
)


fn exportCameras _step:1 _substeps:1 = (
    _str = ""
    for _o in cameras where classOf _o != Targetobject and ( classOf _o == Freecamera or classOf _o == Targetcamera ) do (

        --if target
        if _o.target != undefined do (
            _str += "TargetObject " + normalizeName _o.target.name + " {\n"
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
        --_str += "  sx=" + formatTuple _s_x + ";\n"
        --_str += "  sy=" + formatTuple _s_y + ";\n"
        --_str += "  sz=" + formatTuple _s_z + ";\n"

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
            _str += "  target=\"" + normalizeName _o.target.name + "\";\n"

        _str += "}\n\n"
    )
    _str
)


fn exportLights _step:1 _substeps:1 = (

    _str = ""
    for _o in lights where classOf _o != Targetobject and ( classOf _o == VRayLight or classOf _o == VRaySun or classOf _o == VRayAmbientLight or classOf _o == VRayIES ) do (

        --if target
        if _o.target != undefined do (
            _str += "TargetObject " + normalizeName _o.target.name + " {\n"
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

        --type
        _type = ""
        if classOf _o == VRayLight then (
            case _o.type of (
                0 : _type = "LightRectangle"
                1 : _type = "LightDome"
                2 : _type = "LightSphere"
                3 : _type = "LightMesh"
                4 : _type = "LightRectangle"
            )
        )else if classOf _o == VRaySun then (
            _type = "SunLight"
        )else if classOf _o == VRayAmbientLight then (
            _type = "LightAmbient"
        )else if classOf _o == VRayIES then (
            _type = "LightIES"
        )

        _str += _type + " " + normalizeName  _o.name + " {\n"


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
            _roll = getpropertyvalues _o.controller "roll_angle"
            _str += "  rz=" + formatTuple _roll + ";\n"
        )

        --scale
        --_str += "  sx=" + formatTuple _s_x + ";\n"
        --_str += "  sy=" + formatTuple _s_y + ";\n"
        --_str += "  sz=" + formatTuple _s_z + ";\n"

        --parameters
        if classOf _o == VRayLight then
        (
            fn get_lightPortal _o = if _o.skylightPortal == false then lightPortal = 0 else ( if _o.simplePortal == false then lightPortal = 1 else lightPortal = 2 )

            --specific parameters
            case _o.type of
            (
                0 : (
                    --Plane
                    _str += "  is_disc=False;\n"
                    _str += "  u_size=" + ( _o.size0 * 2 / 100. ) as string + ";\n"
                    _str += "  v_size=" + ( _o.size1 * 2 / 100. ) as string + ";\n"
                    _str += "  directional=" + _o.lightDistribution as string + ";\n"
                    _str += "  ignoreLightNormals=" + formatBoolean( _o.ignoreNormals ) + ";\n"
                    _str += "  doubleSided=" + formatBoolean( _o.doubleSided ) + ";\n"
                    _str += "  lightPortal=" + (get_lightPortal _o) as string + ";\n"
                    _str += "  noDecay=" + formatBoolean( _o.noDecay ) + ";\n"
                )
                1 : (
                    --Dome
                    _str += "  tex_resolution=" + _o.texmap_resolution as string + ";\n"
                    _str += "  tex_adaptive=" + _o.texmap_adaptiveness as string + ";\n"
                    _str += "  dome_spherical=" + formatBoolean( _o.dome_spherical ) + ";\n"
                    _str += "  affect_alpha=" + formatBoolean( _o.dome_affect_alpha ) + ";\n"
                    --texmap_locktodome pas d'equivalent sous houdini
                    _str += "  dome_rayDistanceMode=" + _o.dome_rayDistanceMode as string + ";\n"
                    _str += "  dome_rayDistance=" + _o.dome_rayDistance as string + ";\n"
                    _str += "  dome_targetRadius=" + ( _o.dome_targetRadius / 100. ) as string + ";\n"
                    _str += "  dome_emitRadius=" + ( _o.dome_emitRadius / 100. ) as string  + ";\n"
                )
                2 : (
                    --Sphere
                    _str += "  radius=" + ( _o.size0 / 100.) as string + ";\n"
                    _str += "  noDecay=" + formatBoolean( _o.noDecay ) + ";\n"
                )
                3 : (
                    --Mesh
                    --flip normals a faire
                    --pick mesh a faire
                    _str += "  ignoreLightNormals=" + formatBoolean( _o.ignoreNormals ) + ";\n"
                    _str += "  doubleSided=" + formatBoolean( _o.doubleSided ) + ";\n"
                    _str += "  lightPortal=" + (get_lightPortal _o) as string + ";\n"
                    _str += "  noDecay=" + formatBoolean( _o.noDecay ) + ";\n"
                )
                4 : (
                    --Disc
                    _str += "  is_disc=True;\n"
                    _str += "  u_size=" + (_o.size0 / 100.) as string + ";\n"
                    _str += "  v_size=" + (_o.size1 / 100.) as string + ";\n"
                    _str += "  directional=" + _o.lightDistribution as string + ";\n"
                    _str += "  ignoreLightNormals=" + _o.ignoreNormals as string + ";\n"
                    _str += "  doubleSided=" + formatBoolean( _o.doubleSided ) + ";\n"
                    _str += "  lightPortal=" + (get_lightPortal _o) as string + ";\n"
                    _str += "  noDecay=" + formatBoolean( _o.noDecay ) + ";\n"
                )
            )

            --common parameters
            _str += "  enabled=" + formatBoolean( _o.on ) + ";\n"

            _str += "  units=" + _o.normalizeColor as string + ";\n"

            _str += "  intensity=" + _o.multiplier as string + ";\n"
            _str += "  color=" + formatColor( _o.color ) + ";\n"
            _str += "  map_color=" + formatBoolean( _o.texmap_on ) + ";\n"

            --options parameters
            --exclude a faire
            _str += "  shadows=" + formatBoolean( _o.castShadows ) + ";\n"
            _str += "  invisible=" + formatBoolean( _o.invisible ) + ";\n"
            _str += "  storeWithIrradianceMap=" + formatBoolean( _o.storeWithIrradMap ) + ";\n"
            _str += "  affectDiffuse=" + formatBoolean( _o.affect_diffuse ) + ";\n"
            _str += "  affectSpecular=" + formatBoolean( _o.affect_specular ) + ";\n"
            _str += "  affectReflections=" + formatBoolean( _o.affect_reflections ) + ";\n"
            _str += "  diffuse_contribution=" + _o.diffuse_contribution as string + ";\n"
            _str += "  specular_contribution=" + _o.specular_contribution as string + ";\n"

            --sampling
            _str += "  subdivs=" + _o.subdivs as string + ";\n"
            _str += "  shadowBias=" + _o.ShadowBias as string + ";\n"
            _str += "  cutoffThreshold=" + _o.cutoffThreshold as string + ";\n"

            --viewport
            --rien a exporter ici

            --advanced options
            _str += "  objectID=" + _o.gbufferchannel as string + ";\n"

            --VRay userProps
            diffuseMult = getUserProp _o "VRay_Diffuse_Multipier"
            if diffuseMult != undefined do _str += "  diffuseMult=" + diffuseMult as string + ";\n"
            causticMult = getUserProp _o "VRay_Caustics_Multipier"
            if causticMult != undefined do _str += "  causticMult=" + causticMult as string + ";\n"
            photonSubdivs = getUserProp _o "VRay_Diffuse_Subdivs"
            if photonSubdivs != undefined do _str += "  photonSubdivs=" + photonSubdivs as string + ";\n"
            causticSubdivs = getUserProp _o "VRay_Caustics_Subdivs"
            if causticSubdivs != undefined do _str += "  causticSubdivs=" + causticSubdivs as string + ";\n"

        )else if classOf _o == VRaySun then
        (
            _str += "  enabled=" + formatBoolean(_o.enabled) + ";\n"
            _str += "  invisible=" + formatBoolean(_o.invisible) + ";\n"
            _str += "  affectDiffuse=" + formatBoolean(_o.affect_diffuse) + ";\n"
            _str += "  diffuse_contribution=" + _o.diffuse_contribution as string + ";\n"
            _str += "  affectSpecular=" + formatBoolean(_o.affect_specular) + ";\n"
            _str += "  specular_contribution=" + _o.specular_contribution as string + ";\n"
            _str += "  atmos_shadows=" + formatBoolean(_o.cast_atmospheric_shadows) + ";\n"
            _str += "  turbidity=" + _o.turbidity as string + ";\n"
            _str += "  ozone=" + _o.ozone as string + ";\n"
            _str += "  intensity_multiplier=" + _o.intensity_multiplier as string + ";\n"
            _str += "  size_multiplier=" + _o.size_multiplier as string + ";\n"
            _str += "  filter_color=" + formatColor( _o.filter_color ) + ";\n"
            _str += "  color_mode=" + _o.color_mode as string + ";\n"
            _str += "  shadow_subdivs=" + _o.shadow_subdivs as string + ";\n"
            _str += "  shadowBias=" + (_o.shadow_bias / 100.) as string + ";\n"
            _str += "  photon_radius=" + (_o.photon_emit_radius / 100) as string + ";\n"
            _str += "  photonSubdivs=" + 500 as string + ";\n" --pas d'equivalent dans max
            _str += "  sky_model=" + _o.sky_model as string + ";\n"
            _str += "  horiz_illum=" + _o.indirect_horiz_illum as string + ";\n"
            _str += "  ground_albedor=" + (_o.ground_albedo.r / 255.) as string + ";\n"
            _str += "  ground_albedog=" + (_o.ground_albedo.g / 255.) as string + ";\n"
            _str += "  ground_albedob=" + (_o.ground_albedo.b / 255.) as string + ";\n"
            --"" _o.blend_angle --pas d'equivalent dans houdini
            --"" _o.horizon_offset --pas d'equivalent dans houdini
            _str += "  water_vapour=" + 2 as string + ";\n" --pas d'equivalent dans max
            _str += "  shadows=" + 1 as string + ";\n" --pas d'equivalent dans max

        )else if classOf _o == VRayAmbientLight then
        (
            _str += "  enabled=" + formatBoolean(_o.enabled) + ";\n"
            _str += "  intensity=" + _o.intensity as string + ";\n"
            _str += "  color=" + formatColor( _o.color ) + ";\n"

        )else if classOf _o == VRayIES then
        (
            fn getlightshapemode _o = if _o.override_shape == true then return 1 else return 0

            -- je sais pas sis quelqu un utilise ce genre de lumiere....
            _str += "  enabled=" + formatBoolean(_o.enabled) + ";\n"
            _str += "  power=" + _o.power as string + ";\n"
            --"rescale_max_intensty," -- pas trouvé d'equivalent sous max ?
            _str += "  ies_file,'" + _o.ies_file + "'\n"
            _str += "  color=" + formatColor( _o.color ) + ";\n"

            _str += "  ies_light_shape=" + (getlightshapemode()) as string
            _str += "  ies_light_height=" + _o.height as string + ";\n"
            _str += "  ies_light_length=" + _o.length as string + ";\n"
            _str += "  ies_light_width=" + _o.width as string + ";\n"
            _str += "  ies_light_diameter=" + _o.diameter as string + ";\n"
            _str += "  filter_color=" + formatColor( _o.color ) + ";\n"
            --"soft_shadows," -- pas trouvé d'equivalent sous max ?
            --"use_global_light_level," -- pas trouvé d'equivalent sous max ?
            --"shadow_subdivs=" + _o.shadow_subdivs as string + ";\n" -- pas trouvé d'equivalent sous max ?
            _str += "  shadowBias=" + _o.shadow_bias as string + ";\n"
            _str += "  affectDiffuse=" + formatBoolean(_o.affect_diffuse) + ";\n"
            _str += "  diffuse_contribution=" + _o.diffuse_contribution as string + ";\n"
            _str += "  affectSpecular=" + formatBoolean(_o.affect_specular) + ";\n"
            _str += "  specular_contribution=" + _o.specular_contribution as string + ";\n"
        )

        --if target
        if _o.target != undefined do
            _str += "  target=\"" + normalizeName _o.target.name + "\";\n"

        _str += "}\n\n"
    )
    _str
)


fn exportCustomSettings = (
    _name = normalizeName( getFilenameFile maxfilename )
    _cam = if getActiveCamera() != undefined then normalizeName( (getActiveCamera()).name ) else ""
    _fps = (framerate as float) as string
    _range = [animationrange.start.frame as integer , animationrange.end.frame as integer] as string
    _frame = (currenttime.frame as float) as string

    _str = "CustomSettings scene_settings {\n  name=\"" + _name + "\";\n  camera=\"" + _cam + "\";\n  fps=" + _fps + ";\n  range=" + _range + ";\n  frame=" + _frame + ";\n}\n"

    try(
        _aa_filter = if renderers.current.filter_on == false then 0 else filter_kernel_convert renderers.current.filter_kernel as string
        _str += "\nSettingsImageSampler aa_filter {\n  filter_type=" + _aa_filter + ";\n}\n"
    )catch()

    _str
)


fn exportScene = (

    _dir = sysinfo.tempdir + "houdini_export_temp\\"

    makeDir _dir

    _filename = _dir + getFilenameFile maxfilename

    _script = "#scene_export\n\n"

    vrayExportRTScene ( _filename + ".vrscene" ) exportCompressed:false exportHEXFormatMesh:false exportHEXFormatTransf:false separateFiles:true exportView:false exportLights:false exportGeometry:false exportNodes:true exportMaterials:true exportTextures:true exportBitmaps:true prefix:"" stripPaths:false

    _script += "filename," + _filename + ".vrscene" + "\n"


    setclipboardText _script

    renderSceneDialog.commit()

    appendLineToFile ( _filename + ".vrscene" ) "#include \"%\"\n" (_filename + "_cameras.vrscene")
    appendLineToFile ( _filename + ".vrscene" ) "#include \"%\"\n" (_filename + "_geometries.vrscene")
    appendLineToFile ( _filename + ".vrscene" ) "#include \"%\"\n" (_filename + "_settings.vrscene")

    writeToFile ( _filename + "_settings.vrscene" ) (exportCustomSettings())
    writeToFile ( _filename + "_geometries.vrscene" ) (exportGeometries _dir)
    writeToFile ( _filename + "_cameras.vrscene" ) (exportCameras())
    writeToFile ( _filename + "_lights.vrscene" ) (exportLights())

    print "scene successfully exported"
)

exportScene()
