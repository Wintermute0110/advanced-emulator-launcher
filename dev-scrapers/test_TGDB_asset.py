#!/usr/bin/python3 -B
# -*- coding: utf-8 -*-

# Test AEL TheGamesDB asset scraper.
# Super Mario World for SNES have titlescreen https://thegamesdb.net/game.php?id=136

# --- Import AEL modules ---
import os
import sys
if __name__ == "__main__" and __package__ is None:
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    print('Adding to sys.path {}'.format(path))
    sys.path.append(path)
import resources.const as const
import resources.log as log
import resources.utils as utils
import resources.kodi as kodi
import resources.scrap as scrap
import common

# --- Python standard library ---
import pprint

# --- main ---------------------------------------------------------------------------------------
print('\n*** Fetching candidate game list ******************************************************')
log.set_log_level(log.LOG_DEBUG)
st = kodi.new_status_dic()

# --- Create scraper object ---
scraper = scrap.TheGamesDB(common.settings)
scraper.set_verbose_mode(False)
scraper.set_debug_file_dump(True, os.path.join(os.path.dirname(__file__), 'assets'))

# --- Choose data for testing ---
# search_term, rombase, platform = common.games['metroid']
search_term, rombase, platform = common.games['mworld']
# search_term, rombase, platform = common.games['sonic_megadrive']
# search_term, rombase, platform = common.games['sonic_genesis'] # Aliased platform
# search_term, rombase, platform = common.games['chakan']
# search_term, rombase, platform = common.games['console_wrong_title']
# search_term, rombase, platform = common.games['console_wrong_platform']
# search_term, rombase, platform = common.games['bforever']
# search_term, rombase, platform = common.games['bforever_snes']

# --- Get candidates, print them and set first candidate ---
rom_FN = utils.FileName(rombase)
rom_checksums_FN = utils.FileName(rombase)
if scraper.check_candidates_cache(rom_FN, platform):
    print('>>> Game "{}" "{}" in disk cache.'.format(rom_FN.getBase(), platform))
else:
    print('>>> Game "{}" "{}" not in disk cache.'.format(rom_FN.getBase(), platform))
candidate_list = scraper.get_candidates(search_term, rom_FN, rom_checksums_FN, platform, st)
# pprint.pprint(candidate_list)
common.handle_get_candidates(candidate_list, st)
common.print_candidate_list(candidate_list)
scraper.set_candidate(rom_FN, platform, candidate_list[0])

# --- Print list of assets found -----------------------------------------------------------------
print('\n*** Fetching game assets **************************************************************')
# --- Get all assets (TGBD scraper custom function) ---
# assets = scraper.get_assets_all(candidate)
# pprint.pprint(assets)
# common.print_game_assets(assets)

common.print_game_assets(scraper.get_assets(const.ASSET_FANART_ID, st))
# common.print_game_assets(scraper.get_assets(const.ASSET_BANNER_ID, st))
# common.print_game_assets(scraper.get_assets(const.ASSET_CLEARLOGO_ID, st))
# common.print_game_assets(scraper.get_assets(const.ASSET_TITLE_ID, st))
# common.print_game_assets(scraper.get_assets(const.ASSET_SNAP_ID, st))
common.print_game_assets(scraper.get_assets(const.ASSET_BOXFRONT_ID, st))
# common.print_game_assets(scraper.get_assets(const.ASSET_BOXBACK_ID, st))

# --- Flush scraper disk cache -------------------------------------------------------------------
scraper.flush_disk_cache()
