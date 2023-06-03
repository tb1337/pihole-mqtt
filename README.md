# pihole-mqtt

Transmit configuration data to pihole via MQTT.

Currently it is designed to receive data over MQTT by a MikroTik RouterOS device. But however, it depends only on the DNS payload. So it could be any device you want.

## Use Case

PiHole is my independent DNS resolver at home. But RouterOS takes care of DHCP, hostnames and dynamically creates DNS entries. I want to share that with my PiHole DNS, so it gets updated with fresh local DNS data whenever RouterOS changes something.

## Information

Its a private script. Currently, I don't use a configuration environment and so commited my local credentials. Blame me, but its uncritical. You cannot access the mentioned host, you cannot access my MQTT broker, its just a random password, it is useless for you.

I will update that in the future, to make configuration by environment vars.
