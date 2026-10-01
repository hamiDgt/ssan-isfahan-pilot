#!/bin/bash
# Downloads the three OSM anchors for District 6 from Overpass.
BBOX="32.5416814,51.6627253,32.6446693,51.7650088"
mkdir -p ~/ssan-data/osm
curl --max-time 120 -G --data-urlencode 'data=[out:json][timeout:60];relation["boundary"="administrative"]["name"~"[6۶]"](32.50,51.40,32.80,51.90);out geom;' "http://overpass-api.de/api/interpreter" -o ~/ssan-data/osm/district6_boundary.json
curl --max-time 300 -G --data-urlencode "data=[out:json][timeout:120];way[\"building\"]($BBOX);out center;" "http://overpass-api.de/api/interpreter" -o ~/ssan-data/osm/d6_buildings.json
curl --max-time 120 -G --data-urlencode 'data=[out:json][timeout:60];(node["highway"="bus_stop"]('"$BBOX"');node["railway"~"station|halt"]('"$BBOX"');node["public_transport"="station"]('"$BBOX"'););out body;' "http://overpass-api.de/api/interpreter" -o ~/ssan-data/osm/d6_transit.json
echo "OSM anchors saved to ~/ssan-data/osm/"
