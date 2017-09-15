fn upperfirst s = ((toUpper s[1]) + (substring s 2 s.count))
fn roundfloat v = ( v as string ) as float --( ( v as string ) as integer64 ) as float
fn maxtohoudinicameratransform t =  ( preRotateX ( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] ) -90 ) * t * inverse( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] )
fn maxtohoudinitransform t = ( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] ) * t * inverse( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] )

if selection.count > 0 then
(
	o = selection[1]
	
	if classof o == Targetobject do
		o = (for c in cameras where c.target == o collect c)[1]
	
	if superclassof o == camera then
	(		
		if (classof o == Freecamera) or (classof o == Targetcamera) then
		(
			fname = getSaveFileName caption:"Output filemame" filename:(tolower((classOf o) as string) + "_" + tolower(o.name) + "_export") types:".parm|*.parm" historyCategory:".parm"
			if fname != undefined do
			(
				t = maxtohoudinicameratransform o.transform				
				r = t.rotation as eulerangles
				p = t.position
				s = t.scale
				script = ""
				
				--name
				script += "#name,'" + tolower(o.name) + "'\n"
				
				--type
				script += "#type,'" + substituteString (tolower((classof o) as string)) "camera" "" + "'\n"
				
				--if target
				if classof o == Targetcamera do (
					t_t = maxtohoudinitransform o.target.transform	
					t_p = t_t.position
					script += "#targtx," + ( t_p.x / 100. ) as string + "\n"
					script += "#targty," + ( t_p.y / 100. ) as string + "\n"
					script += "#targtz," + ( t_p.z / 100. ) as string + "\n"
				)
				
				--position
				script += "#tx," + ( p.x / 100. ) as string + "\n"
				script += "#ty," + ( p.y / 100. ) as string + "\n"
				script += "#tz," + ( p.z / 100. ) as string + "\n"
				
				--rotation
				if classof o != Targetcamera then (
					script += "#rx," + roundfloat( r.x ) as string + "\n"
					script += "#ry," + roundfloat( r.y ) as string + "\n"
					script += "#rz," + roundfloat( r.z ) as string + "\n"
				)else (
					--o.type = #free
					script += "#rz," + roundfloat( r.z ) as string + "\n"
					--o.type = #target
				)
				
				--scale
				script += "#sx," + roundfloat( s.x ) as string + "\n"
				script += "#sy," + roundfloat( s.y ) as string + "\n"
				script += "#sz," + roundfloat( s.z ) as string + "\n"
				
				script += "\n"					
								
				--parameters
				lens = 0.5 * (GetRendApertureWidth() / tan(o.fov/2.0))
				script += "focal," + lens as string + "\n"
				
				fn getProjection = if o.orthoProjection then return 1 else return 0
				script += "projection," + (getProjection()) as string + "\n"
				
				script += "aperture," + (getRendApertureWidth()) as string + "\n"
				script += "resx," + renderWidth as string + "\n"
				script += "resy," + renderHeight as string + "\n"
				script += "aspect," + renderPixelAspect as string + "\n" 
				
				if o.clipManually do (				
					script += "near," + o.nearrange as string + "\n"
					script += "far," + o.farrange as string + "\n"
				)
								
				script += "focus," + o.target_distance as string + "\n"
				
				fs = createFile fname
				format "%" script to:fs
				flush fs
				close fs		
				free fs
			)
		)
		
	)else (messagebox "Selection is not a camera!")
)else (messagebox "Nothing to export!")