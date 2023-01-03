import requests
from string import Template

import parse_args

def run(args):
  headers = {
    "Api-Key": args[parse_args.SOURCE_API_KEY],
    "Content-Type": "application/json"
  }

  users = []
  nextCursor = None

  while True:
    queryTemplate = Template("""
    {
      actor {
        organization {
          userManagement {
            authenticationDomains {
              authenticationDomains {
                users(
                  cursor: $nextCursor
                ) {
                  users {
                    id
                    name
                    email
                    type {
                      id
                    }
                  }
                }
              }
              nextCursor
            }
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
      "https://api.eu.newrelic.com/graphql" if args[parse_args.SOURCE_REGION] == "eu" else "https://api.newrelic.com/graphql",
      json={"query": query},
      headers=headers
    )

    if request.status_code != 200:
      print("Query failed to run by returning code of {}. {}".format(request.status_code, query))
      return

    result = request.json()

    for domain in result["data"]["actor"]["organization"]["userManagement"]["authenticationDomains"]["authenticationDomains"]:
      for user in domain["users"]["users"]:
        users.append({
          "domainId": domain["id"],
          "userId": user["id"],
          "userName": user["name"],
          "userEmail": user["email"],
          "userType": user["type"]["id"],
        })

    # Continue to parse till all the data is fetched
    nextCursor = result["data"]["actor"]["organization"]["userManagement"]["authenticationDomains"]["nextCursor"]
    if nextCursor == None:
      print("All users are fetched.")
      break
    else:
      print("Users are not fetched entirely. Continuing...")

  return users
