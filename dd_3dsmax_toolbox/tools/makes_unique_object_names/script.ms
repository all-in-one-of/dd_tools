allName = for i in geometry collect i.name
for o in geometry where findItem allName o.name != 0 do o.name = uniqueName (o.name + "_") numDigits:1