import argparse

# Argument names
SOURCE_ACCOUNT_ID = "srcAccountId"
SOURCE_API_KEY = "srcApiKey"
SOURCE_REGION = "srcRegion"
TARGET_ACCOUNT_ID = "tgtAccountId"
TARGET_API_KEY = "tgtApiKey"
TARGET_REGION = "tgtRegion"

def run():
  parser = argparse.ArgumentParser()

  # Source account info
  parser.add_argument("--{}".format(SOURCE_ACCOUNT_ID), help='New Relic account ID key of the source account.')
  parser.add_argument("--{}".format(SOURCE_API_KEY), help='New Relic API key of the source account.')
  parser.add_argument("--{}".format(SOURCE_REGION), help='New Relic region of the source account.')

  # Target account info
  parser.add_argument("--{}".format(TARGET_ACCOUNT_ID), help='New Relic account ID key of the target account.')
  parser.add_argument("--{}".format(TARGET_API_KEY), help='New Relic API key of the target account.')
  parser.add_argument("--{}".format(TARGET_REGION), help='New Relic region of the target account.')

  args = vars(parser.parse_args())

  # Source account ID
  srcAccountId = args[SOURCE_ACCOUNT_ID]
  if srcAccountId == None:
    raise Exception("Account ID of the source New Relic account is not given!")

  # Source API key
  srcApiKey = args[SOURCE_API_KEY]
  if srcApiKey == None:
    raise Exception("API key of the source New Relic account is not given!")

  # Source region
  srcRegion = args[SOURCE_REGION]
  if srcRegion == None:
    raise Exception("Region of the source New Relic account is not given!")
  elif srcRegion != "eu" and srcRegion != "us":
    raise Exception("New Relic region can be either us or eu!")

  # Target account ID
  tgtAccountId = args[TARGET_ACCOUNT_ID]
  if tgtAccountId == None:
    raise Exception("Account ID of the target New Relic account is not given!")
  
  # Target API key
  tgtApiKey = args[TARGET_API_KEY]
  if tgtApiKey == None:
    raise Exception("API key of the target New Relic account is not given!")

  # Target region
  tgtRegion = args[TARGET_REGION]
  if tgtRegion == None:
    raise Exception("Region of the target New Relic account is not given!")
  elif tgtRegion != "eu" and tgtRegion != "us":
    raise Exception("New Relic region can be either us or eu!")

  return {
    SOURCE_ACCOUNT_ID: srcAccountId,
    SOURCE_API_KEY: srcApiKey,
    SOURCE_REGION: srcRegion,
    TARGET_ACCOUNT_ID: tgtAccountId,
    TARGET_API_KEY: tgtApiKey,
    TARGET_REGION: tgtRegion,
  }
