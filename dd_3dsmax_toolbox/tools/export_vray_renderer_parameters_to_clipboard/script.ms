fn getparentfolder _f =
(
    for i = _f.count to 1 by -1 do
    (
        if _f[i] == "\\" do
        (
            _f = substring _f 1 (i-1)
            exit
        )
    )
    _f
)

fn vrayrendererparameterstoclipboard =
(
	renderSceneDialog.commit()
	lib_dir = getparentfolder( trimRight ( getFilenamePath ( getThisScriptFilename() ) ) "\\/" ) + "\\lib\\"
	fileIn (lib_dir + "parmstostring.ms")

	if getActiveCamera() != undefined then render_camera = "/obj/" + toLower( render_camera.name ) else render_camera = "/obj/cam1"

	fn trange = if rendTimeType == 1 then 0 else 1

	--hou.parm('/out/vray_renderer/f1').deleteAllKeyframes()
	--hou.parm('/out/vray_renderer/f2').deleteAllKeyframes()

	script = "#vray_renderer\n"
	script += "trange," + (trange()) as string + "\n"

	if rendTimeType == 2 then
	(
		script += "f1," + (animationrange.start.frame) as string + "\n"
		script += "f2," + (animationrange.end.frame) as string + "\n"
	)
	else if (rendTimeType == 3) do
	(
		script += "f1," + (rendStart.frame) as string + "\n"
		script += "f2," + (rendEnd.frame) as string + "\n"
	)
	script += "f3," + rendNThFrame as string + "\n"
	script += "render_camera,'" + render_camera + "'\n"
	script += "render_network_environment,'/out/env'\n"
	script += "render_network_render_channels,'/out/render_elements'\n"
	script += parmstostring( renderers.current )

	setclipboardText script
	print( "Render parameters successfully exported to clipboard" )
)

if findstring( ( classOf renderers.current ) as string ) "V_Ray" != undefined then
    vrayrendererparameterstoclipboard()
else
    messageBox( "Current renderer is not VRay" )

