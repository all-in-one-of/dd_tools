fn upperfirst _s = ((toUpper _s[1]) + (substring _s 2 _s.count))
--fn roundfloat v = ( v as string ) as float --( ( v as string ) as integer64 ) as float
fn maxtohoudinicameratransform _t =  ( preRotateX ( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] ) -90 ) * _t * inverse( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] )
fn maxtohoudinitransform _t = ( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] ) * _t * inverse( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] )


if selection.count > 0 then
(
	_o = selection[1]
	
	if classOf _o == Targetobject do
		_o = (for _c in cameras where _c.target == _o collect _c)[1]
	
	if superClassOf _o == camera then
	(		
		if (classOf _o == Freecamera) or (classOf _o == Targetcamera) then
		(
            _t = maxtohoudinicameratransform _o.transform
            _r = _t.rotation as eulerangles
            _p = _t.position / 100.
            _s = _t.scale

            _script = "#camera_export\n\n"
            
            --name
            _script += "#name,'" + toLower(_o.name) + "'\n"
            
            --type
            _script += "#type,'" + substituteString (toLower((classOf _o) as string)) "camera" "" + "'\n"
            
            --if target
            if classOf _o == Targetcamera do
            (
                _t_t = maxtohoudinitransform _o.target.transform
                _t_p = _t_t.position / 100.

                _script += "#targtx," + _t_p.x as string + "\n"
                _script += "#targty," + _t_p.y as string + "\n"
                _script += "#targtz," + _t_p.z as string + "\n"
            )
            
            --position
            _script += "#tx," + _p.x as string + "\n"
            _script += "#ty," + _p.y as string + "\n"
            _script += "#tz," + _p.z as string + "\n"
            
            --rotation
            if classof _o != Targetcamera then (
                _script += "#rx," + _r.x as string + "\n"
                _script += "#ry," + _r.y as string + "\n"
                _script += "#rz," + _r.z as string + "\n"
            )else (
                --only roll angle
                _script += "#rz," + _r.z as string + "\n"
            )
            
            --scale
            _script += "#sx," + _s.x as string + "\n"
            _script += "#sy," + _s.y as string + "\n"
            _script += "#sz," + _s.z as string + "\n\n"
                            
            --parameters
            _lens = 0.5 * (GetRendApertureWidth() / tan(_o.fov/2.0))
            _script += "focal," + _lens as string + "\n"
            
            fn getProjection = if _o.orthoProjection then return 1 else return 0
            _script += "projection," + (getProjection()) as string + "\n"
            
            _script += "aperture," + (getRendApertureWidth()) as string + "\n"
            _script += "resx," + renderWidth as string + "\n"
            _script += "resy," + renderHeight as string + "\n"
            _script += "aspect," + renderPixelAspect as string + "\n" 
            
            if _o.clipManually do (				
                _script += "near," + _o.nearrange as string + "\n"
                _script += "far," + _o.farrange as string + "\n"
            )
                            
            _script += "focus," + _o.target_distance as string + "\n"
            
            setclipboardText _script
            print( "Camera successfully exported to clipboard" )
		)
		
	)else ( messageBox "Selection is not a camera!" )
)else ( messageBox "Nothing to export!" )