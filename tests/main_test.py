import unittest, mock, os, sys
from mock import *
from fakes import *
from distutils.version import LooseVersion
import xml.etree.ElementTree as ET

import xbmcaddon

import resources.main as main
from resources.main import AEL_Paths

from resources.constants import *
from resources.utils import *

class Test_maintests(unittest.TestCase):
    
    ROOT_DIR = ''
    TEST_DIR = ''
    TEST_ASSETS_DIR = ''

    @classmethod
    def setUpClass(cls):
        set_log_level(LOG_DEBUG)
        
        cls.TEST_DIR = os.path.dirname(os.path.abspath(__file__))
        cls.ROOT_DIR = os.path.abspath(os.path.join(cls.TEST_DIR, os.pardir))
        cls.TEST_ASSETS_DIR = os.path.abspath(os.path.join(cls.TEST_DIR,'assets/'))
                
        print('ROOT DIR: {}'.format(cls.ROOT_DIR))
        print('TEST DIR: {}'.format(cls.TEST_DIR))
        print('TEST ASSETS DIR: {}'.format(cls.TEST_ASSETS_DIR))
        print('---------------------------------------------------------------------------')
        
    def _read_file(self, path):
        with open(path, 'r') as f:
            return f.read()        

    def _read_file_xml(self, path):
        data = self._read_file(path)
        root = ET.fromstring(data)
        return root

    # todo: replace by moving settings to external class and mock a simple dictionary
    def mocked_settings(arg):

        if arg == 'scan_metadata_policy' or arg == 'media_state_action' \
            or arg == 'metadata_scraper_mode' or arg == 'asset_scraper_mode' or arg == 'metadata_scraper' \
            or arg == 'asset_scraper' or arg =='scraper_metadata' \
            or arg == 'scraper_title' or  arg =='scraper_snap' or arg == 'scraper_bfront' \
            or arg == 'scraper_bback' or arg == 'scraper_cart' \
            or arg == 'scraper_fanart' or arg == 'scraper_banner' or arg =='scraper_clearlogo' \
            or arg =='scraper_flyer' or arg =='scraper_cabinet' \
            or arg == 'scraper_cpanel' or arg == 'scraper_pcb' or arg =='scraper_flyer_mame' \
            or arg == 'audit_unknown_roms' or arg == 'audit_1G1R_region':
            return 10
        
        if arg == 'scan_asset_policy':
            return 8

        if arg == 'log_level':
            return 1

        if arg == 'delay_tempo':
            return 0
        
        return '1'
           
    @patch('resources.main.sys')
    @patch('resources.utils.FileName.loadFileToStr')
    @patch('resources.main.__addon__.getSetting', side_effect = mocked_settings)       
    def test_when_running_the_plugin_no_errors_occur(self, mock_addon, mock_xmlreader, mock_sys):
        
        # arrange
        mock_xmlreader.return_value = self._read_file_xml(self.TEST_ASSETS_DIR + "\\ms_categories.xml")

        mock_sys.args.return_value = ['contenttype', 'noarg']
        main.__addon_version__ = '0.0.0'
        target = main()
        
        # act
        target.run_plugin()

        # assert
        pass
    
    @patch('resources.main.xbmc.Keyboard.getText', autospec=True)
    @patch('resources.main.__addon__.getSetting', side_effect = mocked_settings)
    def test_when_adding_new_category_the_correct_data_gets_stored(self, mock_addon, mock_keyboard):
        
        # arrange
        catfile = FakeFile('categories.xml')
        catfile.setFakeContent(self._read_file(self.TEST_ASSETS_DIR + "\\ms_categories.xml"))
    
        expected =  'MyTestCategory'

        mock_keyboard.return_value = expected
        target = main
        target.g_PATHS.CATEGORIES_FILE_PATH = catfile
        target.m_get_settings()
        target.m_bootstrap_instances()
        
        # act
        target.m_command_add_new_category()

        contents = catfile.getFakeContent()
        root = ET.fromstring(unicode(contents))
        actual = root[0][0]
        print(actual)

        # assert
        self.assertIn(expected, actual)
            
    @patch('resources.main.__addon__.getSetting', side_effect = mocked_settings)
    @patch('resources.utils.FileName.loadFileToStr')
    def test_when_rendering_roms_it_will_return_a_proper_result(self, mock_xmlreader, mock_addon):
        
        # arrange
        mock_xmlreader.return_value = self._read_file_xml(self.TEST_ASSETS_DIR + "\\ms_categories.xml")

        target = main
        target.m_get_settings()
        target.m_bootstrap_instances()
        target.addon_handle = 0

        launcherID = '2220af27d0937d78ce7bc8317f5e853a'

        # act
        target._command_render_roms(None, launcherID)
     
    @patch('resources.main.__addon__.getSetting', side_effect = mocked_settings)
    @patch('resources.utils.FileName.loadFileToStr')
    def test_rendering_categories(self, mock_xmlreader, mock_addon):
        
        # arrange
        mock_xmlreader.return_value = self._read_file(self.TEST_ASSETS_DIR + "\\ms_categories.xml")
        
        target = main
        target.m_get_settings()
        target.m_bootstrap_instances()
        target.base_url = ''
        target.addon_handle = 0

        # act
        category_list = target.g_ObjectFactory.find_category_all()
        for category in category_list:
            target.m_gui_render_category_row(category)
        

    def test_migrations(self):
        
        # arrange
        shutil.copy2(self.TEST_ASSETS_DIR + "\\ms_categories.xml", self.TEST_ASSETS_DIR + "\\categories.xml")
        main.__addon_version__ = '0.9.9-alpha'

        #target = main.Main()
        main.g_PATHS = AEL_Paths()
        main.g_PATHS.ADDON_CODE_DIR = FakeFile(self.ROOT_DIR)
        main.g_PATHS.ADDON_DATA_DIR = FakeFile(self.TEST_ASSETS_DIR)

        v_from = LooseVersion('0.0.0')

        # act
        main.m_execute_migrations(v_from)


if __name__ == '__main__':
    unittest.main()
