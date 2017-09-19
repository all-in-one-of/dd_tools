fn getsmeselectednode =
(
    smeSelMats = #()
    if (sme.IsOpen()) do
    (
        viewNode = sme.GetView ( sme.activeView )
        for n = 1 to trackViewNodes[#sme][( sme.activeView )].numSubs do
        (
            m = trackViewNodes[#sme][( sme.activeView )][n].reference
            b = viewNode.GetNodeByRef m
            if b.selected and ( superClassOf m == material or  superClassOf m == textureMap ) do append smeSelMats m
        )
	)
	smeSelMats
)

fn writeparameterstofile o =
(
    fname = getSaveFileName caption:"Output filemame" filename:( "max_" + toLower ( ( classOf o as string ) ) + "_params.txt" ) types:".txt|*.txt" historyCategory:".params.txt"
    if fname != undefined do
    (
        fs = createFile fname
        format "class: %\n" ( toLower( classOf o as string ) ) to:fs
        pns = getPropNames o
        sort pns
        for pn in pns do
        (
            p = getProperty o pn
            c = classOf p
            format "name: % - type: % - value: %\n" ( pn as string ) ( classOf p as string ) ( p as string ) to:fs
        )
        flush fs
        close fs
        free fs
    )
)

_c = undefined
_sme = getsmeselectednode()
if selection.count == 1 then
(
    _o = selection[1]
    if classOf _o == Targetobject do _o = (for _n in objects where _n.target == _o collect _n)[1]
    if superClassOf _o == camera or superClassOf _o == light then
        _c = _o
    else if superClassOf _o == GeometryClass and _o.material != undefined then
        _c = _o.material
)else if _sme.count == 1 then
(
    _c = _sme[1]
)
else
(
    _r = renderers.current
    if findString ( classOf _r as string ) "V_Ray_" != undefined do _c = _r
)

if _c != undefined then
    writeparameterstofile _c
else
    messageBox( "Nothing to export." )