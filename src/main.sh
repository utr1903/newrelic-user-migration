#!/bin/bash

# Source account info
srcAccountId=""
srcApiKey=""
srcRegion=""

# Target account info
tgtAccountId=""
tgtApiKey=""
tgtRegion=""

# Run
python3 main.py \
  --srcAccountId $srcAccountId \
  --srcApiKey $srcApiKey \
  --srcRegion $srcRegion \
  --tgtAccountId $tgtAccountId \
  --tgtApiKey $tgtApiKey \
  --tgtRegion $tgtRegion
