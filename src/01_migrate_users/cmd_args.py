import logging
import os
import time
import json
import argparse

# Argument names
LOG_LEVEL = "logLevel"
CONFIG_PATH = "configPath"
DRY_RUN = "dryRun"

def run():
  parser = argparse.ArgumentParser()

  parser.add_argument("--{}".format(LOG_LEVEL), help="Log level: [debug, info, error].")
  parser.add_argument("--{}".format(CONFIG_PATH), help="Path to the configuration file.")
  parser.add_argument("--{}".format(DRY_RUN), help="To see what will be done: [true, false].")

  args = vars(parser.parse_args())

  # Configure logger
  logLevel = args[LOG_LEVEL]
  if logLevel == "debug":
    logging.basicConfig(level=logging.DEBUG)
  elif logLevel == "info":
    logging.basicConfig(level=logging.INFO)
  else:
    logging.basicConfig(level=logging.ERROR)
  
  if not os.path.exists("{}/logs".format(os.getcwd())):
    os.makedirs("{}/logs".format(os.getcwd()))
  logging.getLogger().addHandler(logging.FileHandler("{0}/{1}.log".format("logs", int(time.time()))))

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
