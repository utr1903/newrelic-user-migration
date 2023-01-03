import requests
from string import Template

import parse_args

def run(args):
  headers = {
    "Api-Key": args[parse_args.SOURCE_API_KEY],
    "Content-Type": 'application/json'
  }

  allUsers = []
  nextCursor = None

  while True:
    queryTemplate = Template("""
    {
      actor {
        users {
          userSearch(
            cursor: $nextCursor
          ) {
            users {
              name
              email
              userId
            }
            nextCursor
          }
        }
      }
    }
    """)

    # Substitute variables
    query = queryTemplate.substitute(
      nextCursor = "null" if nextCursor == None else nextCursor,
    )

    # Execute request
    request = requests.post(
      'https://api.eu.newrelic.com/graphql' if args[parse_args.SOURCE_REGION] == "eu" else 'https://api.newrelic.com/graphql',
      json={'query': query},
      headers=headers
    )

    if request.status_code != 200:
      print("Query failed to run by returning code of {}. {}".format(request.status_code, query))
      return

    result = request.json()
    for user in result["data"]["actor"]["users"]["userSearch"]["users"]:
      allUsers.append(user)

    # Continue to parse till all the data is fetched
    nextCursor = result["data"]["actor"]["users"]["userSearch"]["nextCursor"]
    if nextCursor == None:
      print("All users are fetched.")
      break
    else:
      print("Users are not fetched entirely. Continuing...")

  return allUsers