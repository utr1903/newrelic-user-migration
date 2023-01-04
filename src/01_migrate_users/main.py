import parse_args
import fetch_users_from_src
import create_users_in_tgt

def main():

  # Parse command line arguments
  args = parse_args.run()

  # Fetch users from the source account
  users = fetch_users_from_src.run(args)

  # Create new users in the target account
  create_users_in_tgt.run(args, users)

if __name__ == '__main__':
  main()