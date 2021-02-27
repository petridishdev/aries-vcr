#!/usr/bin/python3

import csv
import json
import pip._vendor.requests as requests

queries = {}


def parse_comment(rowstr):
    """
    Gets the test tag and query description from the comment line
    """
    tag, desc = '', ''
    if rowstr.startswith('#'):
        for entry in rowstr.split('#'):
            entry = entry.strip()
            if entry and 'TAG' in entry:
                tag = entry.split(':')[1]
                queries[tag] = {}
            elif entry != '':
                desc = entry
    return tag, desc


def populate_queries(csvfile):
    """
    Generates a dictionary of test tags, query description and query list for each test
    """
    last = ''
    for row in reader:
        rowstr = ', '.join(row)
        tag, desc = parse_comment(rowstr)
        if (tag != '' and desc != ''):
            last = tag
            queries[tag] = {'desc': desc, 'queries': [], 'entries': []}
            continue
        queries[last]['queries'].append(rowstr)


def remove_dates(obj):
    """
    Recursively removes dates from the result
    """
    if (not obj):
        return
    if isinstance(obj, list):
        for subobj in obj:
            remove_dates(subobj)
    else:
        for k, v in obj.copy().items():
            if isinstance(v, object) and not isinstance(v, (int, str, bool)):
                remove_dates(v)
            else:
                if (has_timestamp_key(k)):
                    obj.pop(k)
                if (has_timestamp_value(k, v)):
                    obj.pop('value')


def has_timestamp_key(k):
    return k in ('create_timestamp', 'update_timestamp', 'last_updated')


def has_timestamp_value(k, v):
    return ((k == 'type') and v in ('registration_date', 'entity_name_effective', 'entity_name_assumed_effective', 'entity_status_effective', 'relationship_status_effective'))


if __name__ == "__main__":
    with open('local-corp-test-sample-corps.csv') as csvfile:
        reader = csv.reader(csvfile)
        populate_queries(csvfile)

    for query in queries['entity_type']['queries']:
        params = query.split(',')
        source_id = params[0].strip()
        type = params[1].strip()
        entry = {
            'url': f'http://localhost:8081/api/topic/ident/{type}/{source_id}/formatted',
        }
        r = requests.get(entry['url'])
        res = r.json()
        remove_dates(res)

        entry['result'] = res
        entry['result_str'] = json.dumps(res)
        queries['entity_type']['entries'].append(entry)

    with open('local-corp-test-sample-corps.json', 'w') as jsonfile:
        jsonfile.write(json.dumps(queries))
