import parse_args
import fetch_users_from_src

def main():

  # Parse command line arguments
  args = parse_args.run()

  # Fetch users from the source account
  allUsers = fetch_users_from_src.run(args)

  # Create new users in the target account
  for user in allUsers:
    print(user)

if __name__ == '__main__':
  main()