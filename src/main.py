# coding=utf-8
import asyncio


def get_stats_from_ping_data(stats):
    """
    >>> data = ['statistics', '---\\n5', 'packets', 'transmitted,', '5']
    >>> data += ['received,', '0%', 'packet', 'loss,', 'time', '4001ms\\nrtt']
    >>> data += ['min/avg/max/mdev','=', '79.832/86.519/88.649/3.367', 'ms']
    >>> get_stats_from_ping_data(data)
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


def read_servers(file_path='servers.list'):
    """
    >>> read_servers('test.servers.list')
    [['Canada, Toronto (PPTP/L2TP)', 'tr-ca.boxpnservers.com']]

    Read city and server url from file.

    File example:
    ```
    Canada, Toronto (PPTP/L2TP): tr-ca.boxpnservers.com
    Canada, Toronto (SSTP): sstp-tr-ca.boxpnservers.com

    ```
    :param file_path:
    :return: [['Canada, Toronto (PPTP/L2TP)', 'tr-ca.boxpnservers.com']]
    """
    with open(file_path, 'r') as servers_list:
        servers = filter(
            lambda y: y != '\n' and 'SSTP' not in y,
            [x for x in servers_list.readlines()]
        )

    process_server = lambda s: list(map(lambda x: x.strip(), s.split(':')))
    return list(map(process_server, servers))


def ping(city, url):
    """
    Ping server.
    :param city:
    :param url:
    :return:
    """
    timeout = 10 ** 5
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
            statistics = get_stats_from_ping_data(
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


def print_results(pings):
    """
    Print results in stdout
    :param pings:
    :return:
    """
    template = '{:<3}{:<40}{:<25}{:<10}'
    print(template.format('#', 'City', 'Hostname', 'Ping'))
    for i, p in enumerate(pings, start=1):
        print('-' * 75)
        print(template.format(i, *p))


@asyncio.coroutine
def process():
    """
    Process servers
    :return:
    """
    pings = yield from asyncio.gather(*[ping(*s) for s in read_servers()])
    print_results(sorted(
        filter(lambda x: x[2] < 10 ** 3, pings),
        key=lambda x: x[2],
        reverse=True
    ))


def run():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(process())
    loop.close()

if __name__ == '__main__':
    run()
