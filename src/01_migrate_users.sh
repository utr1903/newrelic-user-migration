#!/bin/bash

# Source account info
srcAccountId=$NEWRELIC_ACCOUNT_ID
srcApiKey=$NEWRELIC_API_KEY
srcRegion=$NEWRELIC_REGION

# Target account info
tgtAccountId="x"
tgtApiKey="x"
tgtRegion="eu"

# Run
python3 01_migrate_users.py \
  --srcAccountId $srcAccountId \
  --srcApiKey $srcApiKey \
  --srcRegion $srcRegion \
  --tgtAccountId $tgtAccountId \
  --tgtApiKey $tgtApiKey \
  --tgtRegion $tgtRegion
