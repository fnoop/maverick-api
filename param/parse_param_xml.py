#!/usr/bin/env python
from __future__ import print_function
import xml.etree.ElementTree as ET
import pprint
import requests
import random

vehicles = ['APMrover2', 'ArduCopter', 'ArduPlane', 'ArduSub', 'AntennaTracker']

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
                    
def get_param_meta(vehicle, remote = True):
    if not vehicle in vehicles:
        return False
    
    if remote:
        url = 'http://autotest.ardupilot.org/Parameters/{0}/apm.pdef.xml'.format(vehicle)
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError as e:
            print('Could not retreive param meta data from remote server: {0} {1}'.format(url, e))
            # TODO: fall back to previous saved version(s)
            return {}
        tree = ET.fromstring(response.content)
    else:
        # TODO: fix this
        return False
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
                curr_param_dict['fields'][sub.attrib['name'].strip()]=sub.text.strip()
            elif sub.tag == 'value':
                curr_param_dict['values'][sub.attrib['code'].strip()]=sub.text.strip()
            else:
                pass
                # print sub.tag, sub.attrib, sub.text
                
    if curr_param_dict: # we have unwritten param data, write it to the root 
        root[curr_name][curr_param_name] = curr_param_dict
        
    # pprint.pprint(root)
    
    meta = {}
    for param_group in root:
        for param in root[param_group].keys():
            param_meta = root[param_group][param]
            # dont use param_group here in order to avoid vehicle name as group
            param_meta['group'] = param.split('_')[0].strip().rstrip('_').upper()
            if not param_meta['values']:
                # its empty, set to none
                param_meta['values'] = None
            if not param_meta['fields']:
                # its empty, set to none
                param_meta['fields'] = None
                
            meta[param] = param_meta
            
            
    return meta
    
if __name__ == '__main__':
    vehicle = random.choice(vehicles)
    print(vehicle)
    meta = get_param_meta(vehicle, remote = True)
    print(meta)
    