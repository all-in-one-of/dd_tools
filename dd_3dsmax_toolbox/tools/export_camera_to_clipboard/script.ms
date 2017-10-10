fn upperfirst _s = ((toUpper _s[1]) + (substring _s 2 _s.count))

fn maxtohoudinicameratransform _t =  ( preRotateX ( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] ) -90 ) * _t * inverse( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] )

fn maxtohoudinitransform _t = ( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] ) * _t * inverse( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] )

fn maxtohoudinigetcameratransforms _o _step:1 _substeps:1 =
(
    _result = #()
    for _t = animationrange.start.frame to animationrange.end.frame by _step / _substeps do
    (
        append _result #( _t, ( maxtohoudinicameratransform ( at time _t _o.transform ) ) )
    )
    _result
)

fn maxtohoudinigettransforms _o _step:1 _substeps:1 =
(
    _result = #()
    for _t = animationrange.start.frame to animationrange.end.frame by _step / _substeps do
    (
        append _result #( _t, ( maxtohoudinitransform ( at time _t _o.transform ) ) )
    )
    _result
)

fn getpropertyvalues _o _name _step:1 _substeps:1 _scale:1 =
(
    _controller = getPropertyController _o _name
    _property = getProperty _o _name

    _result = #()
    if isController _controller then (
        for _t = animationrange.start.frame to animationrange.end.frame by _step / _substeps do (
            append _result #( _t, ( at time _t _controller.value  ) * _scale )
        )
    )
    else (
        append _result #( 0, _property * _scale )
    )
    _result
)

fn isAnimatedTuple _tuple =
(
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

fn formatTuple _tuple =
(
    _result = ""
    if ( isAnimatedTuple _tuple ) then (
        _result = "("
        for i in _tuple do _result += trimLeft( i as string ) "#" + ","
        _result = trimRight _result ","
        _result += ")"
    )else (
        _result = _tuple[1][2] as string
    )
    _result
)

fn exportcameratoclipboard _o =
(
    _t = maxtohoudinigetcameratransforms _o

    _p_x = for i in _t collect ( #( i[1], i[2].position.x / 100. ) )
    _p_y = for i in _t collect ( #( i[1], i[2].position.y / 100. ) )
    _p_z = for i in _t collect ( #( i[1], i[2].position.z / 100. ) )

    _r_x = for i in _t collect ( #( i[1], ( i[2].rotation as eulerangles ).x ) )
    _r_y = for i in _t collect ( #( i[1], ( i[2].rotation as eulerangles ).y ) )
    _r_z = for i in _t collect ( #( i[1], ( i[2].rotation as eulerangles ).z ) )

    _s_x = for i in _t collect ( #( i[1], i[2].scale.x ) )
    _s_y = for i in _t collect ( #( i[1], i[2].scale.y ) )
    _s_z = for i in _t collect ( #( i[1], i[2].scale.z ) )

    _script = "#camera_export," + ( framerate as float ) as string + ",[" + ( animationrange.start.frame as integer ) as string + ", " + ( animationrange.end.frame as integer ) as string + "]\n\n"

    --name
    _script += "name,'" + _o.name + "'\n"

    --type
    --_script += "type,'" + substituteString (toLower((classOf _o) as string)) "camera" "" + "'\n"

    --if target
    if _o.target != undefined do
    (
        _t_t = maxtohoudinigettransforms _o.target
        _t_p_x = for i in _t_t collect ( #( i[1], i[2].position.x / 100. ) )
        _t_p_y = for i in _t_t collect ( #( i[1], i[2].position.y / 100. ) )
        _t_p_z = for i in _t_t collect ( #( i[1], i[2].position.z / 100. ) )

        _t_r_x = for i in _t_t collect ( #( i[1], ( i[2].rotation as eulerangles ).x ) )
        _t_r_y = for i in _t_t collect ( #( i[1], ( i[2].rotation as eulerangles ).y ) )
        _t_r_z = for i in _t_t collect ( #( i[1], ( i[2].rotation as eulerangles ).z ) )

        _t_s_x = for i in _t_t collect ( #( i[1], i[2].scale.x ) )
        _t_s_y = for i in _t_t collect ( #( i[1], i[2].scale.y ) )
        _t_s_z = for i in _t_t collect ( #( i[1], i[2].scale.z ) )

        _script += "target_tx," + formatTuple _t_p_x  + "\n"
        _script += "target_ty," + formatTuple _t_p_y  + "\n"
        _script += "target_tz," + formatTuple _t_p_z  + "\n"

        _script += "target_rx," + formatTuple _t_r_x  + "\n"
        _script += "target_ry," + formatTuple _t_r_y  + "\n"
        _script += "target_rz," + formatTuple _t_r_z  + "\n"

        _script += "target_sx," + formatTuple _t_s_x  + "\n"
        _script += "target_sy," + formatTuple _t_s_y  + "\n"
        _script += "target_sz," + formatTuple _t_s_z  + "\n"
    )

    --position
    _script += "tx," + formatTuple _p_x + "\n"
    _script += "ty," + formatTuple _p_y + "\n"
    _script += "tz," + formatTuple _p_z + "\n"

    --rotation
    if _o.target == undefined then (
        _script += "rx," + formatTuple _r_x + "\n"
        _script += "ry," + formatTuple _r_y + "\n"
        _script += "rz," + formatTuple _r_z + "\n"
    )else (
        --only roll angle
        _roll = getpropertyvalues _o.controller "roll_angle"
        _script += "rz," + formatTuple _roll + "\n"
    )

    --scale
    _script += "sx," + formatTuple _s_x + "\n"
    _script += "sy," + formatTuple _s_y + "\n"
    _script += "sz," + formatTuple _s_z + "\n"

    --parameters
    _fov = getpropertyvalues _o "fov"
    _lens = for i in _fov collect ( #( i[1], 0.5 * ( GetRendApertureWidth() / tan( i[2]/2.0 ) ) ) )

    _script += "focal," + formatTuple _lens + "\n"

    _script += "projection," + ( if _o.orthoProjection then 1 else 0 ) as string + "\n"

    _script += "aperture," + (getRendApertureWidth()) as string + "\n"
    _script += "resx," + renderWidth as string + "\n"
    _script += "resy," + renderHeight as string + "\n"
    _script += "aspect," + renderPixelAspect as string + "\n"

    if _o.clipManually do (
        _script += "near," + formatTuple( getpropertyvalues _o "nearclip" _scale:0.01 ) + "\n" --_o.nearrange
        _script += "far," + formatTuple( getpropertyvalues _o "farclip" _scale:0.01 ) + "\n" --_o.farrange
    )

    if _o.targetDistance.controller != undefined do
        _script += "focus," + formatTuple( getpropertyvalues _o "targetDistance" _scale:0.01 ) + "\n"

    setclipboardText _script
    print( "Camera successfully exported to clipboard" )
)

if selection.count > 0 then
(
    _o = selection[1]

    if classOf _o == Targetobject do
        _o = (for _c in cameras where _c.target == _o collect _c)[1]

    if superClassOf _o == camera then
    (
        if (classOf _o == Freecamera) or (classOf _o == Targetcamera) then
        (
            exportcameratoclipboard _o

        )else ( messageBox "This kind of camera is not currently suported!" )
    )else ( messageBox "Selection is not a camera!" )
)else ( messageBox "Nothing to export!" )
