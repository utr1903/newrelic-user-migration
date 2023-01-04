import logging
import json

import cmd_args

class Config:

  # Arguments
  ARGS = {}

  # Source
  SOURCE_API_KEY = ""
  SOURCE_REGION = ""

  # Target
  TARGET_API_KEY = ""
  TARGET_REGION = ""

  # Auth domain mapping
  AUTH_DOMAIN_MAP = {}

  def __init__(self, args = {
    cmd_args.CONFIG_PATH: "config.json",
    cmd_args.DRY_RUN: False,
  }):
    self.ARGS = args

    logging.debug(json.dumps({
      "message": "Config is initialized.",
    }))

  def parse(self):

    logging.debug(json.dumps({
      "message": "Parsing config file [{}].".format(self.ARGS[cmd_args.CONFIG_PATH]),
    }))
    f = open(self.ARGS[cmd_args.CONFIG_PATH])

    try:
      data = json.load(f)

      # Source
      self.SOURCE_API_KEY = data["src"]["apiKey"]
      self.SOURCE_REGION = data["src"]["region"]

      # Target
      self.TARGET_API_KEY = data["tgt"]["apiKey"]
      self.TARGET_REGION = data["tgt"]["region"]

      self.AUTH_DOMAIN_MAP = data["authDomainMapping"]

    except Exception as e:
      msg = "Config file could not be parsed."
      logging.error(json.dumps({
        "message": msg,
        "exception": str(e),
      }))
      raise Exception(msg)

    finally:
      f.close()
 
