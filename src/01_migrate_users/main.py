import cmd_args
from config import Config
import fetch_users
import create_users

import json

def main():

  # Parse command line arguments
  args = cmd_args.run()

  # Parse config file
  cfg = Config(args)
  cfg.parse()

  # Fetch users from the source account
  oldUsers = fetch_users.run(cfg)

  # Create new users in the target account
  newUsers = create_users.run(cfg, oldUsers)

if __name__ == '__main__':
  main()