fn lookupTableComparator a b = (
	if a == b then -1
	else if a.name > b.name then 1
	else if a.name < b.name then -1
	else 0
)
_objects = objects as array
qsort _objects lookupTableComparator

for o in objects where bsearch o _objects lookupTableComparator != undefined do o.name = uniqueName (o.name + "_") numDigits:0