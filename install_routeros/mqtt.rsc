:local mqttBroker "iot"
:local mqttTopic "mikrotik/dns-config"

:local jsonDNS ""
:local jsonCNAME ""

:foreach dnsentry in [/ip dns static find] do={
    :local name [/ip dns static get value-name=name $dnsentry]
    :local type [/ip dns static get value-name=type $dnsentry]
    :local addr [/ip dns static get value-name=address $dnsentry]

    :if ($type = "CNAME") do={
        :local cname [/ip dns static get value-name=cname $dnsentry]
        :set jsonCNAME "$jsonCNAME\n,{\"match\":\"$name\",\"value\":\"$cname\"}"
    } else={
        :set jsonDNS "$jsonDNS\n,{\"match\":\"$addr\",\"value\":\"$name\"}"
    }
}

:set jsonDNS [:pick $jsonDNS 2 [[:len $jsonDNS] -2 ]]
:set jsonCNAME [:pick $jsonCNAME 2 [[:len $jsonCNAME] -2 ]]

:local json "{ \"dns\":[ $jsonDNS ], \"cname\":[ $jsonCNAME ] }"

:log info "[dnsexport] sending data to MQTT broker..."

/iot/mqtt/publish broker=$mqttBroker qos=1 retain=yes topic=$mqttTopic message=$json

:log info "[dnsexport] done!"