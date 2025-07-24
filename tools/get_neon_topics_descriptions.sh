#!/bin/bash

# List of topics
topics=(
reading.sensor
reading.sensor.aepg600m
reading.sensor.aepg600m_heated
reading.sensor.cmp22
reading.sensor.csat3
reading.sensor.csat3b
reading.sensor.drx8533ep_raw
reading.sensor.dualfan
reading.sensor.enviroscan
reading.sensor.g2131i_raw
reading.sensor.gmp343
reading.sensor.grape
reading.sensor.hfp01sc
reading.sensor.hivol3000
reading.sensor.hmp155
reading.sensor.l2130i_raw
reading.sensor.li191r
reading.sensor.li7200_raw
reading.sensor.li840a
reading.sensor.li850
reading.sensor.mcseries
reading.sensor.metone370380
reading.sensor.mti300ahrs
reading.sensor.mwseries
reading.sensor.nadp127tm
reading.sensor.ncon127tm
reading.sensor.nr01
reading.sensor.picarro3way
reading.sensor.pqs1
reading.sensor.pressuretransducer
reading.sensor.prt
reading.sensor.prtncon
reading.sensor.ptb330a
reading.sensor.pump
reading.sensor.si111
reading.sensor.solenoid
reading.sensor.spn1
reading.sensor.t7610
reading.sensor.windobserverii
reading.sensor.windobserverii_extreme
)

for topic in "${topics[@]}"; do
  subject="${topic##*.}"
  description=$(curl -sSL -H "Accept: application/vnd.schemaregistry.v1+json" "https://schemaregistry.cper.eng.neoninternal.org/subjects/$subject/versions/latest" | jq -r .schema | jq -r .doc)
  echo -e "$subject: $description"
done