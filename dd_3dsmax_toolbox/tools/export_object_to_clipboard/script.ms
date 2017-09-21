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



fn exportObject _o _s animated:false step:1 substeps:1 =
(	
	if isvalidnode _o == true do
	if superclassof _o == GeometryClass do
	(
	    _name = toLower( substituteString ( substituteString _o.name " " "_" ) "." "_" )
		_abcfile = sysinfo.tempdir + _name + ".abc"
		frange = [0,100]
		opath = getHierarchy _o			
		if animated == false then frange = [currenttime.frame, currenttime.frame] else frange = [animationrange.start.frame, animationrange.end.frame]
		jobString = "filename=" + _abcfile
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
		jobString += ";particlesystemtomeshconversion=true"
		--jobString += ";dynamictopology=true"
		jobString += ";storageFormat=hdf5"
		result = ExocortexAlembic.createExportJobs( jobString )
		if( result != 0 ) then
		(
			messageBox "Failure - See Maxscript Listener for details." title:"Exocortex Alembic Export"
		)else
		(
			_s += "name," + _name + "\n"
			_s += "object_id," + _o.gbufferChannel  as string + "\n"
			_s += "wirecolor,(" + ( _o.wirecolor.r / 255. ) as string + "," + ( _o.wirecolor.g/ 255. ) as string + "," + ( _o.wirecolor.b / 255. ) as string + ")\n"
			_s += "handle," + _o.inode.handle as string + "\n"
			_s += "filename," + _abcfile + "\n\n"
		)
	)
	_s
)


if selection.count > 0 then
(
    _script = "#abc_export,"  + ( framerate as float ) as string + ",[" + ( animationrange.start.frame as integer ) as string + ", " + ( animationrange.end.frame as integer ) as string + "]\n\n"

    for _o in selection do
    (
        if superClassOf _o == GeometryClass and classOf _o != Targetobject then
        (
            animated = ( _o.isAnimated or isDeformable _o )
            _script = exportObject _o _script animated:animated step:1 substeps:1
        )
        else print(_o.name +  "is not geometry" )
    )
    setclipboardText _script
)
else messageBox( "Nothing selected" )
