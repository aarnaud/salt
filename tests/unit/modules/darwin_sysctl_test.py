# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Nicole Thomas <nicole@satlstack.com>`
'''

# Import Python Libs

# Import Salt Libs
from salt.modules import darwin_sysctl
from salt.exceptions import CommandExecutionError

# Import Salt Testing Libs
from salttesting import TestCase
from salttesting.helpers import ensure_in_syspath
from salttesting.mock import MagicMock, mock_open, patch, call

ensure_in_syspath('../../')

# Globals
darwin_sysctl.__salt__ = {}

SYSCTL_ALL = 'kern.ostype = Darwin\n' \
             'kern.osrelease = 13.1.0'


class DarwinSysctlTestCase(TestCase):
    '''
    TestCase for salt.modules.darwin_sysctl module
    '''

    def test_get(self):
        '''
        Tests the return of get function
        '''
        mock_cmd = MagicMock(return_value='foo')
        with patch.dict(darwin_sysctl.__salt__, {'cmd.run': mock_cmd}):
            self.assertEqual(darwin_sysctl.get('kern.ostype'), 'foo')

    def test_assign_cmd_failed(self):
        '''
        Tests if the assignment was successful or not
        '''
        cmd = {'pid': 3548, 'retcode': 1, 'stderr': '',
               'stdout': 'net.inet.icmp.icmplim: 250 -> 50'}
        mock_cmd = MagicMock(return_value=cmd)
        with patch.dict(darwin_sysctl.__salt__, {'cmd.run_all': mock_cmd}):
            self.assertRaises(CommandExecutionError,
                              darwin_sysctl.assign,
                              'net.inet.icmp.icmplim', 50)

    def test_assign(self):
        '''
        Tests the return of successful assign function
        '''
        cmd = {'pid': 3548, 'retcode': 0, 'stderr': '',
               'stdout': 'net.inet.icmp.icmplim: 250 -> 50'}
        ret = {'net.inet.icmp.icmplim': '50'}
        mock_cmd = MagicMock(return_value=cmd)
        with patch.dict(darwin_sysctl.__salt__, {'cmd.run_all': mock_cmd}):
            self.assertEqual(darwin_sysctl.assign(
                'net.inet.icmp.icmplim', 50), ret)

    @patch('os.path.isfile', MagicMock(return_value=False))
    def test_persist_no_conf_failure(self):
        '''
        Tests adding of config file failure
        '''
        mock = mock_open()
        with patch('salt.utils.fopen', mock_open(read_data=mock)) as m_open:
            helper_open = m_open()
            helper_open.write.assertRaises(CommandExecutionError,
                                           darwin_sysctl.persist,
                                           'net.inet.icmp.icmplim',
                                           50, config=None)

    @patch('os.path.isfile', MagicMock(return_value=False))
    def test_persist_no_conf_success(self):
        '''
        Tests successful add of config file when previously not one
        '''
        mock = mock_open()
        with patch('salt.utils.fopen', mock_open(read_data=mock)) as m_open:
            darwin_sysctl.persist('net.inet.icmp.icmplim', 50)
            helper_open = m_open()
            helper_open.write.assert_called_once_with(
                '#\n# Kernel sysctl configuration\n#\n')

    @patch('os.path.isfile', MagicMock(return_value=True))
    def test_persist_success(self):
        '''
        Tests successful write to existing sysctl file
        '''
        to_write = '#\n# Kernel sysctl configuration\n#\n'
        m_calls_list = [call.writelines(['net.inet.icmp.icmplim=50'])]
        with patch('salt.utils.fopen', mock_open(read_data=to_write)) as m_open:
            darwin_sysctl.persist('net.inet.icmp.icmplim', 50, config=to_write)
            helper_open = m_open()
            calls_list = helper_open.method_calls
            self.assertEqual(calls_list, m_calls_list)


if __name__ == '__main__':
    from integration import run_tests
    run_tests(DarwinSysctlTestCase, needs_daemon=False)
