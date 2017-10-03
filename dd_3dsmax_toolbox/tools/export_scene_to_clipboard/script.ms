
fn writeVRScenefiles _start:currentframe _end:currentframe =
(
    _script = ""
    _vrscenefile = sysinfo.tempdir + getFilenameFile maxfilename + ".vrscene"

    if _start != currentframe and _end != currentframe then
        vrayExportRTScene _vrscenefile exportCompressed:false exportHEXFormatMesh:false exportHEXFormatTransf:false separateFiles:false exportView:true exportLights:true exportGeometry:false exportNodes:true exportMaterials:true exportTextures:true exportBitmaps:true prefix:"" startFrame:_start endFrame:_end stripPaths:false
    else
        vrayExportRTScene _vrscenefile exportCompressed:false exportHEXFormatMesh:false exportHEXFormatTransf:false separateFiles:false exportView:true exportLights:true exportGeometry:false exportNodes:true exportMaterials:true exportTextures:true exportBitmaps:true prefix:"" stripPaths:false

    _script += "filename," + _vrscenefile + "\n"

    _script
)



--if selection.count > 0 then
--(
    _script = "#scene_export\n\n"
    --for _o in selection do
    --(
        --if isValidNode _o == true then
        --(
            --if superClassOf _o == GeometryClass or superClassOf _o == shape and classOf _o != Targetobject then
            --(
                _script += writeVRScenefiles()
            --)
            --else print(_o.name +  " is not geometry or shape" )
        --)else print(_o.name +  " is not a valid node" )
    --)
    setclipboardText _script
--)
--else messageBox( "Nothing selected" )
