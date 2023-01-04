import logging
import json
import requests
from string import Template

def run(cfg):

  headers = {
    "Api-Key": cfg.SOURCE_API_KEY,
    "Content-Type": "application/json"
  }

  users = []
  nextCursor = None

  logging.debug(json.dumps({
    "message": "Fetching all users from the source account.",
  }))

  while True:
    queryTemplate = Template("""
    {
      actor {
        organization {
          userManagement {
            authenticationDomains {
              authenticationDomains {
                id
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

    for domain in result["data"]["actor"]["organization"]["userManagement"]["authenticationDomains"]["authenticationDomains"]:
      for user in domain["users"]["users"]:
        logging.info(json.dumps({
          "message": "Saving user information.",
          "domainId": domain["id"],
          "userId": user["id"],
          "userName": user["name"],
          "userEmail": user["email"],
          "userType": user["type"]["id"],
        }))

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
      logging.debug(json.dumps({
        "message": "All users are fetched successfully.",
      }))
      break
    else:
      logging.debug(json.dumps({
        "message": "Users are not fetched entirely, continuing.",
      }))

  return users
