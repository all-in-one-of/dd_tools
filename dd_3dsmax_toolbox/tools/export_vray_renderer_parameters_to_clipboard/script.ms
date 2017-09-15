fn VRayRendererToClipboard =
(
	renderSceneDialog.commit()
	currentdir = getFilenamePath ( getThisScriptFilename() )
	fileIn (currentdir + @"\ExportParametersToString_V01.ms")

	render_camera = "/obj/cam1"
	render_camera = getActiveCamera()
	if render_camera != undefined do render_camera = "/obj/" + tolower(render_camera.name)

	fn trange = if rendTimeType == 1 then 0 else 1

	--hou.parm('/out/vray_renderer/f1').deleteAllKeyframes()
	--hou.parm('/out/vray_renderer/f2').deleteAllKeyframes()

	script = ""
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
	script += ExportParametersToString renderers.current

	setclipboardText script
)

VRayRendererToClipboard()
