# coding=utf-8
import asyncio

import asyncio_pinger.main
import unittest


class PingerTest(unittest.TestCase):
    def setUp(self):
        self.pinger = asyncio_pinger.main.Pinger('test.servers.list')
        self.loop = asyncio.get_event_loop()

    def _list(self, attr='servers_list'):
        attr = getattr(self.pinger, attr)
        self.assertTrue(isinstance(attr, list))
        self.assertTrue(len(attr) == 1)
        self.assertTrue(isinstance(attr[0], (list, tuple)))
        self.assertTrue(attr[0][0] == 'Canada, Toronto (PPTP/L2TP)')
        self.assertTrue(attr[0][1] == 'tr-ca.boxpnservers.com')

    def test_read_servers(self):
        self.pinger.read_servers()
        self._list()

    def test_get_stats_from_ping_data(self):
        stats = [
            'statistics', '---\\n5', 'packets', 'transmitted,', '5',
            'received,', '0%', 'packet', 'loss,', 'time', '4001ms\\nrtt',
            'min/avg/max/mdev', '=', '79.832/86.519/88.649/3.367', 'ms'
        ]
        stats_01 = asyncio_pinger.main.Pinger.get_stats_from_ping_data(stats)
        self.assertEqual(stats_01, [79.832, 86.519, 88.649, 3.367, 5.0])
        stats_02 = self.pinger.get_stats_from_ping_data(stats)
        self.assertEqual(stats_02, [79.832, 86.519, 88.649, 3.367, 5.0])
        self.assertEqual(stats_01, stats_02)

    def test_run(self):
        self.pinger.run()
        self._list()
        self._list('pings')
        self.assertTrue(type(self.pinger.pings[0][2]) == float)
