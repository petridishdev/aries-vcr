#!/usr/bin/python3

import csv
import json
import os
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
            queries[tag] = {'desc': desc, 'queries': [], 'entries': {}}
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
    return k in ('create_timestamp', 'update_timestamp', 'last_updated', 'effective_date', 'first_effective_date', 'last_effective_date', 'revoked_date')


def has_timestamp_value(k, v):
    return ((k == 'type') and v in ('registration_date', 'entity_name_effective', 'entity_name_assumed_effective', 'entity_status_effective', 'relationship_status_effective'))


if __name__ == "__main__":
    with open('local-corp-test-sample-corps.csv') as csvfile:
        reader = csv.reader(csvfile)
        populate_queries(csvfile)

    # Entity Type
    for query in queries['entity_type']['queries']:
        params = query.split(',')
        source_id = params[0].strip()
        type = params[1].strip()
        entry = {
            'url': f'http://localhost:8081/api/v3/topic/{type}/{source_id}',
        }
        r = requests.get(entry['url'])
        res = r.json()
        remove_dates(res)

        entry['result'] = res
        entry['result_str'] = json.dumps(res)
        queries['entity_type']['entries'][source_id] = entry

    # Topic/Credential
    for query in queries['credential']['queries']:
        params = query.split(',')
        source_id = params[0].strip()
        type = params[1].strip()
        id = params[2].strip()
        entry = {
            'url': f'http://localhost:8081/api/topic/{id}/credentialset',
        }
        r = requests.get(entry['url'])
        res = r.json()
        remove_dates(res)

        entry['result'] = res
        entry['result_str'] = json.dumps(res)
        queries['credential']['entries'][source_id] = entry

    write_path = 'local-corp-test-sample-corps.json'
    if not os.path.exists(write_path):
        open(write_path, 'w').close()

    with open(write_path, 'r+') as jsonfile:
        res = jsonfile.read()
        if res == '':
            jsonfile.write(json.dumps(queries))
        else:
            changes = {}
            known = json.loads(res)
            for cat in ('entity_type', 'credential'):
                for k, v in queries[cat]['entries'].items():
                    curr = v['result_str']
                    prev = known[cat]['entries'][k]['result_str']
                    if curr != prev:
                        if cat not in changes:
                            changes[cat] = {}
                        changes[cat][k] = {
                            'curr': curr,
                            'prev': prev
                        }

            if (len(changes.keys())):
                print('The API has changed')
                with open('local-corp-test-sample-corps.changes.json', 'w+') as jsonchangefile:
                    jsonchangefile.write(json.dumps(changes))
