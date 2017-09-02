# -*- coding: utf-8 -*-
#
# Advanced Emulator Launcher
#

# Copyright (c) 2016-2017 Wintermute0110 <wintermute0110@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# --- Python standard library ---
from __future__ import unicode_literals
import xml.etree.ElementTree as ET

# --- Modules/packages in this plugin ---
from utils import *
from utils_kodi import *

# -------------------------------------------------------------------------------------------------
# Data structures
# -------------------------------------------------------------------------------------------------
# DTD "http://www.logiqx.com/Dats/datafile.dtd"
def audit_new_rom_logiqx(): 
    rom = {
        'name'         : '',
        'cloneof'      : '',
        'year'         : '',
        'manufacturer' : ''
    }

    return rom

# HyperList doesn't include Plot
def audit_new_rom_HyperList(): 
    rom = {
        'name'         : '',
        'description'  : '',
        'cloneof'      : '',
        'crc'          : '',
        'manufacturer' : '',
        'year'         : '',
        'genre'        : '',
        'rating'       : '',
        'enabled'      : ''
    }

    return rom

def audit_new_rom_GameDB():
    rom = {
        'name'         : '',
        'description'  : '',
        'year'         : '',
        'rating'       : '',
        'manufacturer' : '',
        'genre'        : '',
        'player'       : '',
        'story'        : ''
    }

    return rom

# Manufacturer is Publisher
def audit_new_rom_AEL_Offline(): 
    rom = {
        'name'         : '',
        'description'  : '',
        'cloneof'      : '',
        'source'       : '',
        'status'       : '',
        'year'         : '',
        'genre'        : '',
        'manufacturer' : '',
        'nplayers'     : '',
        'rating'       : '',
        'plot'         : ''
    }

    return rom

def audit_new_LB_game():
    g = {
        'Name'              : '',
        'ReleaseYear'       : '',
        'Overview'          : '',
        'MaxPlayers'        : '',
        'Cooperative'       : '',
        'VideoURL'          : '',
        'DatabaseID'        : '',
        'CommunityRating'   : '',
        'Platform'          : '',
        'Genres'            : '',
        'Publisher'         : '',
        'Developer'         : '',
        'ReleaseDate'       : '',
        'ESRB'              : '',
        'WikipediaURL'      : '',
        'DOS'               : '',
        'StartupFile'       : '',
        'StartupMD5'        : '',
        'SetupFile'         : '',
        'SetupMD5'          : '',
        'StartupParameters' : '',
    }

    return g

def audit_new_LB_platform():
    g = {
        'Name'           : '',
        'Emulated'       : '',
        'ReleaseDate'    : '',
        'Developer'      : '',
        'Manufacturer'   : '',
        'Cpu'            : '',
        'Memory'         : '',
        'Graphics'       : '',
        'Sound'          : '',
        'Display'        : '',
        'Media'          : '',
        'MaxControllers' : '',
        'Notes'          : '',
        'Category'       : '',
        'UseMameFiles'   : '',
    }

    return g

def audit_new_LB_gameImage():
    g = {
        'DatabaseID' : '',
        'FileName'   : '',
        'Type'       : '',
        'CRC32'      : '',
        'Region'     : '',
    }

    return g

