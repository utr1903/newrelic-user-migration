import cmd_args
from config import Config
import write
import fetch
import create

def main():

  # Parse command line arguments
  args = cmd_args.run()

  # Parse config file
  cfg = Config(args)
  cfg.parse()

  # Fetch users in src domains
  srcDomains = fetch.run(cfg)
  write.run(srcDomains, "src")

  # Create users in tgt domains
  tgtDomains = create.run(cfg, srcDomains)
  write.run(tgtDomains, "tgt")

if __name__ == '__main__':
  main()