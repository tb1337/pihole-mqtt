# pihole-mqtt

Transmit configuration data to pihole via MQTT.

Currently it is designed to receive data over MQTT by a MikroTik RouterOS device. But however, it depends only on the DNS payload. So it could be any device you want.

## Use Case

PiHole is my independent DNS resolver at home. But RouterOS takes care of DHCP, hostnames and dynamically creates DNS entries. I want to share that with my PiHole DNS, so it gets updated with fresh local DNS data whenever RouterOS changes something.

## Information

Its a private script. Currently, I don't use a configuration environment and so commited my local credentials. Blame me, but its uncritical. You cannot access the mentioned host, you cannot access my MQTT broker, its just a random password, it is useless for you.

I will update that in the future, to make configuration by environment vars.

## Installation

### Python

Create a folder wherever you want, possibly on your home folder. Example:

```
mkdir pihole-mqtt
cd pihole-mqtt

git clone https://github.com/tb1337/pihole-mqtt.git .

python3 -m venv .venv
source .venv/bin/activate

python3 -m pip install --upgrade pip
pip install -r ./requirements.txt
```

Finally,
`python3 async.py`

### RouterOS

Check out the install_routeros folder:

| Script   | Description                                                                                                                        |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| mqtt.rsc | Will be renamed into dns-config.rsc soon. Collects static DNS and CNAME data from your RouterOS and sends it via your MQTT broker. |

### Unix Service

In the install_unix folder, I added a simple installation shell script, which does everything on UNIX side for you.

```
cd ./install_unix
chmod +x install.sh
./install.sh
```