def audit_load_LB_metadata_XML(filename_FN, games_dic, platforms_dic, gameimages_dic):
    if not filename_FN.exists():
        log_error("Cannot load file '{0}'".format(xml_file.getOriginalPath()))
        return

    # --- Parse using cElementTree ---
    log_verb('audit_load_LB_metadata_XML() Loading "{0}"'.format(filename_FN.getPath()))
    try:
        xml_root = filename_FN.readXml()
    except ET.ParseError, e:
        log_error('(ParseError) Exception parsing XML categories.xml')
        log_error('(ParseError) {0}'.format(str(e)))
        return
    for xml_element in xml_root:
        if xml_element.tag == 'Game':
            game = audit_new_LB_game()
            for xml_child in xml_element:
                xml_tag  = xml_child.tag
                xml_text = xml_child.text if xml_child.text is not None else ''
                if xml_tag not in game:
                    log_info('Unknown <Game> child tag <{0}>'.format(xml_tag))
                    return
                game[xml_tag] = text_unescape_XML(xml_text)
            games_dic[game['Name']] = game
        elif xml_element.tag == 'Platform':
            platform = audit_new_LB_platform()
            for xml_child in xml_element:
                xml_tag  = xml_child.tag
                xml_text = xml_child.text if xml_child.text is not None else ''
                if xml_tag not in platform:
                    log_info('Unknown <Platform> child tag <{0}>'.format(xml_tag))
                    return
                platform[xml_tag] = text_unescape_XML(xml_text)
            platforms_dic[platform['Name']] = platform
        elif xml_element.tag == 'PlatformAlternateName':
            pass
        elif xml_element.tag == 'Emulator':
            pass
        elif xml_element.tag == 'EmulatorPlatform':
            pass
        elif xml_element.tag == 'GameAlternateName':
            pass
        elif xml_element.tag == 'GameImage':
            game_image = audit_new_LB_gameImage()
            for xml_child in xml_element:
                xml_tag  = xml_child.tag
                xml_text = xml_child.text if xml_child.text is not None else ''
                if xml_tag not in game_image:
                    log_info('Unknown <GameImage> child tag <{0}>'.format(xml_tag))
                    return
                game_image[xml_tag] = text_unescape_XML(xml_text)
            gameimages_dic[game_image['FileName']] = game_image
        else:
            log_info('Unknwon main tag <{0}>'.format(xml_element.tag))
            return
    log_verb('audit_load_LB_metadata_XML() Loaded {0} games ({1} bytes)'.format(len(games_dic), sys.getsizeof(games_dic)))
    log_verb('audit_load_LB_metadata_XML() Loaded {0} platforms'.format(len(platforms_dic)))
    log_verb('audit_load_LB_metadata_XML() Loaded {0} game images'.format(len(gameimages_dic)))

# -------------------------------------------------------------------------------------------------
# Functions
# -------------------------------------------------------------------------------------------------
#
# Loads offline scraper information XML file.
#
def audit_load_OfflineScraper_XML(xml_file):
    __debug_xml_parser = 0
    games = {}

    # --- Check that file exists ---
    if not xml_file.exists():
        log_error("Cannot load file '{0}'".format(xml_file.getOriginalPath()))
        return games

    # --- Parse using cElementTree ---
    log_verb('audit_load_OfflineScraper_XML() Loading "{0}"'.format(xml_file.getOriginalPath()))
    try:
        xml_root = xml_file.readXml()
    except ET.ParseError, e:
        log_error('(ParseError) Exception parsing XML categories.xml')
        log_error('(ParseError) {0}'.format(str(e)))
        return games
    for game_element in xml_root:
        if __debug_xml_parser:
            log_debug('=== Root child tag "{0}" ==='.format(game_element.tag))

        if game_element.tag == 'game':
            # Default values
            game = audit_new_rom_logiqx()

            # ROM name is an attribute of <game>
            game['name'] = game_element.attrib['name']
            if __debug_xml_parser: log_debug('Game name = "{0}"'.format(game['name']))

            # Parse child tags of category
            for game_child in game_element:
                # By default read strings
                xml_text = game_child.text if game_child.text is not None else ''
                xml_text = text_unescape_XML(xml_text)
                xml_tag  = game_child.tag
                if __debug_xml_parser: log_debug('Tag "{0}" --> "{1}"'.format(xml_tag, xml_text))
                game[xml_tag] = xml_text
            key = game['name']
            games[key] = game

    return games

