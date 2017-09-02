"""Compare the api classes of henna and gavin"""
import json

from tools.printer import Printer

printer = Printer(True)
gavin = printer.open_json('../docs/randep-model/classed_apis.txt')
henna = printer.open_json('../docs/randep-model/classed_apis_henna.txt')
randep = printer.open_json('../docs/randep-model/randep-skeleton.json')

# uni_gavin = []
all_uni_gavin = []
# uni_henna = []
all_uni_henna = []
all_uni_randep = []

team_classify = {
    "stealth": {"fingerprinting": {"apis":[], "categories":[], "signatures":[]},
                "propagating": {"apis":[], "categories":[], "signatures":[]},
                "communicating": {"apis":[], "categories":[], "signatures":[]},
                "mapping": {"apis":[], "categories":[], "signatures":[]}},
    "suspicious": {"encrypting": {"apis":[], "categories":[], "signatures":[]},
                   "locking": {"apis":[], "categories":[], "signatures":[]}},
    "termination": {"deleting": {"apis":[], "categories":[], "signatures":[]},
                    "threatening": {"apis":[], "categories":[], "signatures":[]}}
}

team_clash_g = [
    "GetCursorPos", "GetVolumePathNamesForVolumeNameW", "GetVolumePathNameW", "GetFileAttributesExW", "NetShareEnum",
    "GetVolumeNameForVolumeMountPointW", "CryptDecrypt"
]
team_clash_h = ["GetFileInformationByHandleEx", "SetFilePointer", "GetAdaptersInfo", "GetFileInformationByHandle"]

output = ""

for group in gavin:
    for cat in gavin[group]:
        # subtract from user group the APIs that clash with the other user's choice, so we only get unique APIs
        # per user. One group needs to add all apart from those that clash, and the other needs to add all apart
        # from those that are already from the other group and those that clash
        uni_gavin = list(set(gavin[group][cat]['apis']) - set(team_clash_h))
        uni_henna = list(set(henna[group][cat]['apis']) - set(gavin[group][cat]['apis']) - set(team_clash_g))
        # add the unique APIs from the randep-skeleton
        uni_randep = list(set(randep[group][cat]['apis']) - set(uni_gavin) - set(uni_henna))
        # temp_list.extend(list(set(team_clash_g).intersection(gavin[group][cat]['apis'])))
        # temp_list.extend(list(set(team_clash_h).intersection(henna[group][cat]['apis'])))
        temp_list = []
        temp_list.extend(uni_gavin)
        temp_list.extend(uni_henna)
        temp_list.extend(uni_randep)
        temp_list = sorted(list(set(temp_list)))
        team_classify[group][cat]['apis'].extend(temp_list)
        # print "Team classify: %s" % team_classify
        # print uni_gavin
        # team_classify[group][cat]['apis'].extend(uni_gavin)
        # print "Team classify: %s" % team_classify
        # team_classify[group][cat]['apis'].extend(uni_henna)
        # team_classify[group][cat]['apis'].extend(list(set(uni_gavin).intersection(uni_henna)))
        output += "In %s Gavin has these unique APIs %s\n" % (cat, json.dumps(uni_gavin))
        output += "In %s Henna has these unique APIs %s\n" % (cat, json.dumps(uni_henna))
        all_uni_gavin.extend(uni_gavin)
        all_uni_henna.extend(uni_henna)
        all_uni_randep.extend(uni_randep)

output += "Gavin has %d APIs\n" % len(all_uni_gavin)
output += "Henna has %d APIs\n" % len(all_uni_henna)

unique = [api for api in all_uni_gavin if api not in all_uni_henna]
output += "Gavin uniquely used %d APIs, which are %s\n" % (len(unique), json.dumps(unique))

# print list(set(all_uni_gavin) - set(unique))

unique = [api for api in all_uni_henna if api not in all_uni_gavin]
output += "Henna uniquely used %d APIs, which are %s\n" % (len(unique), json.dumps(unique))

output += "Henna clashed with Gavin on %s\n" % json.dumps(list(set(all_uni_henna) - set(unique)))

dup_all_uni_randep = {}
for i, api in enumerate(all_uni_randep):
    all_uni_randep.pop(i)
    if api in all_uni_randep:
        if api not in dup_all_uni_randep:
            dup_all_uni_randep[api] = [i]
        else:
            dup_all_uni_randep[api].append(i)

output += "Randep has duplicate keys: %s\n" % dup_all_uni_randep

printer.write_file('../docs/randep-model/randep_team_differences.txt', output, 'w')
printer.write_file('../docs/randep-model/team_classify.json',
                   json.dumps(team_classify, sort_keys=True, indent=4), 'w')
