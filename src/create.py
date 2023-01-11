import logging
import json
import requests
from string import Template
import uuid

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

def createQueryToFetchUsers(domainId, cursorUsers):

  # Create template
  queryTemplate = Template("""
  {
    actor {
      organization {
        userManagement {
          authenticationDomains(
            id: "$domainId"
          ) {
            authenticationDomains {
              users(cursor: $cursorUsers) {
                nextCursor
                users {
                  id
                  email
                  groups {
                    groups {
                      displayName
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  """)

  # Substitute variables
  query = queryTemplate.substitute(
    domainId = domainId,
    cursorUsers = "null" if cursorUsers == None else cursorUsers,
  )

  return query

def areAllUsersFetched(cursorUsers, domainId):
  if cursorUsers == None:
    logging.debug(json.dumps({
      "message": "All users are fetched successfully.",
      "domainId": domainId,
    }))
    return True
  else:
    logging.debug(json.dumps({
      "message": "Users are not fetched entirely, continuing.",
      "domainId": domainId,
      "cursorUsers": cursorUsers,
    }))
    return False

def fetchUsersOfDomain(cfg, tgtDomainId):

  # Initialize variables
  userMapping = {}
  cursorUsers = None

  # Continue until all users are fetched
  while True:

    # Create query
    query = createQueryToFetchUsers(tgtDomainId, cursorUsers)

    # Execute request
    result = executeRequest(cfg, query)

    users = result["data"]["actor"]["organization"]["userManagement"]["authenticationDomains"]["authenticationDomains"][0]["users"]["users"]
    for user in users:
      logging.debug(json.dumps({
        "message": "Fetched user email to ID.",
        "domainId": tgtDomainId,
        "userId": user["id"],
        "userEmail": user["email"],
      }))

      userGroups = []
      for groupName in user["groups"]["groups"]:
        userGroups.append(groupName["displayName"])

      userMapping[user["email"]] = {
        "id": user["id"],
        "groupNames": userGroups,
      }

    cursorUsers = result["data"]["actor"]["organization"]["userManagement"]["authenticationDomains"]["authenticationDomains"][0]["users"]["nextCursor"]
    if areAllUsersFetched(cursorUsers, tgtDomainId):
      break

  return userMapping

def createQueryToFetchGroups(domainId, cursorGroups):

  # Create template
  queryTemplate = Template("""
  {
    actor {
      organization {
        authorizationManagement {
          authenticationDomains(
            id: "$domainId"
          ) {
            authenticationDomains {
              groups(
                cursor: $cursorGroups
              ) {
                nextCursor
                groups {
                  id
                  displayName
                }
              }
            }
          }
        }
      }
    }
  }
  """)

  # Substitute variables
  query = queryTemplate.substitute(
    domainId = domainId,
    cursorGroups = "null" if cursorGroups == None else cursorGroups,
  )

  return query

def areAllGroupsFetched(cursorGroups, domainId):
  if cursorGroups == None:
    logging.debug(json.dumps({
      "message": "All groups are fetched successfully.",
      "domainId": domainId,
    }))
    return True
  else:
    logging.debug(json.dumps({
      "message": "Groups are not fetched entirely, continuing.",
      "domainId": domainId,
      "cursorGroups": cursorGroups,
    }))
    return False

def fetchGroupsOfDomain(cfg, tgtDomainId):

  # Initialize variables
  groupMapping = {}
  cursorGroups = None

  # Continue until all groups are fetched
  while True:

    # Create query
    query = createQueryToFetchGroups(tgtDomainId, cursorGroups)

    # Execute request
    result = executeRequest(cfg, query)

    groups = result["data"]["actor"]["organization"]["authorizationManagement"]["authenticationDomains"]["authenticationDomains"][0]["groups"]["groups"]
    for group in groups:
      logging.debug(json.dumps({
        "message": "Fetched group name to ID.",
        "domainId": tgtDomainId,
        "groupId": group["id"],
        "groupName": group["displayName"],
      }))
      groupMapping[group["displayName"]] = group["id"]

    cursorGroups = result["data"]["actor"]["organization"]["authorizationManagement"]["authenticationDomains"]["authenticationDomains"][0]["groups"]["nextCursor"]
    if areAllGroupsFetched(cursorGroups, tgtDomainId):
      break

  return groupMapping

def createUser(cfg, tgtDomainId, tgtUserName, tgtUserEmail, tgtUserType):

  # Perform if not dry run
  if cfg.ARGS[cmd_args.DRY_RUN] == False:

    # Create query
    query = createQueryToCreateUser(tgtDomainId, tgtUserName, tgtUserEmail, tgtUserType)

    # Execute request
    result = executeRequest(cfg, query)

    return result["data"]["userManagementCreateUser"]["createdUser"]["id"]
  else:
    return str(uuid.uuid4())

