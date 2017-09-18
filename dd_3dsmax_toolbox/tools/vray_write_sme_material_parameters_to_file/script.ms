fn getsmeselectedmaterials =
(
	viewNode = sme.GetView ( sme.activeView )
	smeSelMats = #()
	for n = 1 to trackViewNodes[#sme][( sme.activeView )].numSubs do (
		m = trackViewNodes[#sme][( sme.activeView )][n].reference
		b = viewNode.GetNodeByRef m
		if b.selected and superClassOf m == material do append smeSelMats m
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

writeparameterstofile ( getsmeselectedmaterials() )[1]
