fn writeVRScenefiles _start:currentframe _end:currentframe =
(
    _vrscenefile = sysinfo.tempdir + getFilenameFile maxfilename + ".vrscene"

    _script = "#scene_export\n\n"


    if _start != currentframe and _end != currentframe then
            vrayExportRTScene _vrscenefile exportCompressed:false exportHEXFormatMesh:false exportHEXFormatTransf:false separateFiles:false exportView:true exportLights:true exportGeometry:false exportNodes:true exportMaterials:true exportTextures:true exportBitmaps:true prefix:"" startFrame:_start endFrame:_end stripPaths:false
        else
            vrayExportRTScene _vrscenefile exportCompressed:false exportHEXFormatMesh:false exportHEXFormatTransf:false separateFiles:false exportView:true exportLights:true exportGeometry:false exportNodes:true exportMaterials:true exportTextures:true exportBitmaps:true prefix:"" stripPaths:false

        _script += "filename," + _vrscenefile + "\n"



    setclipboardText _script

    global _fs
    try(
        _fs = openFile _vrscenefile mode:"a"
        _rendercam = if getActiveCamera() != undefined then (getActiveCamera()).name else ""
        _fps = (framerate as float) as string
        _range = [animationrange.start.frame as integer , animationrange.end.frame as integer] as string

        format "CustomSettings scene_settings {\n  camera=\"%\";\n  fps=%;\n  range=%;\n}" _rendercam _fps _range to:_fs
    )catch(print "cannot adding CustomSettings to .vrscene file...")
    close _fs

    print "scene successfully exported"
)

writeVRScenefiles()
