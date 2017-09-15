fn upperfirst s = ((toUpper s[1]) + (substring s 2 s.count))
fn roundfloat v = ( v as string ) as float --( ( v as string ) as integer64 ) as float
fn maxtohoudinitransform t = ( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] ) * t * inverse( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] )

if selection.count > 0 then
(
	o = selection[1]
	if classof o == Targetobject do
		o = (for c in lights where c.target == o collect c)[1]
	
	if superclassof o == light then
	(
		--if findstring ((classof o) as string) "VRay" != undefined then
		if classof o == VRayLight or classof o == VRaySun /*or classof o == VRayAmbientLight or classof o == VRayIES*/ then
		(
			fname = getSaveFileName caption:"Output filemame" filename:(tolower((classOf o) as string) + "_" + tolower(o.name) + "_export") types:".parm|*.parm" historyCategory:".parm"
			if fname != undefined do
			(
				t = maxtohoudinitransform o.transform				
				r = t.rotation as eulerangles
				p = t.position
				s = t.scale
				script = ""
				
				--name
				script += "#name,'" + tolower(o.name) + "'\n"
				
				--type
				if classof o == VRayLight then
				(
					case o.type of
					(
						0 : script += "#type,'VRayNodeLightRectangle'\n"						
						1 : script += "#type,'VRayNodeLightDome'\n"						
						2 : script += "#type,'VRayNodeLightSphere'\n"
						3 : script += "#type,'VRayNodeLightMesh'\n"
						4 : script += "#type,'VRayNodeLightRectangle'\n"
					)
				)else if classof o == VRaySun then
				(
					--type
					script += "#type,'VRayNodeSunLight'\n"
				)else if classof o == VRayAmbientLight then
				(
					--type
					script += "#type,'VRayNodeLightAmbient'\n"
				)else if classof o == VRayIES then
				(
					--type
					script += "#type,'VRayNodeLightIES'\n"
				)
				
				--position
				script += "#tx," + ( p.x / 100. ) as string + "\n"
				script += "#ty," + ( p.y / 100. ) as string + "\n"
				script += "#tz," + ( p.z / 100. ) as string + "\n"
				
				--rotation
				if o.target == undefined then (
					script += "#rx," + roundfloat( r.x ) as string + "\n"
					script += "#ry," + roundfloat( r.y ) as string + "\n"
					script += "#rz," + roundfloat( r.z ) as string + "\n"
				)else (
					script += "#rz," + roundfloat( r.z ) as string + "\n"
				)
				
				--scale
				script += "#sx," + roundfloat( s.x ) as string + "\n"
				script += "#sy," + roundfloat( s.y ) as string + "\n"
				script += "#sz," + roundfloat( s.z ) as string + "\n"
				
				--target
				if o.target != undefined do
				(
					t_t = maxtohoudinitransform o.target.transform	
					t_p = t_t.position
					script += "#targtx," + ( t_p.x / 100. ) as string + "\n"
					script += "#targty," + ( t_p.y / 100. ) as string + "\n"
					script += "#targtz," + ( t_p.z / 100. ) as string + "\n"
				)
				
				script += "\n"
				
				if classof o == VRayLight then
				(
					fn get_lightPortal = if o.skylightPortal == false then lightPortal = 0 else ( if o.simplePortal == false then lightPortal = 1 else lightPortal = 2 )						
					
					--specific parameters
					case o.type of
					(
						0 : (
							--Plane
							script += "is_disc,False\n"
							script += "u_size," + ( o.size0 / 100.) as string + "\n"
							script += "v_size," + ( o.size1 / 100.) as string + "\n"							
							script += "directional," + o.lightDistribution as string + "\n"
							script += "ignoreLightNormals," + upperfirst( o.ignoreNormals as string ) + "\n"
							script += "doubleSided," + upperfirst( o.DoubleSided as string ) + "\n"
							script += "lightPortal," + (get_lightPortal()) as string + "\n"
						)						
						1 : (
							--Dome
							script += "tex_resolution," + o.texmap_resolution as string + "\n"
							script += "tex_adaptive," + o.texmap_adaptiveness as string + "\n"
							script += "dome_spherical," + upperfirst( o.dome_spherical as string ) + "\n"
							script += "affect_alpha," + upperfirst( o.dome_affect_alpha as string ) + "\n"
							--texmap_locktodome pas d'equivalent sous houdini
							script += "dome_rayDistanceMode," + o.dome_rayDistanceMode as string + "\n"
							script += "dome_rayDistance," + o.dome_rayDistance as string + "\n"
							script += "dome_targetRadius," + o.dome_targetRadius as string + "\n"
							script += "dome_emitRadius," + o.dome_emitRadius as string + "\n"
						)						
						2 : (
							--Sphere
							script += "radius," + ( o.size0 / 100.) as string + "\n"
						)						
						3 : (
							--Mesh
							--flip normals a faire
							--pick mesh a faire
							script += "ignoreLightNormals," + upperfirst( o.ignoreNormals as string ) + "\n"
							script += "doubleSided," + upperfirst( o.DoubleSided as string ) + "\n"
							script += "lightPortal," + (get_lightPortal()) as string + "\n"
						)						
						4 : (
							--Disc
							script += "is_disc,True\n"
							script += "u_size," + (o.size0 / 100.) as string + "\n"
							script += "v_size," + (o.size1 / 100.) as string + "\n"
							script += "directional," + o.lightDistribution as string + "\n"
							script += "ignoreLightNormals," + o.ignoreNormals as string + "\n"
							script += "doubleSided," + upperfirst( o.DoubleSided as string ) + "\n"
							script += "lightPortal," + (get_lightPortal()) as string + "\n"
						)
					)
					
					--common parameters				
					script += "enabled," + upperfirst( o.on as string ) + "\n"				
										
					script += "units," + o.normalizeColor as string + "\n"
					
					script += "intensity," + o.multiplier as string + "\n"
					script += "colorr," + (o.color.r / 255.) as string + "\n"
					script += "colorg," + (o.color.g / 255.) as string + "\n"
					script += "colorb," + (o.color.b / 255.) as string + "\n"				
					script += "map_color," + upperfirst( o.texmap_on as string ) + "\n"
					
					--options parameters
					--exclude a faire
					script += "shadows," + upperfirst( o.castShadows as string ) + "\n"					
					script += "invisible," + upperfirst( o.invisible as string ) + "\n"
					script += "noDecay," + upperfirst( o.noDecay as string ) + "\n"					
					script += "storeWithIrradianceMap," + upperfirst( o.storeWithIrradMap as string ) + "\n"
					script += "affectDiffuse," + upperfirst( o.affect_diffuse as string ) + "\n"
					script += "affectSpecular," + upperfirst( o.affect_specular as string ) + "\n"				
					script += "affectReflections," + upperfirst( o.affect_reflections as string ) + "\n"
					script += "diffuse_contribution," + o.diffuse_contribution as string + "\n"
					script += "specular_contribution," + o.specular_contribution as string + "\n"
					
					--sampling
					script += "subdivs," + o.subdivs as string + "\n"				
					script += "shadowBias," + o.ShadowBias as string + "\n"
					script += "cutoffThreshold," + o.cutoffThreshold as string + "\n"
					
					--viewport
					--rien a exporter ici
					
					--advanced options
					script += "objectID," + o.gbufferchannel as string + "\n"				
					
					--VRay userProps
					diffuseMult = getUserProp o "VRay_Diffuse_Multipier"
					if diffuseMult != undefined do script += "diffuseMult," + diffuseMult as string + "\n"
					causticMult = getUserProp o "VRay_Caustics_Multipier"
					if causticMult != undefined do script += "causticMult," + causticMult as string + "\n"
					photonSubdivs = getUserProp o "VRay_Diffuse_Subdivs"
					if photonSubdivs != undefined do script += "photonSubdivs," + photonSubdivs as string + "\n"
					causticSubdivs = getUserProp o "VRay_Caustics_Subdivs"
					if causticSubdivs != undefined do script += "causticSubdivs," + causticSubdivs as string + "\n"
					
					
				
				)else if classof o == VRaySun then
				(
					script += "enabled," + upperfirst(o.enabled as string) + "\n"
					script += "invisible," + upperfirst(o.invisible as string) + "\n"
					script += "affectDiffuse," + upperfirst(o.affect_diffuse as string) + "\n"
					script += "diffuse_contribution," + o.diffuse_contribution as string + "\n"
					script += "affectSpecular," + upperfirst(o.affect_specular as string) + "\n"
					script += "specular_contribution," + o.specular_contribution as string + "\n"
					script += "atmos_shadows," + upperfirst(o.cast_atmospheric_shadows as string) + "\n"
					script += "turbidity," + o.turbidity as string + "\n"
					script += "ozone," + o.ozone as string + "\n"
					script += "intensity_multiplier," + o.intensity_multiplier as string + "\n"
					script += "size_multiplier," + o.size_multiplier as string + "\n"
					script += "filter_colorr," + (o.filter_Color.r / 255.) as string + "\n"
					script += "filter_colorg," + (o.filter_Color.g / 255.) as string + "\n"
					script += "filter_colorb," + (o.filter_Color.b / 255.) as string + "\n"
					script += "color_mode," + o.color_mode as string + "\n"
					script += "shadow_subdivs," + o.shadow_subdivs as string + "\n"
					script += "shadowBias," + (o.shadow_bias / 100.) as string + "\n"
					script += "photon_radius," + (o.photon_emit_radius / 100) as string + "\n"
					script += "photonSubdivs," + 500 as string + "\n" --pas d'equivalent dans max
					script += "sky_model," + o.sky_model as string + "\n"
					script += "horiz_illum," + o.indirect_horiz_illum as string + "\n"
					script += "ground_albedor," + (o.ground_albedo.r / 255.) as string + "\n"
					script += "ground_albedog," + (o.ground_albedo.g / 255.) as string + "\n"
					script += "ground_albedob," + (o.ground_albedo.b / 255.) as string + "\n"
					--"" o.blend_angle --pas d'equivalent dans houdini
					--"" o.horizon_offset --pas d'equivalent dans houdini
					script += "water_vapour," + 2 as string + "\n" --pas d'equivalent dans max
					script += "shadows," + 1 as string + "\n" --pas d'equivalent dans max
				)else if classof o == VRayAmbientLight then
				(				
					script += "enabled," + upperfirst(o.enabled as string) + "\n"
					script += "intensity," + o.intensity as string + "\n"
					script += "colorr," + (o.color.r / 255.) as string + "\n"
					script += "colorg," + (o.color.g / 255.) as string + "\n"
					script += "colorb," + (o.color.b / 255.) as string + "\n"
					
				)else if classof o == VRayIES then
				(
					-- je sais pas sis quelqu un utilise ce genre de lumiere....
					script += "enabled," + upperfirst(o.enabled as string) + "\n"
					script += "power," + o.power as string + "\n"
					--script += "rescale_max_intensty," -- pas trouvé d'equivalent sous max ?
					script += "ies_file,'" + o.ies_file + "'\n"
					script += "colorr," + (o.color.r / 255.) as string + "\n"
					script += "colorg," + (o.color.g / 255.) as string + "\n"
					script += "colorb," + (o.color.b / 255.) as string + "\n"
					
					fn getlightshapemode = if o.override_shape == true then return 1 else return 0
					script += "ies_light_shape," + (getlightshapemode()) as string
					script += "ies_light_height," + o.height as string + "\n"
					script += "ies_light_length," + o.length as string + "\n"
					script += "ies_light_width," + o.width as string + "\n"
					script += "ies_light_diameter," + o.diameter as string + "\n"
					script += "filter_colorr," + (o.color.r / 255.) as string + "\n"
					script += "filter_colorg," + (o.color.g / 255.) as string + "\n"
					script += "filter_colorb," + (o.color.b / 255.) as string + "\n"
					--script += "soft_shadows," -- pas trouvé d'equivalent sous max ?
					--script += "use_global_light_level," -- pas trouvé d'equivalent sous max ?					
					--script += "shadow_subdivs," + o.shadow_subdivs as string + "\n" -- pas trouvé d'equivalent sous max ?		
					script += "shadowBias," + o.shadow_bias as string + "\n"
					script += "affectDiffuse," + upperfirst(o.affect_diffuse as string) + "\n"
					script += "diffuse_contribution," + o.diffuse_contribution as string + "\n"
					script += "affectSpecular," + upperfirst(o.affect_specular as string) + "\n"
					script += "specular_contribution," + o.specular_contribution as string + "\n"
				)
				
				fs = createFile fname
				format "%" script to:fs
				flush fs
				close fs		
				free fs
			)
		)else (messagebox "This kind of light is not supported yet!")
	)else (messagebox "Selection is not a light!")
)else (messagebox "Nothing to export!")