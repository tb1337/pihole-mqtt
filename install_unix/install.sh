echo "Stop service"

systemctl stop pihole-mqtt.service
systemctl disable pihole-mqtt.service

echo "Copy files"

cp ./pihole-mqtt.service /lib/systemd/system/

cp ../async.py /usr/bin/pihole-MQTT
chmod +x /usr/bin/pihole-MQTT

echo "/etc directory check"

[ -d /etc/pihole-MQTT ] || mkdir /etc/pihole-MQTT

if [ ! -f /etc/pihole-MQTT/.env ]
then
    touch /etc/pihole-MQTT/.env

    echo "MQTT_HOST = 'your host ip or dns name'" >> /etc/pihole-MQTT/.env
    echo "MQTT_PORT = 1883" >> /etc/pihole-MQTT/.env
    echo "MQTT_USER = 'your mqtt username'" >> /etc/pihole-MQTT/.env
    echo "MQTT_PASS = 'your mqtt password'" >> /etc/pihole-MQTT/.env
    echo "MQTT_TOPIC_WILL = 'mikrotik/pihole-mqtt'" >> /etc/pihole-MQTT/.env
    echo "MQTT_TOPIC_DNSCONFIG = 'mikrotik/dns-config'" >> /etc/pihole-MQTT/.env
    echo "MQTT_RECONNECT_INTERVAL = 5" >> /etc/pihole-MQTT/.env
fi

echo "Daemon reload"

systemctl daemon-reload

echo "Enable service"

systemctl enable pihole-mqtt.service
systemctl start pihole-mqtt.service
systemctl status pihole-mqtt.service