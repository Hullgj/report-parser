from __future__ import print_function
import json

j_dump = json.dumps([
	'foo', 
	{
		'bar': (
				'baz', None, 1.0, 2
				)
	}
	],
	sort_keys = True,
	indent = 4
)

print(j_dump)

print(json.dumps("\"foo\bar"))

print(json.dumps(u'\u1234'))

print(json.dumps('\\'))

print(json.dumps({
	"c": 0, "b": 0, "a": 0
},
	sort_keys=True,
	indent=4
))

j_load = json.loads(j_dump)
print(j_load)

print(j_load[0])
print(j_load[1]["bar"])
print(j_load[1]["bar"][0])
print(j_load[1]["bar"][1])

print(10 * '-' + 5 * '+' + "Read and parse from json file" + 5 * '+' + 10 * '-')

# open json data and load it
with open("report-1.json") as json_file:
	j_data = json.load(json_file)

# printthe duration
print("Duration: %ds %dms" % (
j_data['info']['duration'], (j_data['info']['ended'] - j_data['info']['duration'] - j_data['info']['started']) * 1000))
