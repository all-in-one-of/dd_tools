fn upperfirst _s = ((toUpper _s[1]) + (substring _s 2 _s.count))

fn maxtohoudinitransform _t = ( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] ) * _t * inverse( matrix3 [1,0,0] [0,0,1] [0,-1,0] [0,0,0] )

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

fn exportlighttoclipboard _o =
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

    _script = "#light_export," + ( framerate as float ) as string + ",[" + ( animationrange.start.frame as integer ) as string + ", " + ( animationrange.end.frame as integer ) as string + "]\n\n"

    --name
    _script += "name,'" + tolower(_o.name) + "'\n"

    --type
    if classof _o == VRayLight then
    (
        case _o.type of
        (
            0 : _script += "type,'VRayNodeLightRectangle'\n"
            1 : _script += "type,'VRayNodeLightDome'\n"
            2 : _script += "type,'VRayNodeLightSphere'\n"
            3 : _script += "type,'VRayNodeLightMesh'\n"
            4 : _script += "type,'VRayNodeLightRectangle'\n"
        )
    )else if classof _o == VRaySun then
    (
        --type
        _script += "type,'VRayNodeSunLight'\n"
    )else if classof _o == VRayAmbientLight then
    (
        --type
        _script += "type,'VRayNodeLightAmbient'\n"
    )else if classof _o == VRayIES then
    (
        --type
        _script += "type,'VRayNodeLightIES'\n"
    )

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
    if classOf _o == VRayLight then
    (
        fn get_lightPortal _o = if _o.skylightPortal == false then lightPortal = 0 else ( if _o.simplePortal == false then lightPortal = 1 else lightPortal = 2 )

        --specific parameters
        case _o.type of
        (
            0 : (
                --Plane
                _script += "is_disc,False\n"
                _script += "u_size," + ( _o.size0 / 100.) as string + "\n"
                _script += "v_size," + ( _o.size1 / 100.) as string + "\n"
                _script += "directional," + _o.lightDistribution as string + "\n"
                _script += "ignoreLightNormals," + upperfirst( _o.ignoreNormals as string ) + "\n"
                _script += "doubleSided," + upperfirst( _o.DoubleSided as string ) + "\n"
                _script += "lightPortal," + (get_lightPortal()) as string + "\n"
            )
            1 : (
                --Dome
                _script += "tex_resolution," + _o.texmap_resolution as string + "\n"
                _script += "tex_adaptive," + _o.texmap_adaptiveness as string + "\n"
                _script += "dome_spherical," + upperfirst( _o.dome_spherical as string ) + "\n"
                _script += "affect_alpha," + upperfirst( _o.dome_affect_alpha as string ) + "\n"
                --texmap_locktodome pas d'equivalent sous houdini
                _script += "dome_rayDistanceMode," + _o.dome_rayDistanceMode as string + "\n"
                _script += "dome_rayDistance," + _o.dome_rayDistance as string + "\n"
                _script += "dome_targetRadius," + _o.dome_targetRadius as string + "\n"
                _script += "dome_emitRadius," + _o.dome_emitRadius as string + "\n"
            )
            2 : (
                --Sphere
                _script += "radius," + ( _o.size0 / 100.) as string + "\n"
            )
            3 : (
                --Mesh
                --flip normals a faire
                --pick mesh a faire
                _script += "ignoreLightNormals," + upperfirst( _o.ignoreNormals as string ) + "\n"
                _script += "doubleSided," + upperfirst( _o.DoubleSided as string ) + "\n"
                _script += "lightPortal," + (get_lightPortal()) as string + "\n"
            )
            4 : (
                --Disc
                _script += "is_disc,True\n"
                _script += "u_size," + (_o.size0 / 100.) as string + "\n"
                _script += "v_size," + (_o.size1 / 100.) as string + "\n"
                _script += "directional," + _o.lightDistribution as string + "\n"
                _script += "ignoreLightNormals," + _o.ignoreNormals as string + "\n"
                _script += "doubleSided," + upperfirst( _o.DoubleSided as string ) + "\n"
                _script += "lightPortal," + (get_lightPortal()) as string + "\n"
            )
        )

        --common parameters
        _script += "enabled," + upperfirst( _o.on as string ) + "\n"

        _script += "units," + _o.normalizeColor as string + "\n"

        _script += "intensity," + _o.multiplier as string + "\n"
        _script += "colorr," + (_o.color.r / 255.) as string + "\n"
        _script += "colorg," + (_o.color.g / 255.) as string + "\n"
        _script += "colorb," + (_o.color.b / 255.) as string + "\n"
        _script += "map_color," + upperfirst( _o.texmap_on as string ) + "\n"

        --options parameters
        --exclude a faire
        _script += "shadows," + upperfirst( _o.castShadows as string ) + "\n"
        _script += "invisible," + upperfirst( _o.invisible as string ) + "\n"
        _script += "noDecay," + upperfirst( _o.noDecay as string ) + "\n"
        _script += "storeWithIrradianceMap," + upperfirst( _o.storeWithIrradMap as string ) + "\n"
        _script += "affectDiffuse," + upperfirst( _o.affect_diffuse as string ) + "\n"
        _script += "affectSpecular," + upperfirst( _o.affect_specular as string ) + "\n"
        _script += "affectReflections," + upperfirst( _o.affect_reflections as string ) + "\n"
        _script += "diffuse_contribution," + _o.diffuse_contribution as string + "\n"
        _script += "specular_contribution," + _o.specular_contribution as string + "\n"

        --sampling
        _script += "subdivs," + _o.subdivs as string + "\n"
        _script += "shadowBias," + _o.ShadowBias as string + "\n"
        _script += "cutoffThreshold," + _o.cutoffThreshold as string + "\n"

        --viewport
        --rien a exporter ici

        --advanced options
        _script += "objectID," + _o.gbufferchannel as string + "\n"

        --VRay userProps
        diffuseMult = getUserProp _o "VRay_Diffuse_Multipier"
        if diffuseMult != undefined do _script += "diffuseMult," + diffuseMult as string + "\n"
        causticMult = getUserProp _o "VRay_Caustics_Multipier"
        if causticMult != undefined do _script += "causticMult," + causticMult as string + "\n"
        photonSubdivs = getUserProp _o "VRay_Diffuse_Subdivs"
        if photonSubdivs != undefined do _script += "photonSubdivs," + photonSubdivs as string + "\n"
        causticSubdivs = getUserProp _o "VRay_Caustics_Subdivs"
        if causticSubdivs != undefined do _script += "causticSubdivs," + causticSubdivs as string + "\n"
    )else if classOf _o == VRaySun then
    (
        _script += "enabled," + upperfirst(_o.enabled as string) + "\n"
        _script += "invisible," + upperfirst(_o.invisible as string) + "\n"
        _script += "affectDiffuse," + upperfirst(_o.affect_diffuse as string) + "\n"
        _script += "diffuse_contribution," + _o.diffuse_contribution as string + "\n"
        _script += "affectSpecular," + upperfirst(_o.affect_specular as string) + "\n"
        _script += "specular_contribution," + _o.specular_contribution as string + "\n"
        _script += "atmos_shadows," + upperfirst(_o.cast_atmospheric_shadows as string) + "\n"
        _script += "turbidity," + _o.turbidity as string + "\n"
        _script += "ozone," + _o.ozone as string + "\n"
        _script += "intensity_multiplier," + _o.intensity_multiplier as string + "\n"
        _script += "size_multiplier," + _o.size_multiplier as string + "\n"
        _script += "filter_colorr," + (_o.filter_Color.r / 255.) as string + "\n"
        _script += "filter_colorg," + (_o.filter_Color.g / 255.) as string + "\n"
        _script += "filter_colorb," + (_o.filter_Color.b / 255.) as string + "\n"
        _script += "color_mode," + _o.color_mode as string + "\n"
        _script += "shadow_subdivs," + _o.shadow_subdivs as string + "\n"
        _script += "shadowBias," + (_o.shadow_bias / 100.) as string + "\n"
        _script += "photon_radius," + (_o.photon_emit_radius / 100) as string + "\n"
        _script += "photonSubdivs," + 500 as string + "\n" --pas d'equivalent dans max
        _script += "sky_model," + _o.sky_model as string + "\n"
        _script += "horiz_illum," + _o.indirect_horiz_illum as string + "\n"
        _script += "ground_albedor," + (_o.ground_albedo.r / 255.) as string + "\n"
        _script += "ground_albedog," + (_o.ground_albedo.g / 255.) as string + "\n"
        _script += "ground_albedob," + (_o.ground_albedo.b / 255.) as string + "\n"
        --"" _o.blend_angle --pas d'equivalent dans houdini
        --"" _o.horizon_offset --pas d'equivalent dans houdini
        _script += "water_vapour," + 2 as string + "\n" --pas d'equivalent dans max
        _script += "shadows," + 1 as string + "\n" --pas d'equivalent dans max
    )else if classOf _o == VRayAmbientLight then
    (
        _script += "enabled," + upperfirst(_o.enabled as string) + "\n"
        _script += "intensity," + _o.intensity as string + "\n"
        _script += "colorr," + (_o.color.r / 255.) as string + "\n"
        _script += "colorg," + (_o.color.g / 255.) as string + "\n"
        _script += "colorb," + (_o.color.b / 255.) as string + "\n"

    )else if classOf _o == VRayIES then
    (
        -- je sais pas sis quelqu un utilise ce genre de lumiere....
        _script += "enabled," + upperfirst(_o.enabled as string) + "\n"
        _script += "power," + _o.power as string + "\n"
        --_script += "rescale_max_intensty," -- pas trouvé d'equivalent sous max ?
        _script += "ies_file,'" + _o.ies_file + "'\n"
        _script += "colorr," + (_o.color.r / 255.) as string + "\n"
        _script += "colorg," + (_o.color.g / 255.) as string + "\n"
        _script += "colorb," + (_o.color.b / 255.) as string + "\n"

        fn getlightshapemode _o = if _o.override_shape == true then return 1 else return 0
        _script += "ies_light_shape," + (getlightshapemode()) as string
        _script += "ies_light_height," + _o.height as string + "\n"
        _script += "ies_light_length," + _o.length as string + "\n"
        _script += "ies_light_width," + _o.width as string + "\n"
        _script += "ies_light_diameter," + _o.diameter as string + "\n"
        _script += "filter_colorr," + (_o.color.r / 255.) as string + "\n"
        _script += "filter_colorg," + (_o.color.g / 255.) as string + "\n"
        _script += "filter_colorb," + (_o.color.b / 255.) as string + "\n"
        --_script += "soft_shadows," -- pas trouvé d'equivalent sous max ?
        --_script += "use_global_light_level," -- pas trouvé d'equivalent sous max ?
        --_script += "shadow_subdivs," + _o.shadow_subdivs as string + "\n" -- pas trouvé d'equivalent sous max ?
        _script += "shadowBias," + _o.shadow_bias as string + "\n"
        _script += "affectDiffuse," + upperfirst(_o.affect_diffuse as string) + "\n"
        _script += "diffuse_contribution," + _o.diffuse_contribution as string + "\n"
        _script += "affectSpecular," + upperfirst(_o.affect_specular as string) + "\n"
        _script += "specular_contribution," + _o.specular_contribution as string + "\n"
    )

    setclipboardText _script
    print( "Light successfully exported to clipboard" )
)

if selection.count > 0 then
(
    _o = selection[1]

    if classOf _o == Targetobject do
        _o = (for _c in lights where _c.target == _o collect _c)[1]

    if superClassOf _o == light then
    (
        if classOf _o == VRayLight or classOf _o == VRaySun or classOf _o == VRayAmbientLight or classOf _o == VRayIES  then
        (
            exportlighttoclipboard _o

        )else ( messageBox "This kind of light is not currently suported!" )
    )else ( messageBox "Selection is not a light!" )
)else ( messageBox "Nothing to export!" )
