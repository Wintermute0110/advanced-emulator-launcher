# -*- coding: utf-8 -*-

# Copyright (c) 2016-2021 Wintermute0110 <wintermute0110@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.

# Advanced Emulator Launcher XML autoconfiguration stuff.

# --- Modules/packages in this plugin ---
import resources.const as const
import resources.log as log
import resources.misc as misc
import resources.utils as utils
import resources.platforms as platforms
import resources.db as db
import resources.assets as assets

# --- Kodi stuff ---
# import xbmc
# import xbmcaddon
# import xbmcgui
# import xbmcplugin

# --- Python standard library ---
import os
import time
import xml

# -------------------------------------------------------------------------------------------------
# Exports launchers to an XML file.
# Currently categories are not supported.
# -------------------------------------------------------------------------------------------------
# Helper function to export a single Category.
def export_category_slist(category, sl):
    sl.append('<category>')
    sl.append(misc.XML('name', category['m_name']))
    sl.append(misc.XML('year', category['m_year']))
    sl.append(misc.XML('genre', category['m_genre']))
    sl.append(misc.XML('developer', category['m_developer']))
    sl.append(misc.XML('rating', category['m_rating']))
    sl.append(misc.XML('plot', category['m_plot']))
    sl.append(misc.XML('Asset_Prefix', category['Asset_Prefix']))
    sl.append(misc.XML('s_icon', category['s_icon']))
    sl.append(misc.XML('s_fanart', category['s_fanart']))
    sl.append(misc.XML('s_banner', category['s_banner']))
    sl.append(misc.XML('s_poster', category['s_poster']))
    sl.append(misc.XML('s_clearlogo', category['s_clearlogo']))
    sl.append(misc.XML('s_trailer', category['s_trailer']))
    sl.append('</category>')

# Helper function to export a single Launcher.
def export_launcher_str_list(launcher, category_name, sl):
    # Check if all artwork paths share the same ROM_asset_path. Unless the user has
    # customised the ROM artwork paths this should be the case.
    # A) This function checks if all path_* share a common root directory. If so
    #    this function returns that common directory as an Unicode string. In this
    #    case AEL will write the tag <ROM_asset_path> only.
    # B) If path_* do not share a common root directory this function returns '' and then
    #    AEL writes all <path_*> tags in the XML file.
    ROM_asset_path = assets_get_ROM_asset_path(launcher)
    log.debug('autoconfig_export_all() ROM_asset_path "{}"'.format(ROM_asset_path))

    # Export Launcher
    sl.append('<launcher>')
    sl.append(misc.XML('name', launcher['m_name']))
    sl.append(misc.XML('category', category_name))
    sl.append(misc.XML('year', launcher['m_year']))
    sl.append(misc.XML('genre', launcher['m_genre']))
    sl.append(misc.XML('developer', launcher['m_developer']))
    sl.append(misc.XML('rating', launcher['m_rating']))
    sl.append(misc.XML('plot', launcher['m_plot']))
    sl.append(misc.XML('platform', launcher['platform']))
    sl.append(misc.XML('application', launcher['application']))
    sl.append(misc.XML('args', launcher['args']))
    if launcher['args_extra']:
        for extra_arg in launcher['args_extra']: sl.append(misc.XML('args_extra', extra_arg))
    else:
        sl.append(misc.XML('args_extra', ''))
    sl.append(misc.XML('ROM_path', launcher['rompath']))
    sl.append(misc.XML('ROM_extra_path', launcher['romextrapath']))
    sl.append(misc.XML('ROM_ext', launcher['romext']))
    if ROM_asset_path:
        sl.append(misc.XML('ROM_asset_path', ROM_asset_path))
    else:
        sl.append(misc.XML('path_3dbox', launcher['path_3dbox']))
        sl.append(misc.XML('path_title', launcher['path_title']))
        sl.append(misc.XML('path_snap', launcher['path_snap']))
        sl.append(misc.XML('path_boxfront', launcher['path_boxfront']))
        sl.append(misc.XML('path_boxback', launcher['path_boxback']))
        sl.append(misc.XML('path_cartridge', launcher['path_cartridge']))
        sl.append(misc.XML('path_fanart', launcher['path_fanart']))
        sl.append(misc.XML('path_banner', launcher['path_banner']))
        sl.append(misc.XML('path_clearlogo', launcher['path_clearlogo']))
        sl.append(misc.XML('path_flyer', launcher['path_flyer']))
        sl.append(misc.XML('path_map', launcher['path_map']))
        sl.append(misc.XML('path_manual', launcher['path_manual']))
        sl.append(misc.XML('path_trailer', launcher['path_trailer']))
    sl.append(misc.XML('Asset_Prefix', launcher['Asset_Prefix']))
    sl.append(misc.XML('s_icon', launcher['s_icon']))
    sl.append(misc.XML('s_fanart', launcher['s_fanart']))
    sl.append(misc.XML('s_banner', launcher['s_banner']))
    sl.append(misc.XML('s_poster', launcher['s_poster']))
    sl.append(misc.XML('s_clearlogo', launcher['s_clearlogo']))
    sl.append(misc.XML('s_controller', launcher['s_controller']))
    sl.append(misc.XML('s_trailer', launcher['s_trailer']))
    sl.append('</launcher>')

# Export all Categories and Launchers.
# Check if the output XML file exists (and show a warning dialog if so) is done in caller.
def export_all(categories, launchers, export_FN):
    # --- XML header ---
    sl = []
    sl.append('<?xml version="1.0" encoding="utf-8" standalone="yes"?>')
    sl.append('<!-- Exported by AEL on {} -->'.format(time.strftime("%Y-%m-%d %H:%M:%S")))
    sl.append('<advanced_emulator_launcher_configuration>')

    # --- Export Categories ---
    # Data which is not string must be converted to string
    for categoryID in sorted(categories, key = lambda x : categories[x]['m_name']):
        category = categories[categoryID]
        log.debug('autoconfig_export_all() Category "{}" (ID "{}")'.format(category['m_name'], categoryID))
        export_category_str_list(category, sl)

    # --- Export Launchers and add XML tail ---
    # Data which is not string must be converted to string
    for launcherID in sorted(launchers, key = lambda x : launchers[x]['m_name']):
        launcher = launchers[launcherID]
        if launcher['categoryID'] in categories:
            category_name = categories[launcher['categoryID']]['m_name']
        elif launcher['categoryID'] == CATEGORY_ADDONROOT_ID:
            category_name = CATEGORY_ADDONROOT_ID
        else:
            kodi.dialog_OK('Launcher category not found. This is a bug, please report it.')
            return
        log.debug('autoconfig_export_all() Launcher "{}" (ID "{}")'.format(launcher['m_name'], launcherID))
        export_launcher_str_list(launcher, category_name, sl)
    sl.append('</advanced_emulator_launcher_configuration>')
    sl.append('')
    utils.write_slist_to_file(export_FN.getPath(), sl)

