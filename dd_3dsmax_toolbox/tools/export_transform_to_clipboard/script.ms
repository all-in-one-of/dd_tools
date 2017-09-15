fn maxtohoudinitransform _t = ( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] ) * _t * inverse( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] )
fn roundfloat _v = ( _v as string ) as float

fn transformtoclipboard o =
(
	_t = maxtohoudinitransform o.transform
	_r = _t.rotation as eulerangles
	_p = _t.position
	_s = _t.scale
	script = ""
	--position
	script += "tx," + ( _p.x / 100. ) as string + "\n"
	script += "ty," + ( _p.y  / 100. ) as string + "\n"
	script += "tz," + ( _p.z  / 100. ) as string + "\n"

	--rotation
	script += "rx," + roundfloat( _r.x ) as string + "\n"
	script += "ry," + roundfloat( _r.y ) as string + "\n"
	script += "rz," + roundfloat( _r.z ) as string + "\n"

	--rotation
	script += "sx," + roundfloat( _s.x ) as string + "\n"
	script += "sy," + roundfloat( _s.y ) as string + "\n"
	script += "sz," + roundfloat( _s.z ) as string + "\n"

	setclipboardText script
	print( "Object transform successfully exported to clipboard" )
)


if selection.count == 1 then
	transformtoclipboard $
else
    if selection.count == 0 then
        messageBox("Nothing to export")
    else
        messageBox("More then one object selected")
