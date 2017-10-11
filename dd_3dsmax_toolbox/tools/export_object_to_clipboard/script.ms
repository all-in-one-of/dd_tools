fn getHierarchy _o _opath:"" = (
	_opath = "/" + _o.name + _opath
	if _o.parent != undefined do
	(
		_opath = getHierarchy _o.parent _opath:_opath
	)
	_opath
)

/*
fn objectIsAnimated _o = (
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

fn exportObject _o _step:1 _substeps:1 = (

    _animated = ( _o.isAnimated or isDeformable _o )
    _script = ""
    _name = toLower( substituteString ( substituteString _o.name " " "_" ) "." "_" )
    _abcfile = sysinfo.tempdir + _name + ".abc"
    _frange = [0,100]
    _opath = getHierarchy _o
    if _animated == false then _frange = [currenttime.frame, currenttime.frame] else _frange = [animationrange.start.frame, animationrange.end.frame]

    if classOf _o != HairObject and classOf _o != GuidesObject then
    (
        _job = "filename=" + _abcfile
        _job += ";in=" + (_frange[1] as string)
        _job += ";out=" + (_frange[2] as string)
        _job += ";step=" + (_step as string)
        _job += ";substep=" + (_substeps as string)
        _job += ";purepointcache=false"
        _job += ";normals=true"
        _job += ";uvs=true"
        _job += ";materialids=true"
        _job += ";exportselected=false"
        _job += ";objects=" + getHierarchy _o
        _job += ";flattenhierarchy=true"
        _job += ";automaticinstancing=true"
        _job += ";facesets=partitioningFacesetsOnly"
        _job += ";transformCache=false"
        _job += ";validateMeshTopology=false"
        _job += ";renameConflictingNodes=false"
        _job += ";mergePolyMeshSubtree=true"
        _job += ";particlesystemtomeshconversion=true"
        --_job += ";dynamictopology=true"
        _job += ";transformCache=true"
        _job += ";storageFormat=hdf5"
        _result = ExocortexAlembic.createExportJobs( _job )
        if( _result != 0 ) then
        (
            messageBox "Failure - See Maxscript Listener for details." title:"Exocortex Alembic Export"
        )else
        (
            _script += "name," + _name + "\n"
            _script += "object_id," + _o.gbufferChannel  as string + "\n"
            _script += "wirecolor,(" + ( _o.wirecolor.r / 255. ) as string + "," + ( _o.wirecolor.g/ 255. ) as string + "," + ( _o.wirecolor.b / 255. ) as string + ")\n"
            _script += "handle," + _o.inode.handle as string + "\n"
            _script += "filename," + _abcfile + "\n\n"
        )
    )else (
        --https://ephere.com/plugins/autodesk/max/ornatrix/docs/4/Alembic_Export.html#Examples
        --OxAlembicExport [string filePath] [bool exportSelectedHairs] [int startFrame] [int endFrame] [bool exportRenderVersion] [int upDirection] [int format]
        _result = OxAlembicExport _abcfile true _frange[1] _frange[2]-- false 1 0
        print _result
        _script += "name," + _name + "\n"
        _script += "object_id," + _o.gbufferChannel  as string + "\n"
        _script += "wirecolor,(" + ( _o.wirecolor.r / 255. ) as string + "," + ( _o.wirecolor.g/ 255. ) as string + "," + ( _o.wirecolor.b / 255. ) as string + ")\n"
        _script += "handle," + _o.inode.handle as string + "\n"
        _script += "filename," + _abcfile + "\n\n"
    )

	_script
)


if selection.count > 0 then
(
    _script = "#abc_export,"  + ( framerate as float ) as string + ",[" + ( animationrange.start.frame as integer ) as string + ", " + ( animationrange.end.frame as integer ) as string + "]\n\n"
    for _o in selection do
    (
        if isValidNode _o == true then
        (
            if superClassOf _o == GeometryClass or superClassOf _o == shape and classOf _o != Targetobject then
            (
                animated = ( _o.isAnimated or isDeformable _o )
                _script += exportObject _o animated:animated step:1 substeps:1
            )
            else print(_o.name +  " is not geometry or shape" )
        )else print(_o.name +  " is not a valid node" )
    )
    setclipboardText _script
)
else messageBox( "Nothing selected" )
