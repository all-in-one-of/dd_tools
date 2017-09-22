fn maxtohoudinitransform _t = ( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] ) * _t * inverse( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] )
fn roundfloat _v = ( _v as string ) as float


fn maxtohoudinigettransforms _o _step:1 _substeps:1 =
(
    _result = #()
    for _t = animationrange.start.frame to animationrange.end.frame by _step / _substeps do
    (
        append _result #( _t, ( maxtohoudinitransform ( at time _t _o.transform ) ) )
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

fn transformtoclipboard _o =
(
	_t = maxtohoudinigettransforms _o

    _p_x = for i in _t collect ( #( i[1], i[2].position.x / 100. ) )
    _p_y = for i in _t collect ( #( i[1], i[2].position.y / 100. ) )
    _p_z = for i in _t collect ( #( i[1], i[2].position.z / 100. ) )

    _r_x = for i in _t collect ( #( i[1], ( i[2].rotation as eulerangles ).x ) )
    _r_y = for i in _t collect ( #( i[1], ( i[2].rotation as eulerangles ).y ) )
    _r_z = for i in _t collect ( #( i[1], ( i[2].rotation as eulerangles ).z ) )

    _s_x = for i in _t collect ( #( i[1], i[2].scale.x ) )
    _s_y = for i in _t collect ( #( i[1], i[2].scale.y ) )
    _s_z = for i in _t collect ( #( i[1], i[2].scale.z ) )

	_script = "#copytransform," + ( framerate as float ) as string + ",[" + ( animationrange.start.frame as integer ) as string + ", " + ( animationrange.end.frame as integer ) as string + "]\n\n"

	--position
    _script += "tx," + formatTuple _p_x + "\n"
    _script += "ty," + formatTuple _p_y + "\n"
    _script += "tz," + formatTuple _p_z + "\n"

    --rotation
    _script += "rx," + formatTuple _r_x + "\n"
    _script += "ry," + formatTuple _r_y + "\n"
    _script += "rz," + formatTuple _r_z + "\n"

    --scale
    _script += "sx," + formatTuple _s_x + "\n"
    _script += "sy," + formatTuple _s_y + "\n"
    _script += "sz," + formatTuple _s_z + "\n"

	setclipboardText _script
	print( "Object transform successfully exported to clipboard" )
)


if selection.count == 1 then
	transformtoclipboard selection[1]
else
    if selection.count == 0 then
        messageBox("Nothing to export")
    else
        messageBox("More then one object selected")
