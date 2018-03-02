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

def extract_text(label, node, curr_param_dict):
    curr_param_dict[label] = node.text.strip()
    return curr_param_dict


def extract_param_meta_from_tree(tree, vehicle):
    if tree is None:
        print('Error: No valid tree')
        return {}
    root = {}
    curr_param_dict = {}
    curr_group_name = ''
    curr_param_name = ''
    curr_name = ''
    
    
    groups = tree.findall('./group')
    for group in groups:
        for sub in group.iter():
            # the first element is the group tag itself
            if sub.tag == 'group':
                if curr_param_dict: # we have already populated curr_param_dict, write it to the root and reset
                    # this is not run on the first loop
                    root[curr_param_dict['name'] = curr_param_dict
                    curr_param_dict = {} # reset the param dict
                curr_group_name = sub.attrib['name'] # we enforce that there is a group name
            elif sub.tag == 'parameter':
                curr_param_dict = {'default_value':sub.attrib.get('default', None), 'name':sub.attrib.get('name', None),
                                   'type':sub.attrib.get('type', None), 'group':curr_group_name,
                                   'boolean':False, 'reboot_required':None, 'values':{}
                }
            elif sub.tag in ['short_desc', 'long_desc', 'unit', 'decimal', 'min', 'max', 'reboot_required']:
                curr_param_dict = extract_text(sub.tag, sub, curr_param_dict)
            elif sub.tag == 'value':
                curr_param_dict['values'][sub.attrib['code'].strip()]=sub.text.strip()
            else:
                # TODO sort out bitmask
                pass
        print(curr_param_dict)
        
    pprint.pprint(root)

if __name__ == '__main__':
    from os import sys, path
    sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
    
    
    tree = load_param_meta('parameters')
    meta = extract_param_meta_from_tree(tree, 'test')
    print(meta)