def saveUser(tgtDomains, tgtDomainId, tgtUserId, tgtUserName, tgtUserEmail, tgtUserType):

  # Assign a random ID in case of dry run
  if tgtUserId == None:
    tgtUserId = str(uuid.uuid4())

  logging.info(json.dumps({
    "message": "Saving user information.",
    "domainId": tgtDomainId,
    "userId": tgtUserId,
    "userEmail": tgtUserEmail,
  }))

  # Create users
  tgtDomains[tgtDomainId]["users"][tgtUserId] = {
    "name": tgtUserName,
    "email": tgtUserEmail,
    "type": tgtUserType,
    "groups": {},
  }

def logUserExists(tgtDomainId, tgtUserId):
  logging.info(json.dumps({
    "message": "User already exists.",
    "domainId": tgtDomainId,
    "userId": tgtUserId,
  }))

def createGroup(cfg, tgtDomainId, tgtGroupName):

  # Perform if not dry run
  if cfg.ARGS[cmd_args.DRY_RUN] == False:

    # Create query
    query = createQueryToCreateGroup(tgtDomainId, tgtGroupName)

    # Execute request
    result = executeRequest(cfg, query)

    return result["data"]["userManagementCreateGroup"]["group"]["id"]
  else:
    return str(uuid.uuid4())

def saveGroup(tgtDomains, tgtDomainId, tgtUserId, tgtGroupName, tgtGroupId):

  # Assign a random ID in case of dry run
  if tgtUserId == None:
    tgtUserId = uuid.uuid4()

  logging.info(json.dumps({
    "message": "Saving group information.",
    "domainId": tgtDomainId,
    "userId": tgtUserId,
    "groupId": tgtGroupId,
    "groupName": tgtGroupName,
  }))

  # Create groups
  tgtDomains[tgtDomainId]["users"][tgtUserId]["groups"][tgtGroupName] = tgtGroupId

def logGroupExists(tgtDomainId, tgtGroupId):
  logging.info(json.dumps({
    "message": "Group already exists.",
    "domainId": tgtDomainId,
    "groupId": tgtGroupId,
  }))

def createQueryToAssignUserToGroup(userId, groupId):

  # Create template
  queryTemplate = Template("""
  mutation {
    userManagementAddUsersToGroups(
      addUsersToGroupsOptions: {
        groupIds: "$groupId",
        userIds: "$userId"
      }
    ) {
      groups {
        id
      }
    }
  }
  """)

  # Substitute variables
  query = queryTemplate.substitute(
    userId = userId,
    groupId = groupId,
  )

  return query

def assignUserToGroup(cfg, userId, groupId):

  # Perform if not dry run
  if cfg.ARGS[cmd_args.DRY_RUN] == False:

    # Create query
    query = createQueryToAssignUserToGroup(userId, groupId)

    # Execute request
    executeRequest(cfg, query)
  
  logging.info(json.dumps({
    "message": "User is assigned to group.",
    "userId": userId,
    "groupId": groupId,
  }))

def logUserAlreadyAssignedToGroup(tgtDomainId, tgtUserId, tgtGroupId):
  logging.info(json.dumps({
    "message": "User is already assigned to group.",
    "domainId": tgtDomainId,
    "userId": tgtUserId,
    "groupId": tgtGroupId,
  }))

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

    # Fetch all users of the target domain
    userMapping = fetchUsersOfDomain(cfg, tgtDomainId)

    # Fetch all groups of the target domain
    groupMapping = fetchGroupsOfDomain(cfg, tgtDomainId)

    # Save users
    for srcUser in srcDomain["users"].values():

      # Initialize target user ID
      tgtUserId = None

      # Create new user if not exists
      if srcUser["email"] not in userMapping:
        tgtUserId = createUser(cfg, tgtDomainId, srcUser["name"], srcUser["email"], srcUser["type"])
        saveUser(tgtDomains, tgtDomainId, tgtUserId, srcUser["name"], srcUser["email"], srcUser["type"])
        userMapping[srcUser["email"]] = {
          "id": tgtUserId,
          "groupNames": [],
        }

      # Get the existing user ID
      else:
        tgtUserId = userMapping[srcUser["email"]]["id"]
        saveUser(tgtDomains, tgtDomainId, tgtUserId, srcUser["name"], srcUser["email"], srcUser["type"])
        logUserExists(tgtDomainId, tgtUserId)

      # Save groups & assign users
      for srcGroupName in srcUser["groups"].values():

        # Initialize target group ID
        tgtGroupId = None

        # Create new group if not exists
        if srcGroupName not in groupMapping:
          tgtGroupId = createGroup(cfg, tgtDomainId, srcGroupName)
          saveGroup(tgtDomains, tgtDomainId, tgtUserId, srcGroupName, tgtGroupId)

        # Get the existing group ID
        else:
          tgtGroupId = groupMapping[srcGroupName]
          logGroupExists(tgtDomainId, tgtUserId)

        # Assign user to group if not assigned already
        if srcGroupName not in userMapping[srcUser["email"]]["groupNames"]:
          assignUserToGroup(cfg, tgtUserId, tgtGroupId)
        else:
          logUserAlreadyAssignedToGroup(tgtDomainId, tgtUserId, tgtGroupId)

  return tgtDomains
