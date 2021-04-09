#!/usr/bin/python3 -B

import sys, json, config

for file in sys.argv[1:]:
    try:
        if file.lower().endswith('.json'):
            continue
        if not file.lower().endswith('.xml'):
            raise Exception('Not an xml file')

        r = config.parse_xml_file(file)
        s = json.dumps(r, default=lambda o: o.to_json(), indent=1)
        s = s.replace('\n  ', '\n\t')

        json_file = file[0:-4] + '.json'
        with open(json_file, 'w') as fh:
            fh.write(s)

    except Exception as e:
        print(file, e, file=sys.stderr)


