import logging
import json
import requests
from string import Template

import cmd_args

def getTgtAuthDomainId(cfg, srcDomainId):
  if srcDomainId not in cfg.AUTH_DOMAIN_MAP:
    msg = "Domain ID [{}] of the user is not found in configuration.".format(srcDomainId)
    logging.error(json.dumps({
      "message": msg,
    }))
    raise Exception(msg)

  return cfg.AUTH_DOMAIN_MAP[srcDomainId]

def convertUserType(userType):
  if userType == "0":
    return "FULL_USER_TIER"
  elif userType == "1":
    return "BASIC_USER_TIER"
  else:
    msg = "Given user type [{}] is invalid.".format(userType)
    logging.error(json.dumps({
      "message": msg,
    }))
    raise Exception(msg)

def createQueryToCreateUser(domainId, userName, userEmail, userType):

  # Create template
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
    domainId = domainId,
    userName = userName,
    userEmail = userEmail,
    userType = convertUserType(userType),
  )

  return query

def createQueryToCreateGroup(domainId, groupName):

  # Create template
  queryTemplate = Template("""
  mutation {
    userManagementCreateGroup(
      createGroupOptions: {
        authenticationDomainId: "$domainId",
        displayName: "$groupName"
      }
    ) {
      group {
        id
      }
    }
  }
  """)

  # Substitute variables
  query = queryTemplate.substitute(
    domainId = domainId,
    groupName = groupName,
  )

  return query

def executeRequest(cfg, query):

  # Set headers
  headers = {
    "Api-Key": cfg.TARGET_API_KEY,
    "Content-Type": "application/json"
  }

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

  return result

def saveDomain(tgtDomains, tgtDomainId):
  logging.info(json.dumps({
    "message": "Saving domain information.",
    "domainId": tgtDomainId,
  }))

  # Create domain
  tgtDomains[tgtDomainId] = {
    "users": {},
  }

def saveUser(cfg, tgtDomains, tgtDomainId, srcUserId, srcUser):
  # Initialize properties
  tgtUserId = "*{}*".format(srcUserId)
  tgtUserName = srcUser["name"]
  tgtUserEmail = srcUser["email"]
  tgtUserType = srcUser["type"]

  # Perform if not dry run
  if cfg.ARGS[cmd_args.DRY_RUN] == False:

    # Create query
    query = createQueryToCreateUser(tgtDomainId, tgtUserName, tgtUserEmail, tgtUserType)

    # Execute request
    result = executeRequest(cfg, query)

    # Update properties
    tgtUserId = result["data"]["userManagementCreateUser"]["createdUser"]["id"]
    tgtUserType = result["data"]["userManagementCreateUser"]["createdUser"]["type"]["id"]

  logging.info(json.dumps({
    "message": "Saving user information.",
    "domainId": tgtDomainId,
    "userId": tgtUserId,
  }))

  # Create users
  tgtDomains[tgtDomainId]["users"][tgtUserId] = {
    "name": tgtUserName,
    "email": tgtUserEmail,
    "type": tgtUserType,
    "groups": {},
  }

  return tgtUserId

def saveGroup(cfg, tgtDomains, tgtDomainId, tgtUserId, srcGroupId, tgtGroupName):
  # Initialize properties
  tgtGroupId = "*{}*".format(srcGroupId)

  # Perform if not dry run
  if cfg.ARGS[cmd_args.DRY_RUN] == False:

    # Create query
    query = createQueryToCreateGroup(tgtDomainId, tgtGroupName)

    # Execute request
    result = executeRequest(cfg, query)

    # Update properties
    tgtGroupId = result["data"]["userManagementCreateUser"]["createdUser"]["id"]

  logging.info(json.dumps({
    "message": "Saving user information.",
    "domainId": tgtDomainId,
    "userId": tgtUserId,
    "userId": tgtGroupId,
  }))

  # Create users
  tgtDomains[tgtDomainId]["users"][tgtUserId]["groups"][tgtGroupId] = tgtGroupName

  return tgtGroupId

def run(cfg, srcDomains):

  logging.debug(json.dumps({
    "message": "Creating all users in the target account.",
  }))

  # Init variables
  tgtDomains = {}

  # Save domains
  for srcDomainId, srcDomain in srcDomains.items():
    tgtDomainId = getTgtAuthDomainId(cfg, srcDomainId)
    saveDomain(tgtDomains, tgtDomainId)

    # Save users
    for srcUserId, srcUser in srcDomain["users"].items():
      tgtUserId = saveUser(cfg, tgtDomains, tgtDomainId, srcUserId, srcUser)

      return
      # Save groups & assign users
      for srcGroupId, srcGroupName in srcUser["groups"].items():
        tgtGroupId = saveGroup(cfg, tgtDomains, tgtDomainId, tgtUserId, srcGroupId, srcGroupName)

  return tgtDomains
