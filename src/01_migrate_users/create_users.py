import logging
import json
import requests
from string import Template

import cmd_args

def getNewAuthDomain(cfg, user):
  if user["domainId"] not in cfg.AUTH_DOMAIN_MAP:
    msg = "Domain ID of the user is not found in configuration."
    logging.error(json.dumps({
      "message": msg,
      "userId": user["userId"],
      "userName": user["userName"],
      "userEmail": user["userEmail"],
      "userType": user["userType"],
    }))
    raise Exception(msg)

  return cfg.AUTH_DOMAIN_MAP[user["domainId"]]

def convertUserType(user):
  if user["userType"] == "0":
    return "FULL_USER_TIER"
  elif user["userType"] == "1":
    return "BASIC_USER_TIER"
  else:
    msg = "Given user type is invalid."
    logging.error(json.dumps({
      "message": msg,
      "userId": user["userId"],
      "userName": user["userName"],
      "userEmail": user["userEmail"],
      "userType": user["userType"],
    }))
    raise Exception(msg)

def run(cfg, users):
  headers = {
    "Api-Key": cfg.TARGET_API_KEY,
    "Content-Type": "application/json"
  }

  newUsers = []

  logging.debug(json.dumps({
    "message": "Creating all users in the target account.",
  }))

  for user in users:

    # If dry run, just log
    if cfg.ARGS[cmd_args.DRY_RUN] == True:
      logging.debug(json.dumps({
        "message": "Dry run: To be created user info.",
        "domainId": getNewAuthDomain(cfg, user),
        "userId": user["userId"],
        "userName": user["userName"],
        "userEmail": user["userEmail"],
        "userType": user["userType"],
      }))
      continue

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
      domainId = getNewAuthDomain(cfg, user),
      userId = user["userId"],
      userName = user["userName"],
      userEmail = user["userEmail"],
      userType = convertUserType(user),
    )

    # Execute request
    logging.debug(json.dumps({
      "message": "Making request to New Relic.",
    }))
    request = requests.post(
      "https://api.eu.newrelic.com/graphql" if cfg.TARGET_REGION == "eu" else "https://api.newrelic.com/graphql",
      json={"query": query},
      headers=headers
    )

    if request.status_code != 200:
      msg = "Request has failed."
      logging.error(json.dumps({
        "message": "Request has succeeded to New Relic.",
        "statusCode": request.status_code,
      }))
      raise Exception(msg)

    result = request.json()
    if "errors" in result:
      msg = "Request has returned an error."
      logging.error(json.dumps({
        "message": "Request has succeeded to New Relic.",
        "error": json.dumps(result["errors"]),
      }))
      raise Exception(msg)

    logging.debug(json.dumps({
      "message": "Request has succeeded to New Relic.",
    }))

    newUser = result["data"]["userManagementCreateUser"]["createdUser"]
    logging.info(json.dumps({
      "message": "Saving user information.",
      "domainId": newUser["authenticationDomainId"],
      "userId": newUser["id"],
      "userName": newUser["name"],
      "userEmail": newUser["email"],
      "userType": newUser["type"]["id"],
    }))

    newUsers.append({
      "domainId": newUser["authenticationDomainId"],
      "userId": newUser["id"],
      "userName": newUser["name"],
      "userEmail": newUser["email"],
      "userType": newUser["type"]["id"],
    })

  logging.debug(json.dumps({
    "message": "All users are created successfully.",
  }))

  return newUsers
