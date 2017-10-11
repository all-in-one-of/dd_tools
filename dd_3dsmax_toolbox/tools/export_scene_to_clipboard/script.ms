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
    appendLineToFile ( _vrscenefile + ".vrscene" ) "#include \"%\"\n" (_vrscenefile + "_settings.vrscene")

    _rendercam = if getActiveCamera() != undefined then (getActiveCamera()).name else ""
    _fps = (framerate as float) as string
    _range = [animationrange.start.frame as integer , animationrange.end.frame as integer] as string

    _str = "CustomSettings scene_settings {\n  camera=\"" + _rendercam + "\";\n  fps=" + _fps + ";\n  range=" + _range + ";\n}\n"

    _aa_filter = if renderers.current.filter_on == false then 0 else filter_kernel_convert renderers.current.filter_kernel as string

    _str += "\nSettingsImageSampler aa_filter {\n  filter_type=" + _aa_filter + ";\n}\n"

    writeToFile ( _vrscenefile + "_settings.vrscene" ) _str

    print "scene successfully exported"
)

writeVRScenefiles()
