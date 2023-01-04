import logging
import json
import requests
from string import Template

def createQuery(cursors):

  # Create template
  queryTemplate = Template("""
  {
    actor {
      organization {
        userManagement {
          authenticationDomains(cursor: $cursorDomains) {
            nextCursor
            authenticationDomains {
              id
              name
              users(cursor: $cursorUsers) {
                nextCursor
                users {
                  id
                  name
                  email
                  type {
                    id
                  }
                  groups(cursor: $cursorGroups) {
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
    }
  }
  """)

  # Substitute variables
  query = queryTemplate.substitute(
    cursorDomains = "null" if cursors["domains"] == None else cursors["domains"],
    cursorUsers = "null" if cursors["users"] == None else cursors["users"],
    cursorGroups = "null" if cursors["groups"] == None else cursors["groups"],
  )

  return query

def executeRequest(cfg, cursors):

  # Set headers
  headers = {
    "Api-Key": cfg.SOURCE_API_KEY,
    "Content-Type": "application/json"
  }

  # Create query
  query = createQuery(cursors)

  logging.debug(json.dumps({
    "message": "Making request to New Relic.",
  }))
  request = requests.post(
    "https://api.eu.newrelic.com/graphql" if cfg.SOURCE_REGION == "eu" else "https://api.newrelic.com/graphql",
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

def saveDomain(domains, domain):
  logging.info(json.dumps({
    "message": "Saving domain information.",
    "domainId": domain["id"],
    "domainName": domain["name"],
  }))

  # Create domain
  domains[domain["id"]] = {
    "name": domain["name"],
    "users": {},
  }

def saveUser(domains, domain, user):
  logging.info(json.dumps({
    "message": "Saving user information.",
    "domainId": domain["id"],
    "userId": user["id"],
  }))

  # Create users
  domains[domain["id"]]["users"][user["id"]] = {
    "name": user["name"],
    "email": user["email"],
    "type": user["type"]["id"],
    "groups": {},
  }

def saveGroup(domains, domain, user, group):
  logging.info(json.dumps({
    "message": "Saving group information.",
    "domainId": domain["id"],
    "groupId": user["id"],
  }))

  # Create group
  domains[domain["id"]]["users"][user["id"]]["groups"][group["id"]] = {
    "id": group["id"],
    "name": group["displayName"],
  }

def isStillFetchingUsers(cursorUsers, domainId, groupId):
  if cursorUsers == None:
    logging.debug(json.dumps({
      "message": "All users are fetched successfully.",
      "domainId": domainId,
      "groupId": groupId,
    }))
    return False
  else:
    logging.debug(json.dumps({
      "message": "Users are not fetched entirely, continuing.",
      "domainId": domainId,
      "groupId": groupId,
      "cursorUsers": cursorUsers,
    }))
    return True

def isStillFetchingGroups(cursorGroups, domainId):
  if cursorGroups == None:
    logging.debug(json.dumps({
      "message": "All groups are fetched successfully.",
      "domainId": domainId,
    }))
    return False
  else:
    logging.debug(json.dumps({
      "message": "Groups are not fetched entirely, continuing.",
      "domainId": domainId,
      "cursorGroups": cursorGroups,
    }))
    return True

def isStillFetchingDomains(cursorDomains):
  if cursorDomains == None:
    logging.debug(json.dumps({
      "message": "All domains are fetched successfully.",
    }))
    return False
  else:
    logging.debug(json.dumps({
      "message": "Domains are not fetched entirely, continuing.",
      "cursorDomains": cursorDomains,
    }))
    return True

def run(cfg):

  logging.debug(json.dumps({
    "message": "Fetching all users from the source account.",
  }))

  # Init variables
  domains = {}
  cursors = {
    "domains": None,
    "users": None,
    "groups": None,
  }

  # Fetch all domains
  while True:

    # Execute request
    result = executeRequest(cfg, cursors)

    # Save domains
    for domain in result["data"]["actor"]["organization"]["userManagement"]["authenticationDomains"]["authenticationDomains"]:
      saveDomain(domains, domain)

      # Save users
      for user in domain["users"]["users"]:
        saveUser(domains, domain, user)

        # Save groups
        for group in user["groups"]["groups"]:
          saveGroup(domains, domain, user, group)

    # Check if all groups in the domain are fetched
    cursors["groups"] = user["groups"]["nextCursor"]
    if isStillFetchingGroups(cursors["groups"], domain["id"]):
      continue

    # Check if all users in the group are fetched
    cursors["users"] = domain["users"]["nextCursor"]
    if isStillFetchingUsers(cursors["users"], domain["id"], group["id"]):
      continue

    # Check if all domains are fetched
    cursors["domains"] = result["data"]["actor"]["organization"]["userManagement"]["authenticationDomains"]["nextCursor"]
    if not isStillFetchingDomains(cursors["domains"]):
      break

  return domains