# Export a single Launcher XML configuration.
# Check if the output XML file exists (and show a warning dialog if so) is done in caller.
def export_launcher(launcher, export_FN, categories):
    launcherID = launcher['id']
    if launcher['categoryID'] in categories:
        category_name = categories[launcher['categoryID']]['m_name']
    elif launcher['categoryID'] == CATEGORY_ADDONROOT_ID:
        category_name = CATEGORY_ADDONROOT_ID
    else:
        kodi.dialog_OK('Launcher category not found. This is a bug, please report it.')
        raise AEL_Error('Error exporting Launcher XML configuration')
    log.debug('autoconfig_export_launcher() Launcher "{}" (ID "{}")'.format(launcher['m_name'], launcherID))

    sl = []
    sl.append('<?xml version="1.0" encoding="utf-8" standalone="yes"?>')
    sl.append('<!-- Exported by AEL on {} -->'.format(time.strftime("%Y-%m-%d %H:%M:%S")))
    sl.append('<advanced_emulator_launcher_configuration>')
    export_launcher_str_list(launcher, category_name, sl)
    sl.append('</advanced_emulator_launcher_configuration>')
    sl.append('')
    utils.write_slist_to_file(export_FN.getPath(), sl)

# Export a single Category XML configuration.
# Check if the output XML file exists (and show a warning dialog if so) is done in caller.
def export_category(category, export_FN):
    log.debug('export_category() Category "{}"'.format(category['m_name']))
    log.debug('export_category() ID "{}"'.format(category['id']))
    sl = [
        '<?xml version="1.0" encoding="utf-8" standalone="yes"?>',
        '<!-- Exported by AEL on {} -->'.format(time.strftime("%Y-%m-%d %H:%M:%S")),
        '<advanced_emulator_launcher_configuration>',
    ]
    export_category_slist(category, sl)
    sl.append('</advanced_emulator_launcher_configuration>\n')
    utils.write_slist_to_file(export_FN.getPath(), sl)

# -------------------------------------------------------------------------------------------------
# Import AEL launcher configuration
# -------------------------------------------------------------------------------------------------
def get_default_import_category():
    return {
        'name' : '',
        'year' : '',
        'genre' : '',
        'developer' : '',
        'rating' : '',
        'plot' : '',
        'Asset_Prefix' : '',
        's_icon' : '',
        's_fanart' : '',
        's_banner' : '',
        's_poster' : '',
        's_clearlogo' : '',
        's_trailer' : '',
    }

def get_default_import_launcher():
    return {
        'name' : '',
        'category' : 'root_category',
        'Launcher_NFO' : '',
        'year' : '',
        'genre' : '',
        'developer' : '',
        'rating' : '',
        'plot' : '',
        'platform' : 'Unknown',
        'application' : '',
        'args' : [],
        'args_extra' : [],
        'ROM_path' : '',
        'ROM_ext' : '',
        'ROM_extra_path' : '',
        'Options' : '',
        'ROM_asset_path' : '',
        'path_3dbox' : '',
        'path_title' : '',
        'path_snap' : '',
        'path_boxfront' : '',
        'path_boxback' : '',
        'path_cartridge' : '',
        'path_fanart' : '',
        'path_banner' : '',
        'path_clearlogo' : '',
        'path_flyer' : '',
        'path_map' : '',
        'path_manual' : '',
        'path_trailer' : '',
        'Asset_Prefix' : '',
        's_icon' : '',
        's_fanart' : '',
        's_banner' : '',
        's_poster' : '',
        's_clearlogo' : '',
        's_controller' : '',
        's_trailer' : '',
    }

def search_all_by_name(i_launcher, categories, launchers):
    cat_name = i_launcher['category']
    laun_name = i_launcher['name']
    s_category = None
    if cat_name == CATEGORY_ADDONROOT_ID:
        s_category = CATEGORY_ADDONROOT_ID
    else:
        for categoryID in categories:
            category = categories[categoryID]
            if cat_name == category['m_name']:
                s_category = category['id']
                break

    # If the category was found then search the launcher inside that category.
    if s_category:
        s_launcher = None
        for launcherID in launchers:
            launcher = launchers[launcherID]
            if s_category != launcher['categoryID']: continue
            if laun_name == launcher['m_name']:
                s_launcher = launcher['id']
                break
    # If the category was not found then launcher does not exist.
    else:
        s_launcher = None

    return (s_category, s_launcher)

def search_category_by_name(i_category, categories):
    cat_name = i_category['name']
    s_category = None
    if cat_name == CATEGORY_ADDONROOT_ID:
        s_category = CATEGORY_ADDONROOT_ID
    else:
        for categoryID in categories:
            if cat_name == categories[categoryID]['m_name']:
                s_category = categories[categoryID]['id']
                break

    return s_category

# def search_launcher_by_name(launcher_name):
#     s_launcher = None
#     for launcherID in self.launchers:
#         launcher = self.launchers[launcherID]
#         if launcher_name == launcher['m_name']:
#             s_launcher = launcher['id']
#             return s_launcher
# 
#     return s_launcher

