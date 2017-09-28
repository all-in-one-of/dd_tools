fn upperfirst s = ((toUpper s[1]) + (substring s 2 s.count))

fn parmstostring n =
(
	script = ""
	global glob_n
	glob_n = n
	lib_dir = getFilenamePath ( getThisScriptFilename() )
	
	if n != undefined then
	(
        pc_fname = lib_dir + "\\" + toLower((classOf n) as string) + ".pc"
        if doesfileexist pc_fname then
        (
            file = openFile pc_fname
            while not eof file do
            (
                r =  readLine file
                if substring r 1 3 == "fn " then
                    execute r
                else if r != "" and r[1] != "!" and r[1] != "#" do
                (
                    split1 = filterString r ":"
                    split2 = filterString split1[1] "/"
                    split3 = filterString split2[1] ">"

                    convert_fn = split1[2]
                    type = split2[2]
                    parmfrom = split3[1] as string
                    parmto = split3[2] as string

                    parmval = (execute (" glob_n." + parmfrom)) as string
                    if convert_fn != undefined do
                        parmval = ( execute ( convert_fn + " glob_n." + parmfrom ) ) as string
                    if type == "Boolean" do
                        parmval = upperfirst parmval
                    if type == "String" do
                        parmval = "'" + parmval + "'"

                    script += parmto + "," + parmval + "\n"
                )
            )
            seek file 0
            close file
        )else (messagebox "Conversion file not found for this node type!")
	)else (messagebox "Nothing to export!")
	script
)
