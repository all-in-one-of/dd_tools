fn filter_kernel_convert val = case classOf val of (Area : 1;VRayBoxFilter : 2;Catmull_Rom : 3;Cook_Variable : 4;Soften : 5;VRayLanczosFilter : 6;Mitchell_Netravali : 7;VRayMitNetFilter : 7;VRaySincFilter : 8;VRayTriangleFilter : 9;default : 6)

fn writeVRScenefiles _start:currentframe _end:currentframe =
(
    _vrscenefile = sysinfo.tempdir + getFilenameFile maxfilename + ".vrscene"

    _script = "#scene_export\n\n"


    if _start != currentframe and _end != currentframe then
            vrayExportRTScene _vrscenefile exportCompressed:false exportHEXFormatMesh:false exportHEXFormatTransf:false separateFiles:true exportView:false exportLights:false exportGeometry:false exportNodes:true exportMaterials:true exportTextures:true exportBitmaps:true prefix:"" startFrame:_start endFrame:_end stripPaths:false
        else
            vrayExportRTScene _vrscenefile exportCompressed:false exportHEXFormatMesh:false exportHEXFormatTransf:false separateFiles:true exportView:false exportLights:false exportGeometry:false exportNodes:true exportMaterials:true exportTextures:true exportBitmaps:true prefix:"" stripPaths:false

        _script += "filename," + _vrscenefile + "\n"


    setclipboardText _script

    renderSceneDialog.commit()

    global _fs
    try(
        _fs = openFile _vrscenefile mode:"a"
        _rendercam = if getActiveCamera() != undefined then (getActiveCamera()).name else ""
        _fps = (framerate as float) as string
        _range = [animationrange.start.frame as integer , animationrange.end.frame as integer] as string

        format "CustomSettings scene_settings {\n  camera=\"%\";\n  fps=%;\n  range=%;\n}\n" _rendercam _fps _range to:_fs

        _aa_filter = if renderers.current.filter_on == false then 0 else filter_kernel_convert renderers.current.filter_kernel

        format "\nSettingsImageSampler aa_filter {\n  filter_type=%;\n}\n" _aa_filter to:_fs

    )catch(print "cannot adding CustomSettings to .vrscene file...")
    close _fs

    print "scene successfully exported"
)

writeVRScenefiles()