#
# Loads a No-Intro Parent-Clone XML DAT file. Creates a data structure like
# roms_nointro = {
#   'rom_name_A' : { 'name' : 'rom_name_A', 'cloneof' : '' | 'rom_name_parent},
#   'rom_name_B' : { 'name' : 'rom_name_B', 'cloneof' : '' | 'rom_name_parent},
# }
#
def audit_load_NoIntro_XML_file(xml_FN):
    nointro_roms = {}

    # --- If file does not exist return empty dictionary ---
    if not xml_FN.exists():
        log_error('Does not exists "{0}"'.format(xml_FN.getPath()))
        return nointro_roms

    # --- Parse using cElementTree ---
    log_verb('Loading XML "{0}"'.format(xml_FN.getOriginalPath()))
    try:
        xml_root = xml_FN.readXml()
    except ET.ParseError as e:
        log_error('(ParseError) Exception parsing XML categories.xml')
        log_error('(ParseError) {0}'.format(str(e)))
        return nointro_roms
    except IOError as e:
        log_error('(IOError) {0}'.format(str(e)))
        return nointro_roms
    xml_root = xml_tree.getroot()
    for root_element in xml_root:
        if root_element.tag == 'game':
            nointro_rom = audit_new_rom_logiqx()
            rom_name = root_element.attrib['name']
            nointro_rom['name'] = rom_name
            if 'cloneof' in root_element.attrib:
                nointro_rom['cloneof'] = root_element.attrib['cloneof']
            nointro_roms[rom_name] = nointro_rom

    return nointro_roms

def audit_load_GameDB_XML(xml_FN):
    __debug_xml_parser = 0
    games = {}

    # --- Check that file exists and load ---
    if not xml_FN.exists():
        log_error('Does not exists "{0}"'.format(xml_FN.getPath()))
        return games
    log_verb('Loading XML "{0}"'.format(xml_FN.getPath()))
    try:
        xml_root = xml_FN.readXml()
    except ET.ParseError as e:
        log_error('(ParseError) Exception parsing XML categories.xml')
        log_error('(ParseError) {0}'.format(str(e)))
        return games
    xml_root = xml_tree.getroot()
    for game_element in xml_root:
        if __debug_xml_parser:
            log_debug('=== Root child tag "{0}" ==='.format(game_element.tag))

        if game_element.tag == 'game':
            # Default values
            game = audit_new_rom_GameDB()

            # ROM name is an attribute of <game>
            game['name'] = game_element.attrib['name']
            if __debug_xml_parser: log_debug('Game name = "{0}"'.format(game['name']))

            # Parse child tags of category
            for game_child in game_element:
                # By default read strings
                xml_text = game_child.text if game_child.text is not None else ''
                xml_text = text_unescape_XML(xml_text)
                xml_tag  = game_child.tag
                if __debug_xml_parser: log_debug('Tag "{0}" --> "{1}"'.format(xml_tag, xml_text))
                game[xml_tag] = xml_text
            key = game['name']
            games[key] = game

    return games

def audit_load_Tempest_INI(file_FN):
    games = {}
    # Read_status FSM values
    #   0 -> Looking for '[game_name]' tag
    #   1 -> Reading fields fiel_name=field_value
    read_status = 0
    __debug_INI_parser = False

    # --- Check that file exists ---
    if not file_FN.exists():
        log_error('Does not exists "{0}"'.format(file_FN.getPath()))
        return games
    log_verb('Loading XML "{0}"'.format(file_FN.getPath()))
    try:
        f = open(file_FN.getPath(), 'rt')
    except IOError:
        log_info('audit_load_Tempest_INI() IOError opening "{0}"'.format(filename))
        return {}
    for file_line in f:
        stripped_line = file_line.strip().decode(errors = 'replace')
        if __debug_INI_parser: print('Line "' + stripped_line + '"')
        if read_status == 0:
            m = re.search(r'\[([^\]]+)\]', stripped_line)
            if m:
                game = audit_new_rom_GameDB()
                game_key     = m.group(1)
                game['name'] = m.group(1)
                if __debug_INI_parser: print('Found game [{0}]'.format(game['name']))
                read_status = 1
        elif read_status == 1:
            line_list = stripped_line.split("=")
            if len(line_list) == 1:
                read_status = 0
                games[game_key] = game
                if __debug_INI_parser: print('Added game key "{0}"'.format(game_key))
            else:
                if __debug_INI_parser: print('Line list -> ' + str(line_list))
                field_name = line_list[0]
                field_value = line_list[1]
                if   field_name == 'Publisher':   game['manufacturer'] = field_value
                elif field_name == 'Developer':   game['dev'] = field_value
                elif field_name == 'Released':    game['year'] = field_value
                elif field_name == 'Systems':     pass
                elif field_name == 'Genre':       game['genre'] = field_value
                elif field_name == 'Perspective': pass
                elif field_name == 'Score':       game['score'] = field_value
                elif field_name == 'Controls':    pass
                elif field_name == 'Players':     game['player'] = field_value
                elif field_name == 'Esrb':        game['rating'] = field_value
                elif field_name == 'Url':         pass
                elif field_name == 'Description': game['story'] = field_value
                elif field_name == 'Goodname':    pass
                elif field_name == 'NoIntro':     pass
                elif field_name == 'Tosec':       pass
                else:
                    raise NameError
        else:
            raise CriticalError('Unknown read_status FSM value')
    f.close()
    log_info('audit_load_Tempest_INI() Number of games {0}'.format(len(games)))

    return games

