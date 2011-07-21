#!/bin/bash
hosts="escondido giulia.local nessa localhost"
out="out/"
mkdir -p out
for host in $hosts; do
	ssh $host patience --yaml -s status > $out/$host.yaml
done