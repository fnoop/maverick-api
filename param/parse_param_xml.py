#!/usr/bin/env python
from __future__ import print_function
import xml.etree.ElementTree as ET
import pprint
import requests
import random

def find(key, dictionary):
    '''Find all occurences of a key in nested python dictionaries and lists'''
    # https://stackoverflow.com/questions/9807634/find-all-occurrences-of-a-key-in-nested-python-dictionaries-and-lists
    for k, v in dictionary.iteritems():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find(key, d):
                    yield result
                    
vehicles = ['APMrover2', 'ArduCopter', 'ArduPlane', 'ArduSub', 'AntennaTracker']
vehicle = random.choice(vehicles)
print(vehicle)
url = 'http://autotest.ardupilot.org/Parameters/{0}/apm.pdef.xml'.format(vehicle)
response = requests.get(url)
tree = ET.fromstring(response.content)

# with open('apm.pdef.xml', 'rt') as f:
#     tree = ET.parse(f)

root = {}
curr_param_dict = {}
curr_param_name = ''
curr_name = ''

# find both the vehicles and libraries parameters
nodes = tree.findall('.//parameters')
for node in nodes:
    for sub in node.iter():
        if sub.tag == 'parameters':
            if curr_param_dict: # we have already populated curr_param_dict, write it to the root and reset
                # this is not run on the first loop
                root[curr_name][curr_param_name] = curr_param_dict
                curr_param_dict = {}
            curr_name = str(sub.attrib['name'])
            root[curr_name] = {}
        elif sub.tag == 'param':
            if curr_param_dict: # we have already populated curr_param_dict, write it to the root and reset
                # this is not run on the first loop
                root[curr_name][curr_param_name] = curr_param_dict
                curr_param_dict = {}
            curr_param_name = sub.attrib['name']
            if vehicle in curr_param_name:
                # remove un needed vehicle name if present
                curr_param_name = curr_param_name.lstrip(vehicle).lstrip(':')
            curr_param_dict = {'humanName':sub.attrib.get('humanName', None),
            'user':sub.attrib.get('user', None), 'fields':{}, 'values':{}, 'documentation':sub.attrib.get('documentation', None)}
        elif sub.tag == 'field':
            curr_param_dict['fields'][sub.attrib['name']]=sub.text
        elif sub.tag == 'value':
            curr_param_dict['values'][sub.attrib['code']]=sub.text
        else:
            pass
            # print sub.tag, sub.attrib, sub.text
            
if curr_param_dict: # we have unwritten param data, write it to the root 
    root[curr_name][curr_param_name] = curr_param_dict
    
# pprint.pprint(root)

all_params = []
for param_group in root:
    # print(param_group)
    all_params.extend(root[param_group].keys())

print('')
print(all_params)
print('')

# randomly select a parameter and print its content
param = random.choice(all_params)
print(param, list(find(param, root)))