#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Get all TGDB platform IDs.
#

# --- Python standard library ---
from __future__ import unicode_literals
import os
import pprint
import sys

# --- AEL modules ---
if __name__ == "__main__" and __package__ is None:
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    print('Adding to sys.path {0}'.format(path))
    sys.path.append(path)
from resources.scrap import *
from resources.utils import *

# --- main ----------------------------------------------------------------------------------------
 # >> LOG_INFO, LOG_VERB, LOG_DEBUG
set_log_level(LOG_INFO)

# --- Create scraper object ---
settings = {
    # Make sure this is the Public key.
    'scraper_thegamesdb_apikey' : '828be1fb8f3182d055f1aed1f7d4da8bd4ebc160c3260eae8ee57ea823b42415',
}
scraper_obj = TheGamesDB(settings)
scraper_obj.set_verbose_mode(False)
scraper_obj.set_debug_file_dump(True, os.path.join(os.path.dirname(__file__), 'assets'))

# --- Get platforms ---
# platform_dic = {
# "status" : "Success", 
# "code" : 200, 
# "data" : {
#  "count" : 109, 
#  "platforms" : {
#   "24" : {
#    "alias" : "neogeo", 
#    "id" : 24, 
#    "name" : "Neo Geo"
#   },
online_data = scraper_obj.get_platforms()
platforms_dic = online_data['data']['platforms']
# pprint.pprint(platforms_dic)
pname_dic = {platforms_dic[platform]['name'] : platform for platform in platforms_dic}

# --- Print list ---
table_str = [
    ['left', 'left', 'left'],
    ['ID', 'Name', 'Short name'],
]
for pname in sorted(pname_dic, reverse = False):
    platform = platforms_dic[pname_dic[pname]]
    # print('{0} {1} {2}'.format(platform['id'], platform['name'], platform['alias']))
    try:
        table_str.append([
            unicode(platform['id']),
            unicode(platform['name']),
            unicode(platform['alias'])
        ])
    except UnicodeEncodeError as ex:
        print('Exception UnicodeEncodeError')
        print('ID {0}'.format(platform['id']))
        sys.exit(0)
table_str_list = text_render_table_str(table_str)
print('\n'.join(table_str_list))
