import cmd_args
from config import Config
import fetch
import create

def main():

  # Parse command line arguments
  args = cmd_args.run()

  # Parse config file
  cfg = Config(args)
  cfg.parse()

  # Fetch domains
  domains = fetch.run(cfg)

  # Create new users in the target account
  # newUsers = create_users.run(cfg, oldUsers)

if __name__ == '__main__':
  main()