def audit_load_HyperList_XML(xml_FN):
    __debug_xml_parser = 0
    games = {}

    # --- Check that file exists and load ---
    if not xml_FN.exists():
        log_error('Does not exists "{0}"'.format(xml_FN.getPath()))
        return games
    log_verb('Loading XML "{0}"'.format(xml_FN.getPath()))
    try:
        xml_root = xml_FN.readXml()
    except ET.ParseError as e:
        log_error('(ParseError) Exception parsing XML categories.xml')
        log_error('(ParseError) {0}'.format(str(e)))
        return games
    except IOError as e:
        log_error('(IOError) {0}'.format(str(e)))
        return games
    for game_element in xml_root:
        if __debug_xml_parser:
            log_debug('=== Root child tag "{0}" ==='.format(game_element.tag))

        if game_element.tag == 'game':
            # Default values
            game = audit_new_rom_HyperList()

            # ROM name is an attribute of <game>
            game['name'] = game_element.attrib['name']
            if __debug_xml_parser: log_debug('Game name = "{0}"'.format(game['name']))

            # Parse child tags of category
            for game_child in game_element:
                # By default read strings
                xml_text = game_child.text if game_child.text is not None else ''
                xml_text = text_unescape_XML(xml_text)
                xml_tag  = game_child.tag
                if __debug_xml_parser: log_debug('Tag "{0}" --> "{1}"'.format(xml_tag, xml_text))
                game[xml_tag] = xml_text
            key = game['name']
            games[key] = game

    return games

def audit_make_NoIntro_PClone_dic(nointro_dic):
    log_info('Making PClone dictionary ...')
    main_pclone_dic = {}
    for machine_name in nointro_dic:
        machine = nointro_dic[machine_name]
        if machine['cloneof']:
            parent_name = machine['cloneof']
            # >> If parent already in main_pclone_dic then add clone to parent list.
            # >> If parent not there, then add parent first and then add clone.
            if parent_name not in main_pclone_dic: main_pclone_dic[parent_name] = []
            main_pclone_dic[parent_name].append(machine_name)
        else:
            # >> Machine is a parent. Add to main_pclone_dic if not already there.
            if machine_name not in main_pclone_dic: main_pclone_dic[machine_name] = []

    return main_pclone_dic

def audit_make_NoIntro_Parents_dic(nointro_dic):
    log_info('Making Parents dictionary ...')
    main_pclone_dic = {}
    main_clone_to_parent_dic = {}
    for machine_name in nointro_dic:
        machine = nointro_dic[machine_name]
        if machine['cloneof']:
            parent_name = machine['cloneof']
            main_clone_to_parent_dic[machine_name] = parent_name            

    return main_clone_to_parent_dic

