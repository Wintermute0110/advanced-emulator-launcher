#!/usr/bin/python
# -*- coding: utf-8 -*-

# Test AEL GameFAQs metadata scraper.
#
# --- GameGAQs test URLs ---
# https://gamefaqs.gamespot.com/snes/519824-super-mario-world
# https://gamefaqs.gamespot.com/snes/588741-super-metroid
# https://gamefaqs.gamespot.com/snes/588699-street-fighter-alpha-2
# https://gamefaqs.gamespot.com/genesis/454495-sonic-the-hedgehog

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
import common

# --- main ---------------------------------------------------------------------------------------
print('*** Fetching candidate game list ********************************************************')
set_log_level(LOG_DEBUG)

# --- Create scraper object ---
scraper_obj = GameFAQs(common.settings)
scraper_obj.set_verbose_mode(False)
scraper_obj.set_debug_file_dump(True, os.path.join(os.path.dirname(__file__), 'assets'))
status_dic = kodi_new_status_dic('Scraper test was OK')

# --- Get candidates non-MAME ---
# candidate_list = scraper_obj.get_candidates(*common.games['metroid'], status_dic = status_dic)
candidate_list = scraper_obj.get_candidates(*common.games['mworld'], status_dic = status_dic)
# candidate_list = scraper_obj.get_candidates(*common.games['sonic'], status_dic = status_dic)
# candidate_list = scraper_obj.get_candidates(*common.games['chakan'], status_dic = status_dic)
# candidate_list = scraper_obj.get_candidates(*common.games['console_invalid'], status_dic = status_dic)

# --- Print search results ---
common.handle_get_candidates(candidate_list)
# pprint.pprint(candidate_list)
print_candidate_list(candidate_list)
candidate = candidate_list[0]

# --- Print metadata of first candidate ----------------------------------------------------------
print('*** Fetching game metadata **************************************************************')
metadata = scraper_obj.get_metadata(candidate, status_dic)
# pprint.pprint(metadata)
print_game_metadata(metadata)