def import_launchers(CATEGORIES_FILE_PATH, ROMS_DIR, categories, launchers, import_FN):
    # Load XML file. Fill missing XML tags with sensible defaults.
    __debug_xml_parser = True
    log.debug('autoconfig_import_launchers() Loading {}'.format(import_FN.getOriginalPath()))
    xml_tree = utils_load_XML_to_ET(import_FN.getOriginalPath())
    xml_root = xml_tree.getroot()

    # Process tags in XML configuration file
    imported_categories_list = []
    imported_launchers_list = []
    list_type_tags = ['args', 'args_extra']
    for root_element in xml_root:
        if __debug_xml_parser: log.debug('>>> Root child tag <{}>'.format(root_element.tag))

        if root_element.tag == 'category':
            category_temp = autoconfig_get_default_import_category()
            for root_child in root_element:
                # By default read strings
                misc.XML = root_child.text if root_child.text is not None else ''
                misc.XML = text_unescape_XML(misc.XML)
                xml_tag  = root_child.tag
                if __debug_xml_parser: log.debug('>>> "{:<11s}" --> "{}"'.format(xml_tag, misc.XML))
                category_temp[xml_tag] = misc.XML
            # --- Add category to categories dictionary ---
            log.debug('Adding category "{}" to import list'.format(category_temp['name']))
            imported_categories_list.append(category_temp)
        elif root_element.tag == 'launcher':
            launcher_temp = autoconfig_get_default_import_launcher()
            for root_child in root_element:
                # By default read strings
                misc.XML = root_child.text if root_child.text is not None else ''
                misc.XML = text_unescape_XML(misc.XML)
                xml_tag  = root_child.tag
                if __debug_xml_parser: log.debug('>>> "{:<11s}" --> "{}"'.format(xml_tag, misc.XML))

                # Transform list datatype. Only add to the list if string is non empty.
                if xml_tag in list_type_tags and misc.XML:
                    launcher_temp[xml_tag].append(misc.XML)
                    continue
                launcher_temp[xml_tag] = misc.XML
            # --- Add launcher to categories dictionary ---
            log.debug('Adding launcher "{}" to import list'.format(launcher_temp['name']))
            imported_launchers_list.append(launcher_temp)
        else:
            log.warning('Unrecognised root tag <{}>'.format(root_element.tag))

    # Traverse category import list and import all launchers found in XML file.
    for i_category in imported_categories_list:
        log.info('Processing Category "{}"'.format(i_category['name']))

        # Search category/launcher database to check if imported launcher/category exist.
        s_categoryID = autoconfig_search_category_by_name(i_category, categories)
        log.debug('s_category = "{}"'.format(s_categoryID))

        # --- Options ---
        # A) Category not found. Create new category.
        # B) Category found. Edit existing category.
        if not s_categoryID:
            # Create category AND launcher and import.
            # NOTE root_addon category is always found in autoconfig_search_all_by_name()
            log.debug('Case A) Category not found. Create new category.')
            category = fs_new_category()
            categoryID = misc_generate_random_SID()
            category['id'] = categoryID
            category['m_name'] = i_category['name']
            categories[categoryID] = category
            log.debug('New Category "{}" (ID {})'.format(i_category['name'], categoryID))

            # Import launcher. Only import fields that are not empty strings.
            autoconfig_import_category(categories, categoryID, i_category, import_FN)
        else:
            # Category exists (by name). Overwrite?
            log.debug('Case B) Category found. Edit existing category.')
            ret = kodi_dialog_yesno('Category "{}" found in AEL database. Overwrite?'.format(i_category['name']))
            if ret < 1: continue

            # Import launcher. Only import fields that are not empty strings.
            autoconfig_import_category(categories, s_categoryID, i_category, import_FN)

    # Traverse launcher import list and import all launchers found in XML file.
    # A) Match categories by name. If multiple categories with same name pick the first one.
    # B) If category does not exist create a new one.
    # C) Launchers are matched by name. If launcher name not found then create a new launcherID.
    for i_launcher in imported_launchers_list:
        log.info('Processing Launcher "{}"'.format(i_launcher['name']))
        log.info('      with Category "{}"'.format(i_launcher['category']))

        # Search category/launcher database to check if imported launcher/category exist.
        (s_categoryID, s_launcherID) = autoconfig_search_all_by_name(i_launcher, categories, launchers)
        log.debug('s_launcher = "{}"'.format(s_launcherID))
        log.debug('s_category = "{}"'.format(s_categoryID))

        # --- Options ---
        # NOTE If category not found then create a new one for this imported launcher
        # A) Category not found. This implies launcher not found.
        # B) Category found and Launcher not found.
        # C) Category found and Launcher found.
        if not s_categoryID:
            # Create category AND launcher and import.
            # NOTE root_addon category is always found in autoconfig_search_all_by_name()
            log.debug('Case A) Category not found. This implies launcher not found.')
            category = fs_new_category()
            categoryID = misc_generate_random_SID()
            category['id'] = categoryID
            category['m_name'] = i_launcher['category']
            categories[categoryID] = category
            log.debug('New Category "{}" (ID {})'.format(i_launcher['category'], categoryID))

            # Create new launcher inside newly created category and import launcher.
            launcherID = misc_generate_random_SID()
            launcherdata = fs_new_launcher()
            launcherdata['id'] = launcherID
            launcherdata['categoryID'] = categoryID
            launcherdata['timestamp_launcher'] = time.time()
            launchers[launcherID] = launcherdata
            log.debug('New Launcher "{}" (ID {})'.format(i_launcher['name'], launcherID))

            # Import launcher. Only import fields that are not empty strings.
            # Function edits self.launchers dictionary using first argument key
            autoconfig_import_launcher(ROMS_DIR, categories, launchers, categoryID, launcherID, i_launcher, import_FN)

        elif s_categoryID and not s_launcherID:
            # Create new launcher inside existing category and import launcher.
            log.debug('Case B) Category found and Launcher not found.')
            launcherID = misc_generate_random_SID()
            launcherdata = fs_new_launcher()
            launcherdata['id'] = launcherID
            launcherdata['categoryID'] = s_categoryID
            launcherdata['timestamp_launcher'] = time.time()
            launchers[launcherID] = launcherdata
            log.debug('New Launcher "{}" (ID {})'.format(i_launcher['name'], launcherID))

            # Import launcher. Only import fields that are not empty strings.
            autoconfig_import_launcher(ROMS_DIR, categories, launchers, s_categoryID, launcherID, i_launcher, import_FN)

        else:
            # Both category and launcher exists (by name). Overwrite?
            log.debug('Case C) Category and Launcher found.')
            cat_name = i_launcher['category'] if i_launcher['category'] != CATEGORY_ADDONROOT_ID else 'Root Category'
            ret = kodi_dialog_yesno('Launcher "{}" in Category "{}" '.format(i_launcher['name'], cat_name) +
                'found in AEL database. Overwrite?')
            if ret < 1: continue

            # Import launcher. Only import fields that are not empty strings.
            autoconfig_import_launcher(ROMS_DIR, categories, launchers, s_categoryID, s_launcherID, i_launcher, import_FN)

