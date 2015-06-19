======
Pinger
======

Pinger based on asyncio library.

Pinger collect servers pings and show it in reversed order (first worst ping,
last best ping).

===========
Instalation
===========

.. code-block:: bash

    pip install asyncio_pinger

=====
Usage
=====

Create file like this:

.. code-block:: text

    Argentina, Buenos Aires (PPTP/L2TP): bn-ar.boxpnservers.com
    Argentina, Buenos Aires (SSTP): sstp-bn-ar.boxpnservers.com


Run Python

.. code-block:: python

    from asyncio_pinger.main import Pinger

    p = Pinger(path_to_file)
    p.run()
    p.print_results()