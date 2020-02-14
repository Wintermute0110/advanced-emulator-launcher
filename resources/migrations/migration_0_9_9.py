# --- Python standard library ---
import sys, os

from main import *

current_dir = os.path.dirname(os.path.abspath(__file__))
resources_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
sys.path.append(resources_dir)
from .. import *

from constants import *
from utils import *
from disk_IO import *

MIGRATION_CLASS_NAME = 'Migration_0_9_9'

#
# Release 0.9.9
# This migration will do the following upgrade actions:
#   - Add a 'type' field to each launcher, guessing the correct launcher type.
#   - todo
#
class Migration_0_9_9(Migration):
    def execute(self, addon_path, addon_data_path):
        log_info('[Migration][0.9.9] Starting migration')
        categories_file = addon_data_path.pjoin('categories.xml')

        categories = {}
        launchers = {}
        fs_load_catfile(categories_file, categories, launchers)

        for key, launcher in launchers.iteritems():
            log_info('[Migration][0.9.9] Validating launcher [{}] {}'.format(key, launcher['m_name']))

            # does not yet contain launcher type?
            if not 'type' in launcher or launcher['type'] == '':
                log_debug('[Migration][0.9.9] Launcher "{}" does not have a "type" field yet.')
                self._set_launchertype(launcher)
                
        fs_write_catfile(categories_file, categories, launchers)
        log_info('[Migration][0.9.9] Finished migration')

    def _set_launchertype(self, launcher):
        application = FileName(launcher['application'])
        name = launcher['m_name']

        if application.getPath() == RETROPLAYER_LAUNCHER_APP_NAME:
            log_debug('[Migration][0.9.9] Setting launcher "{}" with type RETROPLAYER'.format(name))
            launcher['type'] = OBJ_LAUNCHER_RETROPLAYER
            return

        if application.getPath() == LNK_LAUNCHER_APP_NAME:
            log_debug('[Migration][0.9.9] Setting launcher "{}" with type LNK'.format(name))
            launcher['type'] = OBJ_LAUNCHER_LNK
            return

        if 'rompath' in launcher and launcher['rompath'] != '':
            log_debug('[Migration][0.9.9] Setting launcher "{}" with type ROM LAUNCHER'.format(name))
            launcher['type'] = OBJ_LAUNCHER_ROM
            return
        
        launcher['type'] = OBJ_LAUNCHER_STANDALONE
        log_debug('[Migration][0.9.9] Setting launcher "{}" with type STANDALONE'.format(name))