# Imports/edits a category with an external XML config file.
def import_category(categories, categoryID, i_category, import_FN):
    log.debug('autoconfig_import_category() categoryID = {}'.format(categoryID))

    # --- Category metadata ---
    if i_category['name']:
        categories[categoryID]['m_name'] = i_category['name']
        log.debug('Imported m_name       "{}"'.format(i_category['name']))

    if i_category['year']:
        categories[categoryID]['m_year'] = i_category['year']
        log.debug('Imported m_year       "{}"'.format(i_category['year']))

    if i_category['genre']:
        categories[categoryID]['m_genre'] = i_category['genre']
        log.debug('Imported m_genre      "{}"'.format(i_category['genre']))

    if i_category['developer']:
        categories[categoryID]['m_developer'] = i_category['developer']
        log.debug('Imported m_developer  "{}"'.format(i_category['developer']))

    if i_category['rating']:
        categories[categoryID]['m_rating'] = i_category['rating']
        log.debug('Imported m_rating =   "{}"'.format(i_category['rating']))

    if i_category['plot']:
        categories[categoryID]['m_plot'] = i_category['plot']
        log.debug('Imported m_plot       "{}"'.format(i_category['plot']))

    # --- Category assets/artwork ---
    if i_category['Asset_Prefix']:
        categories[categoryID]['Asset_Prefix'] = i_category['Asset_Prefix']
        log.debug('Imported Asset_Prefix "{}"'.format(i_category['Asset_Prefix']))
    Asset_Prefix = i_category['Asset_Prefix']
    if Asset_Prefix:
        log.debug('Asset_Prefix non empty. Looking for asset files.')
        (Asset_Prefix_head, Asset_Prefix_tail) = os.path.split(Asset_Prefix)
        log.debug('Effective Asset_Prefix "{}"'.format(Asset_Prefix))
        log.debug('Asset_Prefix_head      "{}"'.format(Asset_Prefix_head))
        log.debug('Asset_Prefix_tail      "{}"'.format(Asset_Prefix_tail))
        if Asset_Prefix_head:
            log.debug('Asset_Prefix head not empty')
            asset_dir_FN = FileName(import_FN.getDir()).pjoin(Asset_Prefix_head)
            norm_asset_dir_FN = FileName(os.path.normpath(asset_dir_FN.getPath()))
            effective_Asset_Prefix = Asset_Prefix_tail
        else:
            log.debug('Asset_Prefix head is empty. Assets in same dir as XML file')
            asset_dir_FN = FileName(import_FN.getDir())
            norm_asset_dir_FN = FileName(os.path.normpath(asset_dir_FN.getPath()))
            effective_Asset_Prefix = Asset_Prefix_tail
        log.debug('import_FN              "{}"'.format(import_FN.getPath()))
        log.debug('asset_dir_FN           "{}"'.format(asset_dir_FN.getPath()))
        log.debug('norm_asset_dir_FN      "{}"'.format(norm_asset_dir_FN.getPath()))
        log.debug('effective_Asset_Prefix "{}"'.format(effective_Asset_Prefix))

        # Get a list of all files in the directory pointed by Asset_Prefix and use this list as
        # a file cache. This list has filenames withouth path.
        log.debug('Scanning files in dir "{}"'.format(norm_asset_dir_FN.getPath()))
        try:
            file_list = sorted(os.listdir(norm_asset_dir_FN.getPath()))
        except WindowsError as E:
            log.error('autoconfig_import_category() (exceptions.WindowsError) exception')
            log.error('Exception message: "{}"'.format(E))
            kodi.dialog_OK('WindowsError exception. {}'.format(E))
            kodi.dialog_OK('Scanning assets using the Asset_Prefix tag in '
                           'Category "{}" will be disabled.'.format(i_category['name']))
            file_list = []
        log.debug('Found {} files'.format(len(file_list)))
        # log.debug('--- File list ---')
        # for file in file_list: log.debug('--- "{}"'.format(file))
    else:
        log.debug('Asset_Prefix empty. Not looking for any asset files.')
        norm_asset_dir_FN = None
        effective_Asset_Prefix = ''
        file_list = []

    # Traverse list of category assets and search for image files for each asset.
    for cat_asset in CATEGORY_ASSET_ID_LIST:
        # Bypass trailers now
        if cat_asset == ASSET_TRAILER_ID: continue

        # Look for assets using the file list cache.
        AInfo = assets_get_info_scheme(cat_asset)
        log.debug('>> Asset "{}"'.format(AInfo.name))
        asset_file_list = autoconfig_search_asset_file_list(
            effective_Asset_Prefix, AInfo, norm_asset_dir_FN, file_list)

        # --- Create image list for selection dialog ---
        listitems_list = []
        listitems_asset_paths = []
        # Current image if found
        current_FN = FileName(categories[categoryID][AInfo.key])
        if current_FN.exists():
            asset_listitem = xbmcgui.ListItem(label = 'Current image', label2 = current_FN.getPath())
            asset_listitem.setArt({'icon' : current_FN.getPath()})
            listitems_list.append(asset_listitem)
            listitems_asset_paths.append(current_FN.getPath())
        # Image in <s_icon>, <s_fanart>, ... tags if found
        tag_asset_FN = FileName(i_category[AInfo.key])
        if tag_asset_FN.exists():
            asset_listitem = xbmcgui.ListItem(label = 'XML <{}> image'.format(AInfo.key),
                                              label2 = tag_asset_FN.getPath())
            asset_listitem.setArt({'icon' : tag_asset_FN.getPath()})
            listitems_list.append(asset_listitem)
            listitems_asset_paths.append(tag_asset_FN.getPath())
        # Images found in XML configuration via <Asset_Prefix> tag if found
        image_count = 1
        for asset_file_name in asset_file_list:
            log.debug('asset_file_name "{}"'.format(asset_file_name))
            asset_FN = FileName(asset_file_name)
            asset_listitem = xbmcgui.ListItem(
                label = 'Asset_Prefix #{} "{}"'.format(image_count, asset_FN.getBase()),
                label2 = asset_file_name)
            asset_listitem.setArt({'icon' : asset_file_name})
            listitems_list.append(asset_listitem)
            listitems_asset_paths.append(asset_FN.getPath())
            image_count += 1
        # >> If list is empty at this point no images were found at all.
        if not listitems_list:
            log.debug('listitems_list is empty. Keeping {} as it was.'.format(AInfo.name))
            continue
        # >> No image
        asset_listitem = xbmcgui.ListItem(label = 'No image')
        asset_listitem.setArt({'icon' : 'DefaultAddonNone.png'})
        listitems_list.append(asset_listitem)
        listitems_asset_paths.append('')

        # Show image selection select() dialog
        title_str = 'Category "{}". Choose {} ...'.format(i_category['name'], AInfo.name)
        ret_idx = KodiSelectDialog(title_str, listitems_list, useDetails = True).executeDialog()
        if ret_idx is None: return

        # Set asset field
        categories[categoryID][AInfo.key] = listitems_asset_paths[ret_idx]
        log.debug('Set category artwork "{}" = "{}"'.format(AInfo.key, listitems_asset_paths[ret_idx]))

