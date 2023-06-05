#!/usr/bin/python3

# -*- coding: utf-8 -*-

import sys
import os
import json
import re

from dotenv import load_dotenv
from pathlib import Path

import aiofiles
import asyncio
import asyncio_mqtt as aiomqtt

load_dotenv(dotenv_path=Path('/etc/pihole-MQTT/.env'))

MQTT_HOST = os.environ.get('MQTT_HOST')
MQTT_PORT = os.environ.get('MQTT_PORT')
MQTT_USER = os.environ.get('MQTT_USER')
MQTT_PASS = os.environ.get('MQTT_PASS')

MQTT_TOPIC_WILL = os.environ.get('MQTT_TOPIC_WILL')
MQTT_TOPIC_DNSCONFIG = os.environ.get('MQTT_TOPIC_DNSCONFIG')

MQTT_RECONNECT_INTERVAL = os.environ.get('MQTT_RECONNECT_INTERVAL') or 5


class DnsEntityConfig():
    Members = {}

    def __init__(self, name, **kwargs):
        self.name = name
        self.configfile = kwargs['configfile']
        self.searchpattern = kwargs['searchpattern']
        self.persistpath = kwargs['persistpath']
        self.add_command = kwargs['add_command']
        self.del_command = kwargs['del_command']
        self.source_data = None
        self.dest_data = None

        DnsEntityConfig.Members.update({self.name: self})

    def __str__(self):
        return self.name

    async def parse_configfile(self):
        result = []
        try:
            async with aiofiles.open(self.configfile, mode='r') as file:
                async for line in file:
                    r = re.search(self.searchpattern, line.strip())
                    if r is not None:
                        result.append(list(r.group(1, 2)))
        except:
            pass

        self.dest_data = result

    async def persist_data(self):
        try:
            async with aiofiles.open(self.persistpath, mode='w') as file:
                for d in self.payload:
                    line = "%s %s" % (d[0], d[1])
                    await file.write(line)
        except:
            pass

    async def compare_data(self):
        src = set(map(tuple, self.source_data))
        dst = set(map(tuple, self.dest_data))

        return {
            'add': src - dst,
            'del': dst - src,
            'equ': src & dst,
        }


DNS = DnsEntityConfig(
    "dns",
    configfile='/etc/pihole/custom.list',
    searchpattern='\A([\w.-]+) ([\w.-]+)',
    persistpath='/etc/pihole-MQTT/dns.list',
    add_command='-a addcustomdns %s %s false',
    del_command='-a removecustomdns %s %s false',
)
CNAME = DnsEntityConfig(
    "cname",
    configfile='/etc/dnsmasq.d/05-pihole-custom-cname.conf',
    searchpattern='\Acname=([\w.-]+),([\w.-]+)',
    persistpath='/etc/pihole-MQTT/cname.list',
    add_command='-a addcustomcname %s %s false',
    del_command='-a removecustomcname %s %s false',
)


async def on_topic_dnsconfig(payload: str):
    for name, inst in DnsEntityConfig.Members.items():
        try:
            inst.source_data = payload[name]
        except:
            pass

    data_changed = False
    num_entries = 0

    for e in DnsEntityConfig.Members.values():
        await e.persist_data()
        await e.parse_configfile()

        tasks = await e.compare_data()

        # Add actions
        for s in tasks['add']:
            cmd = e.add_command % (s[0], s[1])
            await pihole_command(cmd, "  [ADD COMMAND] " + cmd)

        # Remove actions
        for s in tasks['del']:
            cmd = e.del_command % (s[0], s[1])
            await pihole_command(cmd, "  [DEL COMMAND] " + cmd)

        data_changed = data_changed or len(
            tasks['add']) > 0 or len(tasks['del']) > 0

        num_entries += len(tasks['equ']) + \
            len(tasks['add']) + len(tasks['del'])

    if data_changed:
        await pihole_command('restartdns', 'Reloaded pihole dns resolver.')
    else:
        print('Received data, but nothing changed.', file=sys.stdout)

    print(f'{num_entries} dns/cname entries currently in sync.', file=sys.stdout)


async def pihole_command(command, message_pre=None, message_post=None):
    if message_pre:
        print(message_pre, file=sys.stdout)

    os.system(f'pihole {command}')

    if message_post:
        print(message_post, file=sys.stdout)


async def main():
    configuration = {
        "hostname": MQTT_HOST,
        "username": MQTT_USER,
        "password": MQTT_PASS,
        "client_id": "pihole-mqtt",
        "will": aiomqtt.Will(
            topic=MQTT_TOPIC_WILL,
            payload=False,
            qos=1,
            retain=True
        )
    }

    callbacks = {
        MQTT_TOPIC_DNSCONFIG: on_topic_dnsconfig
    }

    while True:
        try:
            async with aiomqtt.Client(**configuration) as client:
                print('Conntected to broker.', file=sys.stdout)
                await client.publish(MQTT_TOPIC_WILL, payload=True)

                async with client.messages() as messages:
                    [await client.subscribe(t) for t in callbacks]

                    async for message in messages:
                        payload = json.loads(message.payload.decode())

                        for topic, cb in callbacks.items():
                            if message.topic.matches(topic):
                                await cb(payload)

        except aiomqtt.MqttError as error:
            await client.publish(MQTT_TOPIC_WILL, payload=False)
            print(
                f'Error "{error}". Reconnecting in {MQTT_RECONNECT_INTERVAL} seconds.', file=sys.stderr)
            await asyncio.sleep(MQTT_RECONNECT_INTERVAL)


# https://github.com/sbtinstruments/asyncio-mqtt
# Change to the "Selector" event loop if platform is Windows
if sys.platform.lower() == "win32" or os.name.lower() == "nt":
    # only import if platform/os is win32/nt, otherwise "WindowsSelectorEventLoopPolicy" is not present
    from asyncio import (
        set_event_loop_policy,
        WindowsSelectorEventLoopPolicy
    )
    # set the event loop
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())


loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
