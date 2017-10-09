fn writeVRScenefiles _start:currentframe _end:currentframe =
(
    _vrscenefile = sysinfo.tempdir + getFilenameFile maxfilename + ".vrscene"

    _script = "#scene_export\n\n"


    if _start != currentframe and _end != currentframe then
            vrayExportRTScene _vrscenefile exportCompressed:false exportHEXFormatMesh:false exportHEXFormatTransf:false separateFiles:false exportView:true exportLights:true exportGeometry:false exportNodes:true exportMaterials:true exportTextures:true exportBitmaps:true prefix:"" startFrame:_start endFrame:_end stripPaths:false
        else
            vrayExportRTScene _vrscenefile exportCompressed:false exportHEXFormatMesh:false exportHEXFormatTransf:false separateFiles:false exportView:true exportLights:true exportGeometry:false exportNodes:true exportMaterials:true exportTextures:true exportBitmaps:true prefix:"" stripPaths:false

        _script += "filename," + _vrscenefile + "\n"

    fs = openFile _vrscenefile mode:"a"

    _rendercam = "cam1"

    if getActiveCamera() != undefined do _rendercam = (getActiveCamera()).name

    format "CustomSettings camera_settings {\n  camera=\"%\"\n}" _rendercam to:fs
    close fs

    setclipboardText _script

    print "scene successfully exported"
)

writeVRScenefiles()
