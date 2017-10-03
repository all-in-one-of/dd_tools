import re

regex = r"(.*?)\ (.*?)\ {(.*?)\}"
content = ''
fname = 'C:/Users/j.fabbris/Desktop/k2zo_seul_materials.vrscene'

plugins = list()
connections = list()

with open(fname, 'r') as content_file:
    content = content_file.read()

matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)
for matchNum, match in enumerate(matches):
    for groupNum in range(0, len(match.groups())):
        type = match.group(1).strip()
        name = match.group(2).strip()
        split = match.group(3).split(';')
        parms = list()
        for p in (i for i in split if i.strip() != ''):
            parm = p.strip().split('=')
            parm_name = parm[0]
            parm_val = parm[1]

            if not parm_val.__contains__('@'):
                parms.append({'Name': parm_name, 'Value': parm_val})
            else:
                connections.append({'From': name, 'Input': parm_name, 'To': parm_val.replace('@', '_')})

        plugins.append({'Type': type, 'Name': name, 'Parms': parms})

print(plugins)
print(connections)
