import requests
from string import Template

import parse_args

def convertUserType(userType):
  if userType == "0":
    return "FULL_USER_TIER"
  elif userType == "1":
    return "BASIC_USER_TIER"
  else:
    raise Exception("Given user type is invalid")

def run(args, users):
  headers = {
    "Api-Key": args[parse_args.TARGET_API_KEY],
    "Content-Type": "application/json"
  }

  newUsers = []
  for user in users:

    queryTemplate = Template("""
    mutation {
      userManagementCreateUser(
        createUserOptions: {
          authenticationDomainId: "$domainId",
          name: "$userName",
          email: "$userEmail",
          userType: $userType
        }
      ) {
        createdUser {
          authenticationDomainId
          id
          name
          email
          type {
            id
          }
        }
      }
    }
    """)

    # Substitute variables
    query = queryTemplate.substitute(
      domainId = user["domainId"],
      userId = user["userId"],
      userName = user["userName"],
      userEmail = user["userEmail"],
      userType = convertUserType(user["userType"]),
    )

    # Execute request
    request = requests.post(
      "https://api.eu.newrelic.com/graphql" if args[parse_args.TARGET_REGION] == "eu" else "https://api.newrelic.com/graphql",
      json={"query": query},
      headers=headers
    )

    if request.status_code != 200:
      print("Query failed to run by returning code of {}. {}".format(request.status_code, query))
      return

    result = request.json()
    if "errors" in result:
      print("Query has returned error(s): {}.".format(result["errors"]))
      return

    for newUser in result["data"]["userManagementCreateUser"]["createdUser"]:
      newUsers.append({
        "domainId": newUser["authenticationDomainId"],
        "userId": newUser["id"],
        "userName": newUser["name"],
        "userEmail": newUser["email"],
        "userType": newUser["type"]["id"],
      })

    break

  print("All users are created.")  

  return newUsers
