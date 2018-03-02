#!/usr/bin/env python
from __future__ import print_function
if __name__ == '__main__' and __package__ is None:
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from util.common import find, file_age_in_seconds
import xml.etree.ElementTree as ET
import pprint
import requests
import random
import os

vehicles = ['APMrover2', 'ArduCopter', 'ArduPlane', 'ArduSub', 'AntennaTracker']

def get_ardupilot_url(vehicle):
    return 'http://autotest.ardupilot.org/Parameters/{0}/apm.pdef.xml'.format(vehicle)

def test_file_age(file_path, max_age):
    sec = file_age_in_seconds(file_path)
    if (sec is not None and sec <= max_age):
        return True
    else:
        return False
                    
def get_param_meta(vehicle, remote = True, force_download = False, max_age = 60*10):
    if not vehicle in vehicles:
        # TODO: inform failure
        return {}
    if remote:
        # check to see if we have a recent file from the server
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, '{0}.xml'.format(vehicle))
        if (not test_file_age(file_path, max_age) or force_download):
            url = get_ardupilot_url(vehicle)
            tree = download_param_meta(url)
            
            if tree is not None:
                save_param_meta(tree, vehicle)
            else:
                # request for meta failed, try to fall back to saved file
                # TODO: inform user
                tree = load_param_meta(vehicle)
        else:
            tree = load_param_meta(vehicle)
        return extract_param_meta_from_tree(tree, vehicle)
    else:
        # TODO: generate param meta from ardupilot code base
        return extract_param_meta_from_tree(None, vehicle)
        
def save_param_meta(tree, file_name, dir_path = None):
    if tree is None:
        return False
    if not dir_path:
        dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, '{0}.xml'.format(file_name))
    param_meta_data = ET.tostring(tree)
    print('Saving meta to {0}'.format(file_path))
    with open(file_path, 'w') as fid:
        fid.write(param_meta_data)
    
def download_param_meta(url):
    print('Downloading meta from {0}'.format(url))
    tree = None
    try:
        response = requests.get(url)
        tree = ET.fromstring(response.content)
    except requests.exceptions.ConnectionError as e:
        print('Could not retreive param meta data from remote server: {0} {1}'.format(url, e))
    finally:
        return tree
        
def load_param_meta(file_name, dir_path = None):
    tree = None
    if not dir_path:
        dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, '{0}.xml'.format(file_name))
    print('Loading meta from {0}'.format(file_path))
    try:
        with open(file_path, 'rt') as f:
            tree = ET.parse(f)
        return tree
    except IOError as e:
        print('An error occurred while loading meta from {0} {1}'.format(file_path, e))
        return None
        
def extract_param_meta_from_tree(tree, vehicle):
    if tree is None:
        print('Error: No valid tree')
        return {}
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

def download_and_save_all_param_meta():
    for vehicle in vehicles:
        url = get_ardupilot_url(vehicle)
        tree = download_param_meta(url)
        save_param_meta(tree, file_name = vehicle)
    
if __name__ == '__main__':
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    
    vehicle = random.choice(vehicles)
    print(vehicle)
    meta = get_param_meta(vehicle, remote = True)
    # print(meta)
    # download_and_save_all_param_meta()