# Imports/Edits a launcher with an extenal XML config file.
def import_launcher(ROMS_DIR, categories, launchers, categoryID, launcherID, i_launcher, import_FN):
    log.debug('autoconfig_import_launcher() categoryID = {}'.format(categoryID))
    log.debug('autoconfig_import_launcher() launcherID = {}'.format(launcherID))
    Launcher_NFO_meta = {'year' : '', 'genre' : '', 'developer' : '', 'rating' : '', 'plot' : ''}
    XML_meta          = {'year' : '', 'genre' : '', 'developer' : '', 'rating' : '', 'plot' : ''}

    # --- Launcher metadata ---
    if i_launcher['name']:
        old_launcher_name = launchers[launcherID]['m_name']
        new_launcher_name = i_launcher['name']
        log.debug('old_launcher_name "{}"'.format(old_launcher_name))
        log.debug('new_launcher_name "{}"'.format(new_launcher_name))
        launchers[launcherID]['m_name'] = i_launcher['name']
        log.debug('Imported m_name "{}"'.format(i_launcher['name']))

    # Process <Launcher_NFO> before any metadata tag
    if i_launcher['Launcher_NFO']:
        log.debug('Processing <Launcher_NFO> "{}"'.format(i_launcher['Launcher_NFO']))
        Launcher_NFO_FN = FileName(import_FN.getDir()).pjoin(i_launcher['Launcher_NFO'])
        Launcher_NFO_meta = fs_read_launcher_NFO(Launcher_NFO_FN)
        log.debug('NFO year      "{}"'.format(Launcher_NFO_meta['year']))
        log.debug('NFO genre     "{}"'.format(Launcher_NFO_meta['genre']))
        log.debug('NFO developer "{}"'.format(Launcher_NFO_meta['developer']))
        log.debug('NFO rating    "{}"'.format(Launcher_NFO_meta['rating']))
        log.debug('NFO plot      "{}"'.format(Launcher_NFO_meta['plot']))

    # Process XML metadata and put in temporal dictionary
    if i_launcher['year']:
        XML_meta['year'] = i_launcher['year']
        log.debug('XML year      "{}"'.format(i_launcher['year']))

    if i_launcher['genre']:
        XML_meta['genre'] = i_launcher['genre']
        log.debug('XML genre     "{}"'.format(i_launcher['genre']))

    if i_launcher['developer']:
        XML_meta['developer'] = i_launcher['developer']
        log.debug('XML developer "{}"'.format(i_launcher['developer']))

    if i_launcher['rating']:
        XML_meta['rating'] = i_launcher['rating']
        log.debug('XML rating    "{}"'.format(i_launcher['rating']))

    if i_launcher['plot']:
        XML_meta['plot'] = i_launcher['plot']
        log.debug('XML plot      "{}"'.format(i_launcher['plot']))

    # Process metadata. XML metadata overrides Launcher_NFO metadata, if exists.
    if XML_meta['year']:
        launchers[launcherID]['m_year'] = XML_meta['year']
        log.debug('Imported m_year "{}"'.format(XML_meta['year']))
    elif Launcher_NFO_meta['year']:
        launchers[launcherID]['m_year'] = Launcher_NFO_meta['year']
        log.debug('Imported m_year "{}"'.format(Launcher_NFO_meta['year']))

    if XML_meta['genre']:
        launchers[launcherID]['m_genre'] = XML_meta['genre']
        log.debug('Imported m_genre "{}"'.format(XML_meta['genre']))
    elif Launcher_NFO_meta['genre']:
        launchers[launcherID]['m_genre'] = Launcher_NFO_meta['genre']
        log.debug('Imported m_genre "{}"'.format(Launcher_NFO_meta['genre']))

    if XML_meta['developer']:
        launchers[launcherID]['m_developer'] = XML_meta['developer']
        log.debug('Imported m_developer "{}"'.format(XML_meta['developer']))
    elif Launcher_NFO_meta['developer']:
        launchers[launcherID]['m_developer'] = Launcher_NFO_meta['developer']
        log.debug('Imported m_developer "{}"'.format(Launcher_NFO_meta['developer']))

    if XML_meta['rating']:
        launchers[launcherID]['m_rating'] = XML_meta['rating']
        log.debug('Imported m_rating "{}"'.format(XML_meta['rating']))
    elif Launcher_NFO_meta['rating']:
        launchers[launcherID]['m_rating'] = Launcher_NFO_meta['rating']
        log.debug('Imported m_rating "{}"'.format(Launcher_NFO_meta['rating']))

    if XML_meta['plot']:
        launchers[launcherID]['m_plot'] = XML_meta['plot']
        log.debug('Imported m_plot "{}"'.format(XML_meta['plot']))
    elif Launcher_NFO_meta['plot']:
        launchers[launcherID]['m_plot'] = Launcher_NFO_meta['plot']
        log.debug('Imported m_plot "{}"'.format(Launcher_NFO_meta['plot']))

    # --- Launcher stuff ---
    # If platform cannot be found in the official list then warn user and set it to 'Unknown'
    if i_launcher['platform']:
        platform = i_launcher['platform']
        if i_launcher['platform'] in platform_long_to_index_dic:
            log.debug('Platform name "{}" recognised'.format(platform))
        else:
            kodi.dialog_OK(
                'Unrecognised platform name "{}".'.format(platform),
                title = 'Launcher "{}"'.format(i_launcher['name']))
            log.debug('Unrecognised platform name "{}".'.format(platform))
        launchers[launcherID]['platform'] = platform
        log.debug('Imported platform "{}"'.format(platform))

    # >> If application not found warn user.
    if i_launcher['application']:
        app_FN = FileName(i_launcher['application'])
        if not app_FN.exists():
            log.debug('Application NOT found.')
            kodi.dialog_OK(
                'Application "{}" not found'.format(app_FN.getPath()),
                title = 'Launcher "{}"'.format(i_launcher['name']))
        else:
            log.debug('Application found.')
        launchers[launcherID]['application'] = i_launcher['application']
        log.debug('Imported application "{}"'.format(i_launcher['application']))

    # Both <args> and <args_extra> are lists. <args_extra> is deprecated.
    # Case 1) Only one <args> tag
    # Case 2) Multiple <args> tag
    # Case 3) One <arg> tag and one or more <args_extra> tags. This is deprecated.
    len_args = len(i_launcher['args'])
    len_extra_args = len(i_launcher['args_extra'])
    if len_args == 1 and len_extra_args == 0:
        args_str = i_launcher['args'][0]
        launchers[launcherID]['args'] = args_str
        launchers[launcherID]['args_extra'] = []
        log.debug('Imported args "{}"'.format(i_launcher['args']))
        log.debug('Resetted args_extra')
    elif len_args > 1 and len_extra_args == 0:
        args_str = i_launcher['args'][0]
        args_extra_list = i_launcher['args'][1:]
        launchers[launcherID]['args'] = args_str
        log.debug('Imported args "{}"'.format(args_str))
        launchers[launcherID]['args_extra'] = []
        for args in args_extra_list:
            launchers[launcherID]['args_extra'].append(args)
            log.debug('Imported args_extra "{}"'.format(args))
    elif len_args == 1 and len_extra_args >= 1:
        args_str = i_launcher['args'][0]
        args_extra_list = i_launcher['args_extra']
        launchers[launcherID]['args'] = args_str
        log.debug('Imported args "{}"'.format(args_str))
        launchers[launcherID]['args_extra'] = []
        for args in args_extra_list:
            launchers[launcherID]['args_extra'].append(args)
            log.debug('Imported args_extra "{}"'.format(args))
    else:
        log.error('Wrong usage of <args> and <args_extra>')
        log.error('len_args = {}, len_extra_args = {}'.format(len_args, len_extra_args))
        log.error('No arguments imported.')

    # Warn user if rompath directory does not exist
    if i_launcher['ROM_path']:
        rompath = FileName(i_launcher['ROM_path'])
        log.debug('ROMpath OP "{}"'.format(rompath.getOriginalPath()))
        log.debug('ROMpath  P "{}"'.format(rompath.getPath()))
        if not rompath.exists():
            log.debug('ROM path NOT found.')
            kodi.dialog_OK(
                'ROM path "{}" not found'.format(rompath.getPath()),
                title = 'Launcher "{}"'.format(i_launcher['name']))
        else:
            log.debug('ROM_path found.')
        launchers[launcherID]['rompath'] = i_launcher['ROM_path']
        log.debug('Imported ROM path "{}"'.format(i_launcher['ROM_path']))

    if i_launcher['ROM_ext']:
        launchers[launcherID]['romext'] = i_launcher['ROM_ext']
        log.debug('Imported romext "{}"'.format(i_launcher['ROM_ext']))

    if i_launcher['ROM_extra_path']:
        rompath = FileName(i_launcher['ROM_extra_path'])
        log.debug('ROMpath OP "{}"'.format(rompath.getOriginalPath()))
        log.debug('ROMpath  P "{}"'.format(rompath.getPath()))
        if not rompath.exists():
            log.debug('ROM_extra_path NOT found.')
            kodi.dialog_OK(
                'ROM path "{}" not found'.format(rompath.getPath()),
                title = 'Launcher "{}"'.format(i_launcher['name']))
        else:
            log.debug('ROM_extra_path found.')
        launchers[launcherID]['romextrapath'] = i_launcher['ROM_extra_path']
        log.debug('Imported ROM extra path "{}"'.format(i_launcher['ROM_extra_path']))

    # --- Launcher options ---
    if i_launcher['Options']:
        opt_string = text_type(i_launcher['Options']).strip()
        log.debug('Imported Options "{}"'.format(opt_string))
        # Parse options
        raw_opt_list = opt_string.split(',')
        opt_list = [w.strip() for w in raw_opt_list]
        log.debug('Stripped options list {}'.format(text_type(opt_list)))
        launcher = launchers[launcherID]
        for option in opt_list:
            if option == 'Blocking':
                launcher['non_blocking'] = False
                log.debug('Set launcher non_blocking to {}'.format(launcher['non_blocking']))
            elif option == 'NonBlocking':
                launcher['non_blocking'] = True
                log.debug('Set launcher non_blocking to {}'.format(launcher['non_blocking']))

            elif option == 'StaticWindow':
                launcher['minimize'] = False
                log.debug('Set launcher minimize to {}'.format(launcher['minimize']))
            elif option == 'ToggleWindow':
                launcher['minimize'] = True
                log.debug('Set launcher minimize to {}'.format(launcher['minimize']))

            elif option == 'Unfinished':
                launcher['finished'] = False
                log.debug('Set launcher finished to {}'.format(launcher['finished']))
            elif option == 'Finished':
                launcher['finished'] = True
                log.debug('Set launcher finished to {}'.format(launcher['finished']))

            else:
                kodi.dialog_OK('Unrecognised launcher <Option> "{}"'.format(option))

    # --- ROM assets path ---
    # If ROM_asset_path not found warn the user and tell him if should be created or not.
    if i_launcher['ROM_asset_path']:
        launchers[launcherID]['ROM_asset_path'] = i_launcher['ROM_asset_path']
        log.debug('Imported ROM_asset_path  "{}"'.format(i_launcher['ROM_asset_path']))
        ROM_asset_path_FN = FileName(i_launcher['ROM_asset_path'])
        log.debug('ROM_asset_path_FN OP "{}"'.format(ROM_asset_path_FN.getOriginalPath()))
        log.debug('ROM_asset_path_FN  P "{}"'.format(ROM_asset_path_FN.getPath()))

        # Warn user if ROM_asset_path_FN directory does not exist
        if not ROM_asset_path_FN.exists():
            log.debug('Not found ROM_asset_path "{}"'.format(ROM_asset_path_FN.getPath()))
            ret = kodi_dialog_yesno(
                'ROM asset path "{}" not found. '.format(ROM_asset_path_FN.getPath()) +
                'Create it?', title = 'Launcher "{}"'.format(i_launcher['name']))
            if ret:
                log.debug('Creating dir "{}"'.format(ROM_asset_path_FN.getPath()))
                ROM_asset_path_FN.makedirs()
            else:
                log.debug('Do not create "{}"'.format(ROM_asset_path_FN.getPath()))

        # Create asset directories if ROM path exists
        if ROM_asset_path_FN.exists():
            log.debug('ROM_asset_path path found. Creating assets subdirectories.')
            assets_init_asset_dir(ROM_asset_path_FN, launchers[launcherID])
        else:
            log.debug('ROM_asset_path path not found even after asking user to create it or not.')
            log.debug('ROM asset directories left blank or as there were.')

    # --- <path_*> tags override <ROM_asset_path> ---
    # This paths will be imported in a raw way, no existance checkings will be done.
    # Note that path_* tags will be imported only if they are non-empty.
    if i_launcher['path_3dbox']:
        launchers[launcherID]['path_3dbox'] = i_launcher['path_3dbox']
        log.debug('Imported path_3dbox "{}"'.format(i_launcher['path_3dbox']))

    if i_launcher['path_title']:
        launchers[launcherID]['path_title'] = i_launcher['path_title']
        log.debug('Imported path_title "{}"'.format(i_launcher['path_title']))

    if i_launcher['path_snap']:
        launchers[launcherID]['path_snap'] = i_launcher['path_snap']
        log.debug('Imported path_snap "{}"'.format(i_launcher['path_snap']))

    if i_launcher['path_boxfront']:
        launchers[launcherID]['path_boxfront'] = i_launcher['path_boxfront']
        log.debug('Imported path_boxfront "{}"'.format(i_launcher['path_boxfront']))

    if i_launcher['path_boxback']:
        launchers[launcherID]['path_boxback'] = i_launcher['path_boxback']
        log.debug('Imported path_boxback "{}"'.format(i_launcher['path_boxback']))

    if i_launcher['path_cartridge']:
        launchers[launcherID]['path_cartridge'] = i_launcher['path_cartridge']
        log.debug('Imported path_cartridge "{}"'.format(i_launcher['path_cartridge']))

    if i_launcher['path_fanart']:
        launchers[launcherID]['path_fanart'] = i_launcher['path_fanart']
        log.debug('Imported path_fanart "{}"'.format(i_launcher['path_fanart']))

    if i_launcher['path_banner']:
        launchers[launcherID]['path_banner'] = i_launcher['path_banner']
        log.debug('Imported path_banner "{}"'.format(i_launcher['path_banner']))

    if i_launcher['path_clearlogo']:
        launchers[launcherID]['path_clearlogo'] = i_launcher['path_clearlogo']
        log.debug('Imported path_clearlogo "{}"'.format(i_launcher['path_clearlogo']))

    if i_launcher['path_flyer']:
        launchers[launcherID]['path_flyer'] = i_launcher['path_flyer']
        log.debug('Imported path_flyer "{}"'.format(i_launcher['path_flyer']))

    if i_launcher['path_map']:
        launchers[launcherID]['path_map'] = i_launcher['path_map']
        log.debug('Imported path_map "{}"'.format(i_launcher['path_map']))

    if i_launcher['path_manual']:
        launchers[launcherID]['path_manual'] = i_launcher['path_manual']
        log.debug('Imported path_manual "{}"'.format(i_launcher['path_manual']))

    if i_launcher['path_trailer']:
        launchers[launcherID]['path_trailer'] = i_launcher['path_trailer']
        log.debug('Imported path_trailer "{}"'.format(i_launcher['path_trailer']))

    # --- Launcher assets/artwork ---
    if i_launcher['Asset_Prefix']:
        launchers[launcherID]['Asset_Prefix'] = i_launcher['Asset_Prefix']
        log.debug('Imported Asset_Prefix "{}"'.format(i_launcher['Asset_Prefix']))
    Asset_Prefix = i_launcher['Asset_Prefix']
    # >> Look at autoconfig_import_category() for a reference implementation.
    if Asset_Prefix:
        log.debug('Asset_Prefix non empty. Looking for asset files.')
        (Asset_Prefix_head, Asset_Prefix_tail) = os.path.split(Asset_Prefix)
        log.debug('Effective Asset_Prefix "{}"'.format(Asset_Prefix))
        log.debug('Asset_Prefix_head      "{}"'.format(Asset_Prefix_head))
        log.debug('Asset_Prefix_tail      "{}"'.format(Asset_Prefix_tail))
        if Asset_Prefix_head:
            log.debug('Asset_Prefix head not empty')
            asset_dir_FN = FileName(import_FN.getDir()).pjoin(Asset_Prefix_head)
            norm_asset_dir_FN = FileName(os.path.normpath(asset_dir_FN.getPath()))
            effective_Asset_Prefix = Asset_Prefix_tail
        else:
            log.debug('Asset_Prefix head is empty. Assets in same dir as XML file')
            asset_dir_FN = FileName(import_FN.getDir())
            norm_asset_dir_FN = FileName(os.path.normpath(asset_dir_FN.getPath()))
            effective_Asset_Prefix = Asset_Prefix_tail
        log.debug('import_FN              "{}"'.format(import_FN.getPath()))
        log.debug('asset_dir_FN           "{}"'.format(asset_dir_FN.getPath()))
        log.debug('norm_asset_dir_FN      "{}"'.format(norm_asset_dir_FN.getPath()))
        log.debug('effective_Asset_Prefix "{}"'.format(effective_Asset_Prefix))

        # Get a list of all files in the directory pointed by Asset_Prefix and use this list as
        # a file cache. This list has filenames withouth path.
        log.debug('Scanning files in dir "{}"'.format(norm_asset_dir_FN.getPath()))
        file_list = sorted(os.listdir(norm_asset_dir_FN.getPath()))
        log.debug('Found {} files'.format(len(file_list)))
        # log.debug('--- File list ---')
        # for file in file_list: log.debug('--- "{}"'.format(file))
    else:
        log.debug('Asset_Prefix empty. Not looking for any asset files.')
        norm_asset_dir_FN = None
        effective_Asset_Prefix = ''
        file_list = []

    # Traverse list of category assets and search for image files for each asset
    for laun_asset in LAUNCHER_ASSET_ID_LIST:
        # Bypass trailers now
        if laun_asset == ASSET_TRAILER_ID: continue

        # >> Look for assets
        AInfo = assets_get_info_scheme(laun_asset)
        log.debug('>> Asset "{}"'.format(AInfo.name))
        asset_file_list = autoconfig_search_asset_file_list(effective_Asset_Prefix, AInfo, norm_asset_dir_FN, file_list)
        # --- Create image list for selection dialog ---
        listitems_list = []
        listitems_asset_paths = []
        # >> Current image if found
        current_FN = FileName(launchers[launcherID][AInfo.key])
        if current_FN.exists():
            log.debug('Current asset found "{}"'.format(current_FN.getPath()))
            asset_listitem = xbmcgui.ListItem(label = 'Current image', label2 = current_FN.getPath())
            asset_listitem.setArt({'icon' : current_FN.getPath()})
            listitems_list.append(asset_listitem)
            listitems_asset_paths.append(current_FN.getPath())
        else:
            log.debug('Current asset NOT found "{}"'.format(current_FN.getPath()))
        # >> Image in <s_icon>, <s_fanart>, ... tags if found
        tag_asset_FN = FileName(i_launcher[AInfo.key])
        if tag_asset_FN.exists():
            log.debug('<{}> tag found "{}"'.format(AInfo.key, tag_asset_FN.getPath()))
            asset_listitem = xbmcgui.ListItem(label = 'XML <{}> image'.format(AInfo.key),
                                              label2 = tag_asset_FN.getPath())
            asset_listitem.setArt({'icon' : tag_asset_FN.getPath()})
            listitems_list.append(asset_listitem)
            listitems_asset_paths.append(tag_asset_FN.getPath())
        else:
            log.debug('<{}> tag NOT found "{}"'.format(AInfo.key, tag_asset_FN.getPath()))
        # >> Images found in XML configuration via <Asset_Prefix> tag
        image_count = 1
        for asset_file_name in asset_file_list:
            log.debug('Asset_Prefix found "{}"'.format(asset_file_name))
            asset_FN = FileName(asset_file_name)
            asset_listitem = xbmcgui.ListItem(label = 'Asset_Prefix #{} "{}"'.format(image_count, asset_FN.getBase()),
                                              label2 = asset_file_name)
            asset_listitem.setArt({'icon' : asset_file_name})
            listitems_list.append(asset_listitem)
            listitems_asset_paths.append(asset_FN.getPath())
            image_count += 1
        # If list is empty at this point no images were found at all.
        if not listitems_list:
            log.debug('listitems_list is empty. Keeping {} as it was.'.format(AInfo.name))
            continue
        # No image
        asset_listitem = xbmcgui.ListItem(label = 'No image')
        asset_listitem.setArt({'icon' : 'DefaultAddonNone.png'})
        listitems_list.append(asset_listitem)
        listitems_asset_paths.append('')

        title_str = 'Launcher "{}". Choose {} file'.format(i_launcher['name'], AInfo.name)
        ret_idx = KodiSelectDialog(title_str, listitems_list, useDetails = True).executeDialog()
        if ret_idx is None: return

        # Set asset field
        launchers[launcherID][AInfo.key] = listitems_asset_paths[ret_idx]
        log.debug('Set launcher artwork "{}" = "{}"'.format(AInfo.key, listitems_asset_paths[ret_idx]))

    # Rename ROMS JSON/XML only if there is a change in filenames.
    # Regenerate roms_base_noext and rename old one if necessary.
    old_roms_base_noext = launchers[launcherID]['roms_base_noext']
    category_name       = categories[categoryID]['m_name'] if categoryID in categories else CATEGORY_ADDONROOT_ID
    new_roms_base_noext = fs_get_ROMs_basename(category_name, new_launcher_name, launcherID)
    log.debug('old_roms_base_noext "{}"'.format(old_roms_base_noext))
    log.debug('new_roms_base_noext "{}"'.format(new_roms_base_noext))
    if old_roms_base_noext != new_roms_base_noext:
        log.debug('Renaming JSON/XML launcher databases')
        launchers[launcherID]['roms_base_noext'] = new_roms_base_noext
        fs_rename_ROMs_database(ROMS_DIR, old_roms_base_noext, new_roms_base_noext)
    else:
        log.debug('Not renaming ROM databases (old and new names are equal)')

