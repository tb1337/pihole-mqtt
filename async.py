#!/usr/bin/python3

# -*- coding: utf-8 -*-

import sys
import os
import json

import aiofiles
import asyncio
import asyncio_mqtt as aiomqtt


MQTT_HOST = '192.168.42.23'
MQTT_PORT = 1883
MQTT_USER = 'pihole'
MQTT_PASS = 'QfMTx10LHqX9Nt'
MQTT_TOPIC = 'mikrotik/dns-config'
MQTT_RECONNECT_INTERVAL = 5


class Entity():
    def __init__(self, **kwargs):
        self.file_exp = kwargs['export']
        self.file_dest = kwargs['destination']
        self.line_format = kwargs['line_format']


DNS = Entity(
    export='/etc/pihole-MQTT/dns.list',
    destination='/etc/pihole/custom.list',
    line_format="%s %s\n"
)
CNAME = Entity(
    export='/etc/pihole-MQTT/cname.list',
    destination='/etc/dnsmasq.d/05-pihole-custom-cname.conf',
    line_format="cname=%s,%s\n"
)


async def parse_message(payload: str):
    await save_data(DNS, payload['dns'])
    await save_data(CNAME, payload['cname'])
    print('Received data.', file=sys.stdout)

    await do_os_magic()
    print('Reloaded pihole dns resolver.', file=sys.stdout)


async def save_data(entity: Entity, payload: list):
    try:
        async with aiofiles.open(entity.file_exp, mode='w') as file:
            for d in payload:
                line = entity.line_format % (d["match"], d["value"])
                await file.write(line)
    except:
        pass


async def do_os_magic():
    os.system(f'cp {DNS.file_exp} {DNS.file_dest}')
    os.system(f'cp {CNAME.file_exp} {CNAME.file_dest}')
    os.system(f'pihole restartdns')


async def main():
    configuration = {
        "hostname": MQTT_HOST,
        "username": MQTT_USER,
        "password": MQTT_PASS
    }

    while True:
        try:
            async with aiomqtt.Client(**configuration) as client:
                print('Conntected to broker.', file=sys.stdout)

                async with client.messages() as messages:
                    await client.subscribe(MQTT_TOPIC)

                    async for message in messages:
                        payload = json.loads(message.payload.decode())

                        if message.topic.matches(MQTT_TOPIC):
                            await parse_message(payload)
                        else:
                            pass
        except aiomqtt.MqttError as error:
            print(
                f'Error "{error}". Reconnecting in {MQTT_RECONNECT_INTERVAL} seconds.', file=sys.stderr)
            await asyncio.sleep(MQTT_RECONNECT_INTERVAL)

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
finally:
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()
