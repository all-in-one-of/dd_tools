fn normalizeName _name = (
    re = dotnetObject "System.Text.RegularExpressions.Regex" "[^a-zA-Z0-9]"
    _name = re.Replace _name "_"
    re = dotnetObject "System.Text.RegularExpressions.Regex" "_+"
    _name = re.Replace _name "_"
    re = dotnetObject "System.Text.RegularExpressions.Regex" "_$"
    re.Replace _name ""
)


fn lookupTableComparator a b = (
	if a == b then -1
	else if a.name > b.name then 1
	else if a.name < b.name then -1
	else 0
)


for o in objects do o.name = normalizeName o.name

_objects = objects as array
qsort _objects lookupTableComparator

for o in objects where bsearch o _objects lookupTableComparator != undefined do o.name = uniqueName (o.name + "_") numDigits:0
