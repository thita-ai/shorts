#!/bin/sh
# Real Greater Tokyo geography from OpenStreetMap: main-line rail + coastline (about 26 MB) -> data/osm.json
mkdir -p data
curl -s -m 300 -A "thita-shorts" -o data/osm.json --data-urlencode \
  'data=[out:json][timeout:180];(way["railway"="rail"]["usage"="main"](35.15,139.1,36.1,140.5);way["natural"="coastline"](34.9,138.9,36.3,140.7););out geom;' \
  https://overpass-api.de/api/interpreter
