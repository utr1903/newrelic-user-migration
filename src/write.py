import os
import logging
import json

def run(data, filename):

  if not os.path.exists("{}/out".format(os.getcwd())):
    os.makedirs("{}/out".format(os.getcwd()))

  f = open("out/{}.json".format(filename), "w")
  try:
    f.write(json.dumps(data))
  except Exception as e:
    msg = "File could not be written."
    logging.error(json.dumps({
      "message": msg,
      "exception": str(e),
    }))
    raise Exception(msg)

  finally:
    f.close()
