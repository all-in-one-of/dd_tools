fn getHierarchy o opath:"" =
(
	opath = "/" + o.name + opath
	if o.parent != undefined do
	(
		opath = getHierarchy o.parent opath:opath
	)
	opath
)

/*
fn objectIsAnimated _o =
(
    _o = $
    _isAnimated = _o.isAnimated
    for i = 1 to _o.numSubs while not _isAnimated do
    (
        _suba = getSubAnim _o i
        if _suba.controller != undefined do
        if _suba.isAnimated do _isAnimated = true
    )
    for _m in _o.modifiers where _m.enabled do
    (
        for i = 1 to _m.numSubs while not _isAnimated do
        (
            _suba = getSubAnim _m i
            if _suba.controller != undefined do
            if _suba.isAnimated do _isAnimated = true
        )
    )
    _isAnimated
    isDeformable _o
)
*/

fn exportObject _o animated:false step:1 substeps:1 =
(	
	if isvalidnode _o == true do
	if superclassof _o == GeometryClass do
	(
		tmpabcfile = sysinfo.tempdir + "tmp_abc"
		frange = [0,100]
		opath = getHierarchy _o			
		if animated == false then frange = [currenttime.frame, currenttime.frame] else frange = [animationrange.start.frame, animationrange.end.frame]
		jobString = "filename=" + tmpabcfile
		jobString += ";in=" + (frange[1] as string)
		jobString += ";out=" + (frange[2] as string)
		jobString += ";step=" + (step as string)
		jobString += ";substep=" + (substeps as string)		
		jobString += ";purepointcache=false"
		jobString += ";normals=true"		
		jobString += ";uvs=true" 
		jobString += ";materialids=true" 
		jobString += ";exportselected=false"
		jobString += ";objects=" + getHierarchy _o
		jobString += ";flattenhierarchy=true" 
		jobString += ";automaticinstancing=true"
		jobString += ";facesets=partitioningFacesetsOnly"
		jobString += ";transformCache=false"
		jobString += ";validateMeshTopology=false"
		jobString += ";renameConflictingNodes=false"
		jobString += ";mergePolyMeshSubtree=true"
		--jobString += ";dynamictopology=true"
		jobString += ";storageFormat=hdf5"
		result = ExocortexAlembic.createExportJobs( jobString )
		if( result != 0 ) then
		(
			messageBox "Failure - See Maxscript Listener for details." title:"Exocortex Alembic Export"
		)else
		(
			script = "#abc_export\n"
			script += "filename=" + tmpabcfile + "\n"
			script += "name=" + toLower( substituteString _o.name " " "_" ) + "\n"
			script += "object_id=" + _o.gbufferChannel  as string + "\n"
			script += "wirecolor=(" + ( _o.wirecolor.r / 255. ) as string + "," + ( _o.wirecolor.g/ 255. ) as string + "," + ( _o.wirecolor.b / 255. ) as string + ")\n"
			script += "handle=" + _o.inode.handle as string "\n"
			setclipboardText script
		)		
	)
)


if selection.count == 1 then
(
    _o = selection[1]
    if superClassOf _o == GeometryClass then
    (
        animated = ( _o.isAnimated or isDeformable _o )
        exportObject _o animated:animated step:1 substeps:1
    )
    else
        messageBox( "Select geometry" )
)
else
    if selection.count == 0 then
        messageBox( "Nothing selected" )
    else
        messageBox( "Too much objects selected" )
