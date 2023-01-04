import logging
import json
import argparse

# Argument names
CONFIG_PATH = "configPath"
DRY_RUN = "dryRun"

def run():

  # Configure logger
  logging.basicConfig(level=logging.DEBUG)

  logging.debug(json.dumps({
    "message": "Parsing command line arguments.",
  }))

  parser = argparse.ArgumentParser()

  parser.add_argument("--{}".format(CONFIG_PATH), help="Path to the configuration file.")
  parser.add_argument("--{}".format(DRY_RUN), help="To see what will be done.")

  args = vars(parser.parse_args())

  # Source account ID
  configPath = args[CONFIG_PATH]
  if configPath == None:
    msg = "The flag {} is not defined.".format(CONFIG_PATH)
    logging.error(json.dumps({
      "message": msg,
    }))
    raise Exception(msg)
  else:
    logging.debug(json.dumps({
      "message": "The flag {} is defined as {}.".format(CONFIG_PATH, configPath),
    }))

  # Source API key
  dryRun = args[DRY_RUN]
  if dryRun == "false":
    dryRun = False
    logging.debug(json.dumps({
      "message": "The flag {} is defined as {}.".format(DRY_RUN, dryRun),
    }))
  elif dryRun == "true":
    dryRun = True
    logging.debug(json.dumps({
      "message": "The flag {} is defined as {}.".format(DRY_RUN, dryRun),
    }))
  else:
    msg = "The flag {} is not defined.".format(DRY_RUN)
    logging.error(json.dumps({
      "message": msg,
    }))
    raise Exception(msg)

  logging.debug(json.dumps({
    "message": "Command line arguments are parsed successfully.",
  }))

  return {
    CONFIG_PATH: configPath,
    DRY_RUN: dryRun,
  }