# -------------------------------------------------------------------------------------------------
# Retroarch System directory BIOS audit
# -------------------------------------------------------------------------------------------------
Retro_core_dic = {
    'atari800'  : 'Atari800',
    'prosystem' : 'ProSystem',
}

# See https://github.com/libretro/libretro-database/blob/master/dat/BIOS.dat
# See https://github.com/libretro/libretro-database/blob/master/dat/BIOS%20-%20Non-Merged.dat
Libretro_BIOS_list = [
    # --- Atari 5200 ---
    {'filename' : '5200.rom', 'size' : 2048, 'md5': '281f20ea4320404ec820fb7ec0693b38',
     'mandatory' : True, 'cores' : ['atari800']},

    # --- Atari 7800 ---
    {'filename' : '7800 BIOS (E).rom', 'size' : 16384, 'md5': '397bb566584be7b9764e7a68974c4263',
     'mandatory' : True, 'cores' : ['prosystem']},
    {'filename' : '7800 BIOS (U).rom', 'size' : 4096, 'md5': '0763f1ffb006ddbe32e52d497ee848ae',
     'mandatory' : True, 'cores' : ['prosystem']},

    # --- Atari Lynx ---
    {'filename' : 'lynxboot.img', 'size' : 512, 'md5': 'fcd403db69f54290b51035d82f835e7b',
     'mandatory' : True, 'cores' : ['mednafen_lynx', 'handy']},

    # --- Atari ST ---
    

    # --- Id Software - Doom ---
    

    # --- Magnavox - Odyssey2 ---
    {'filename' : 'o2rom.bin', 'size' : 1024, 'md5': '562d5ebf9e030a40d6fabfc2f33139fd',
     'mandatory' : True, 'cores' : ['o2em']},

    # --- Microsoft - MSX ---
    # https://github.com/libretro/libretro-super/blob/master/dist/info/fmsx_libretro.info
    {'filename' : 'MSX.ROM', 'size' : 32768, 'md5': 'aa95aea2563cd5ec0a0919b44cc17d47',
     'mandatory' : True, 'cores' : ['fmsx']},
    {'filename' : 'MSX2.ROM', 'size' : 32768, 'md5': 'ec3a01c91f24fbddcbcab0ad301bc9ef',
     'mandatory' : True, 'cores' : ['fmsx']},
    {'filename' : 'MSX2EXT.ROM', 'size' : 16384, 'md5': '2183c2aff17cf4297bdb496de78c2e8a',
     'mandatory' : True, 'cores' : ['fmsx']},
    {'filename' : 'MSX2P.ROM', 'size' : 32768, 'md5': '6d8c0ca64e726c82a4b726e9b01cdf1e',
     'mandatory' : True, 'cores' : ['fmsx']},
    {'filename' : 'MSX2PEXT.ROM', 'size' : 16384, 'md5': '7c8243c71d8f143b2531f01afa6a05dc',
     'mandatory' : True, 'cores' : ['fmsx']},

    # --- NEC - PC Engine and Supergrafx ---
    {'filename' : 'syscard3.pce', 'size' : 262144, 'md5': '38179df8f4ac870017db21ebcbf53114',
     'mandatory' : True, 'cores' : ['mednafen_pce_fast', 'mednafen_supergrafx']},

    {'filename' : 'gecard.pce', 'size' : 32768, 'md5': '6d2cb14fc3e1f65ceb135633d1694122',
     'mandatory' : True, 'cores' : [ ]},

    # --- NEC - PC-FX ---
    # https://github.com/libretro/libretro-super/blob/master/dist/info/mednafen_pcfx_libretro.info
    {'filename' : 'pcfx.rom', 'size' : 1048576, 'md5': '08e36edbea28a017f79f8d4f7ff9b6d7',
     'mandatory' : True, 'cores' : ['mednafen_pcfx']},
    {'filename' : 'fx-scsi.rom', 'size' : 524288, 'md5': '430e9745f9235c515bc8e652d6ca3004',
     'mandatory' : True, 'cores' : [ ]},
    {'filename' : 'pcfxbios.bin', 'size' : 1048576, 'md5': '08e36edbea28a017f79f8d4f7ff9b6d7',
     'mandatory' : True, 'cores' : [ ]},
    {'filename' : 'pcfxv101.bin', 'size' : 1048576, 'md5': 'e2fb7c7220e3a7838c2dd7e401a7f3d8',
     'mandatory' : True, 'cores' : [ ]},
    {'filename' : 'pcfxga.rom', 'size' : 1048576, 'md5': '5885bc9a64bf80d4530b9b9b978ff587',
     'mandatory' : True, 'cores' : [ ]},

    # --- Nintendo - Famicom Disk System ---
    # https://github.com/libretro/libretro-super/blob/master/dist/info/fceumm_libretro.info
    # https://github.com/libretro/libretro-super/blob/master/dist/info/nestopia_libretro.info
    {'filename' : 'disksys.rom', 'size' : 8192, 'md5': 'ca30b50f880eb660a320674ed365ef7a',
     'mandatory' : True, 'cores' : ['fceumm', 'nestopia']},

    # --- Nintendo - Gameboy ---
    
    # --- Nintendo - Game Boy Advance ---
    
    # --- Nintendo - Gameboy Color ---
    
    # --- Nintendo - GameCube ---
    {'filename' : 'gc-ntsc-10.bin', 'size' : 2097152 , 'md5': 'fc924a7c879b661abc37cec4f018fdf3',
     'mandatory' : True, 'cores' : []},
    {'filename' : 'gc-pal-10.bin', 'size' : 2097152 , 'md5': '0cdda509e2da83c85bfe423dd87346cc',
     'mandatory' : True, 'cores' : []},
    {'filename' : 'gc-pal-12.bin', 'size' : 2097152 , 'md5': 'db92574caab77a7ec99d4605fd6f2450',
     'mandatory' : True, 'cores' : []},
    {'filename' : 'gc-dvd-20010608.bin', 'size' : 131072 , 'md5': '561532ad496f644897952d2cef5bb431',
     'mandatory' : True, 'cores' : []},
    {'filename' : 'gc-dvd-20010831.bin', 'size' : 131072 , 'md5': 'b953eb1a8fc9922b3f7051c1cdc451f1',
     'mandatory' : True, 'cores' : []},
    {'filename' : 'gc-dvd-20020402.bin', 'size' : 131072 , 'md5': '413154dd0e2c824c9b18b807fd03ec4e',
     'mandatory' : True, 'cores' : []},
    {'filename' : 'gc-dvd-20020823.bin', 'size' : 131072 , 'md5': 'c03f6bbaf644eb9b3ee261dbe199eb42',
     'mandatory' : True, 'cores' : []},

    # --- Nintendo - Nintendo 64DD ---
    {'filename' : '64DD_IPL.bin', 'size' : 4194304, 'md5': '8d3d9f294b6e174bc7b1d2fd1c727530',
     'mandatory' : True, 'cores' : ['parallel']},

    # --- Nintendo - Nintendo DS ---
    {'filename' : 'bios7.bin', 'size' : 16384, 'md5': 'df692a80a5b1bc90728bc3dfc76cd948',
     'mandatory' : True, 'cores' : []},
    {'filename' : 'bios9.bin', 'size' : 4096, 'md5': 'a392174eb3e572fed6447e956bde4b25',
     'mandatory' : True, 'cores' : []},
    {'filename' : 'firmware.bin', 'size' : 262144, 'md5': 'e45033d9b0fa6b0de071292bba7c9d13',
     'mandatory' : True, 'cores' : []},

    # --- Nintendo - Nintendo Entertainment System ---
    

    # --- Nintendo - Pokemon Mini ---
    # https://github.com/libretro/libretro-super/blob/master/dist/info/pokemini_libretro.info
    {'filename' : 'bios.min', 'size' : 4096, 'md5': '1e4fb124a3a886865acb574f388c803d',
     'mandatory' : True, 'cores' : ['pokemini']},

    # --- Nintendo - Super Nintendo Entertainment System ---
    

    # --- Phillips - Videopac+ ---
    {'filename' : 'c52.bin', 'size' : 1024, 'md5': 'f1071cdb0b6b10dde94d3bc8a6146387',
     'mandatory' : True, 'cores' : []},
    {'filename' : 'g7400.bin', 'size' : 1024, 'md5': 'c500ff71236068e0dc0d0603d265ae76',
     'mandatory' : True, 'cores' : []},
    {'filename' : 'jopac.bin', 'size' : 1024, 'md5': '279008e4a0db2dc5f1c048853b033828',
     'mandatory' : True, 'cores' : []},

    # --- Sega - Dreamcast ---
    # https://github.com/libretro/libretro-super/blob/master/dist/info/reicast_libretro.info
    # https://github.com/libretro/libretro-super/blob/master/dist/info/redream_libretro.info
    {'filename' : 'dc/dc_boot.bin', 'size' : 2097152, 'md5': 'e10c53c2f8b90bab96ead2d368858623',
     'mandatory' : True, 'cores' : ['reicast', 'redream']},
    {'filename' : 'dc/dc_flash.bin', 'size' : 131072, 'md5': '0a93f7940c455905bea6e392dfde92a4',
     'mandatory' : True, 'cores' : ['reicast', 'redream']},

    # --- Sega - Mega Drive - Genesis ---
    # https://github.com/libretro/libretro-super/blob/master/dist/info/genesis_plus_gx_libretro.info
    {'filename' : 'areplay.bin', 'size' : 32768, 'md5': 'a0028b3043f9d59ceeb03da5b073b30d',
     'mandatory' : False, 'cores' : ['genesis_plus_gx']},
    {'filename' : 'bios.gg', 'size' : 1024, 'md5': '672e104c3be3a238301aceffc3b23fd6',
     'mandatory' : False, 'cores' : ['genesis_plus_gx']},

    # https://github.com/libretro/libretro-super/blob/master/dist/info/genesis_plus_gx_libretro.info
    # https://github.com/libretro/libretro-super/blob/master/dist/info/picodrive_libretro.info
    {'filename' : 'bios_CD_E.bin', 'size' : 131072, 'md5': 'e66fa1dc5820d254611fdcdba0662372',
     'mandatory' : True, 'cores' : ['genesis_plus_gx', 'picodrive']},
    {'filename' : 'bios_CD_U.bin', 'size' : 131072, 'md5': '2efd74e3232ff260e371b99f84024f7f',
     'mandatory' : True, 'cores' : ['genesis_plus_gx', 'picodrive']},
    {'filename' : 'bios_CD_J.bin', 'size' : 131072, 'md5': '278a9397d192149e84e820ac621a8edd',
     'mandatory' : True, 'cores' : ['genesis_plus_gx', 'picodrive']},

    # https://github.com/libretro/libretro-super/blob/master/dist/info/genesis_plus_gx_libretro.info
    {'filename' : 'bios_E.sms', 'size' : 8192, 'md5': '840481177270d5642a14ca71ee72844c',
     'mandatory' : False, 'cores' : ['genesis_plus_gx']},
    {'filename' : 'bios_J.sms', 'size' : 8192, 'md5': '24a519c53f67b00640d0048ef7089105',
     'mandatory' : False, 'cores' : ['genesis_plus_gx']},
    {'filename' : 'bios_U.sms', 'size' : 8192, 'md5': '840481177270d5642a14ca71ee72844c',
     'mandatory' : False, 'cores' : ['genesis_plus_gx']},
    {'filename' : 'ggenie.bin', 'size' : 32768, 'md5': 'b5d5ff1147036b06944b4d2cac2dd1e1',
     'mandatory' : False, 'cores' : ['genesis_plus_gx']},
    {'filename' : 'sk.bin', 'size' : 2097152, 'md5': '4ea493ea4e9f6c9ebfccbdb15110367e',
     'mandatory' : False, 'cores' : ['genesis_plus_gx']},
    {'filename' : 'sk2chip.bin', 'size' : 262144, 'md5': 'b4e76e416b887f4e7413ba76fa735f16',
     'mandatory' : False, 'cores' : []},

    # --- Sega Saturn ---
    # https://github.com/libretro/libretro-super/blob/master/dist/info/mednafen_saturn_libretro.info
    {'filename' : 'mpr-17933.bin', 'size' : 524288, 'md5': '3240872c70984b6cbfda1586cab68dbe',
     'mandatory' : True, 'cores' : ['mednafen_saturn']},
    {'filename' : 'mpr-18811-mx.ic1', 'size' : 2097152, 'md5': '255113ba943c92a54facd25a10fd780c',
     'mandatory' : True, 'cores' : ['mednafen_saturn']},
    {'filename' : 'mpr-19367-mx.ic1', 'size' : 2097152, 'md5': '1cd19988d1d72a3e7caa0b73234c96b4',
     'mandatory' : True, 'cores' : ['mednafen_saturn']},
    {'filename' : 'sega_101.bin', 'size' : 524288, 'md5': '85ec9ca47d8f6807718151cbcca8b964',
     'mandatory' : True, 'cores' : ['mednafen_saturn']},

    # https://github.com/libretro/libretro-super/blob/master/dist/info/yabause_libretro.info
    {'filename' : 'saturn_bios.bin', 'size' : 524288, 'md5': 'af5828fdff51384f99b3c4926be27762',
     'mandatory' : False, 'cores' : []},

    # --- Sharp - X68000 ---
    {'filename' : 'cgrom.dat', 'size' : 786432, 'md5': 'cb0a5cfcf7247a7eab74bb2716260269',
     'mandatory' : True, 'cores' : []},
    {'filename' : 'iplrom.dat', 'size' : 131072, 'md5': '7fd4caabac1d9169e289f0f7bbf71d8e',
     'mandatory' : True, 'cores' : []},

    # --- Sony PlayStation ---
    {'filename' : 'scph5500.bin', 'size' : 524288, 'md5': '8dd7d5296a650fac7319bce665a6a53c',
     'mandatory' : True, 'cores' : ['mednafen_psx', 'mednafen_psx_hw', 'pcsx_rearmed']},
    {'filename' : 'scph5501.bin', 'size' : 524288, 'md5': '490f666e1afb15b7362b406ed1cea246',
     'mandatory' : True, 'cores' : ['mednafen_psx', 'mednafen_psx_hw', 'pcsx_rearmed']},
    {'filename' : 'scph5502.bin', 'size' : 524288, 'md5': '32736f17079d0b2b7024407c39bd3050',
     'mandatory' : True, 'cores' : ['mednafen_psx', 'mednafen_psx_hw', 'pcsx_rearmed']},

    # --- Sony PlayStation Portable ---
    {'filename' : 'ppge_atlas.zim', 'size' : 784968, 'md5': 'a93fc411c1ce7d001a2a812643c70085',
     'mandatory' : True, 'cores' : ['ppsspp', 'psp1']},

    # --- The 3DO Company - 3DO ---
    {'filename' : 'goldstar.bin', 'size' : 1048576, 'md5': '8639fd5e549bd6238cfee79e3e749114',
     'mandatory' : True, 'cores' : []},
    {'filename' : 'panafz1.bin', 'size' : 1048576, 'md5': 'f47264dd47fe30f73ab3c010015c155b',
     'mandatory' : True, 'cores' : []},
    {'filename' : 'panafz10.bin', 'size' : 1048576, 'md5': '51f2f43ae2f3508a14d9f56597e2d3ce',
     'mandatory' : True, 'cores' : []},
    {'filename' : 'sanyotry.bin', 'size' : 1048576, 'md5': '35fa1a1ebaaeea286dc5cd15487c13ea',
     'mandatory' : True, 'cores' : []},
]
