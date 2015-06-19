# coding=utf-8
import asyncio


class Pinger(object):

    def __init__(self, file_path=None, servers_list=None):
        if servers_list is None:
            servers_list = []

        self.file_path = file_path
        self.servers_list = servers_list
        self.pings = None

    @staticmethod
    def get_stats_from_ping_data(stats):
        """
        >>> data = ['statistics', '---\\n5', 'packets', 'transmitted,', '5']
        >>> data += ['received,', '0%', 'packet', 'loss,', 'time', '4001ms\\nrtt']
        >>> data += ['min/avg/max/mdev','=', '79.832/86.519/88.649/3.367', 'ms']
        >>> Pinger.get_stats_from_ping_data(data)
        [79.832, 86.519, 88.649, 3.367, 5.0]

        Return stats from ping output data.
        :param stats:
        :return:
        """

        out = []
        for i, x in enumerate(reversed(stats[:])):
            data = str(x).split('/')
            for d in data:
                try:
                    out.append(float(d))
                except ValueError:
                    continue

        return out

    def read_servers(self):
        """
        >>> f = Pinger('test.servers.list')
        >>> f.read_servers()
        [['Canada, Toronto (PPTP/L2TP)', 'tr-ca.boxpnservers.com']]

        Read city and server url from file.

        File example:
        ```
        Canada, Toronto (PPTP/L2TP): tr-ca.boxpnservers.com
        Canada, Toronto (SSTP): sstp-tr-ca.boxpnservers.com

        ```
        """
        with open(self.file_path, 'r') as servers_list:
            servers = filter(
                lambda y: y != '\n' and 'SSTP' not in y,
                [x for x in servers_list.readlines()]
            )

        process_server = lambda s: list(map(lambda x: x.strip(), s.split(':')))
        self.servers_list = list(map(process_server, servers))

    @staticmethod
    def ping(city, url):
        """
        Ping server.
        :param city:
        :param url:
        :return:
        """
        timeout = None
        packets_count = 5
        try:
            _ping = asyncio.create_subprocess_shell(
                "ping -n -c {} {}".format(packets_count, url),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            _ping = yield from _ping
            yield from _ping.wait()
            out = yield from _ping.stdout.read()
            out = out.decode().rstrip()
            if out:
                statistics = Pinger.get_stats_from_ping_data(
                    out[out.index('statistics ---'):].split(' ')
                )

                try:
                    # received_packets = statistics.pop()
                    # minimum = statistics.pop()
                    # average = statistics.pop()
                    # maximum = statistics.pop()
                    # stddev = statistics.pop()
                    # percent = (received_packets / packets_count) * 100
                    timeout = statistics[-3]
                except IndexError:
                    pass
                    # print "no data for one of minimum,maximum,average,packet"
            else:
                pass
                # print 'No ping'

        except Exception as a:
            print(a)
            # print "Couldn't get a ping"
        finally:
            return city, url, timeout

    def print_results(self):
        """
        Print results in stdout
        :param pings:
        :return:
        """
        assert self.pings, list
        template = '{:<3}{:<40}{:<25}{:<10}'
        print(template.format('#', 'City', 'Hostname', 'Ping'))
        for i, p in enumerate(self.pings, start=1):
            print('-' * 75)
            print(template.format(i, *p))

    @asyncio.coroutine
    def process(self):
        """
        Process servers
        :type file_path: 'path to file with servers'
        :return:
        """
        pings = yield from asyncio.gather(
            *[self.ping(*s) for s in self.servers_list]
        )
        self.pings = list(sorted(
            filter(lambda x: x[2] is not None, pings),
            key=lambda x: x[2],
            reverse=True
        ))

    def run(self):
        del self.servers_list[:]
        self.read_servers()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.process())
        loop.close()

if __name__ == '__main__':
    p = Pinger('servers.list')
    p.run()
    p.print_results()
