echo "Stop service"

systemctl stop pihole-mqtt.service
systemctl disable pihole-mqtt.service

echo "Copy files"

cp ./service/pihole-mqtt.service /lib/systemd/system/

cp ../async.py /usr/bin/pihole-MQTT
chmod +x /usr/bin/pihole-MQTT

echo "/etc directory check"

[ -d /etc/pihole-MQTT ] || mkdir /etc/pihole-MQTT

echo "Daemon reload"

systemctl daemon-reload

echo "Enable service"

systemctl enable pihole-mqtt.service
systemctl start pihole-mqtt.service
systemctl status pihole-mqtt.service