# Search for asset files and return a list of found asset files.
# Get a non-recursive list of all files on the directory the XML configuration file is. Then,
# scan this list for asset matching.
#
# Search patterns (<> is mandatory, [] is optional):
#
#   A) <asset_path_prefix>_<icon|fanart|banner|poster|clearlogo>[_Comment].<asset_extensions>
#   B) <asset_path_prefix>_<icon|fanart|banner|poster|clearlogo>_N[_Comment].<asset_extensions>
#   C) <asset_path_prefix>_<icon|fanart|banner|poster|clearlogo>_NN[_Comment].<asset_extensions>
#
# N is a number [0-9]
# Comment may have spaces
def search_asset_file_list(asset_prefix, AInfo, norm_asset_dir_FN, file_list):
    log.debug('autoconfig_search_asset_file_list() BEGIN asset infix "{}"'.format(AInfo.fname_infix))

    # >> Traverse list of filenames (no paths)
    filename_noext = asset_prefix + '_' + AInfo.fname_infix
    # log.debug('filename_noext "{}"'.format(filename_noext))
    img_ext_regexp = asset_get_regexp_extension_list(IMAGE_EXTENSION_LIST)
    # log.debug('img_ext_regexp "{}"'.format(img_ext_regexp))
    pattern = '({})([ \w]*?)\.{}'.format(filename_noext, img_ext_regexp)
    log.debug('autoconfig_search_asset_file_list() pattern "{}"'.format(pattern))

    # --- Search for files in case A, B and C ---
    asset_file_list = []
    for file in file_list:
        # log.debug('Testing "{}"'.format(file))
        m = re.match(pattern, file)
        if m:
            # log.debug('MATCH   "{}"'.format(m.group(0)))
            asset_full_path = norm_asset_dir_FN.pjoin(file)
            # log.debug('Adding  "{}"'.format(asset_full_path.getPath()))
            asset_file_list.append(asset_full_path.getPath())
    # log.debug('autoconfig_search_asset_file_list() END')

    return asset_file_list
