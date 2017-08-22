from tools.printer import Printer

printer = Printer(True)
skeleton = printer.open_json('../docs/randep-model/team_classify.json')
classify = printer.open_json('../docs/classify.json')
classed_apis = []
un_classed_apis = []
re_classed_apis = []
all_apis = []
for group in skeleton:
    for cat in skeleton[group]:
        classed_apis.extend(skeleton[group][cat]['apis'])

for api in classify['apis']:
    all_apis.append(api)

# omit the last letter if it is a capital, to remove the variant of the API name
classed_apis = [x.lower()[:-1] if x[-1].isupper() else x.lower() for x in classed_apis]
all_apis = [x.lower()[:-1] if x[-1].isupper() else x.lower() for x in all_apis]
# omit the first two chars if it is Nt
classed_apis = [x[2:] if x[:2] == 'nt' else x for x in classed_apis]
all_apis = [x[2:] if x[:2] == 'nt' else x for x in all_apis]
# omit the next last two letters if it is ex
classed_apis = [x[:-2] if x[-2:] == 'ex' else x for x in classed_apis]
all_apis = [x[:-2] if x[-2:] == 'ex' else x for x in all_apis]

for api in all_apis:
    if api not in classed_apis:
        un_classed_apis.append(api)
    else:
        re_classed_apis.append(api)

# print classed_apis
print list(set(classed_apis))
print "len(set(classed_apis)): %s and len(classed_apis): %s" % (len(set(classed_apis)), len(classed_apis))
print "unclassed apis: %s, length: %s" % (un_classed_apis, len(un_classed_apis))
print "reclasses apis: %s, lenght: %s" % (re_classed_apis, len(re_classed_apis))
# output = [w for w in classed_apis if not set(w.split()).intersection(un_classed_apis)]
# print "output: %s len: %s" % (output, len(output))

un_classed_apis_desc = {}
for cat in classify['categories']:
    for api in classify['categories'][cat]:
        t_api = api.lower()[:-1] if api[-1].isupper() else api.lower()
        t_api = t_api[2:] if t_api[:2] == 'nt' else t_api
        # print t_api
        if t_api in un_classed_apis:
            un_classed_apis_desc[api] = {
                'description': classify['categories'][cat][api]['description'],
                'link': classify['categories'][cat][api]['link']
            }

# printer.write_file("../docs/randep-model/unclassed apis", json.dumps(un_classed_apis_desc, sort_keys=True, indent=4), 'w')
