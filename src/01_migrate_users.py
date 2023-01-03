import argparse
import requests
from string import Template

# Argument names
SOURCE_ACCOUNT_ID = "srcAccountId"
SOURCE_API_KEY = "srcApiKey"
SOURCE_REGION = "srcRegion"
TARGET_ACCOUNT_ID = "tgtAccountId"
TARGET_API_KEY = "tgtApiKey"
TARGET_REGION = "tgtRegion"

def main():

  ####################################
  ### Parse command line arguments ###
  ####################################
  parser = argparse.ArgumentParser()

  # Source account info
  parser.add_argument("--{}".format(SOURCE_ACCOUNT_ID), help='New Relic account ID key of the source account.')
  parser.add_argument("--{}".format(SOURCE_API_KEY), help='New Relic API key of the source account.')
  parser.add_argument("--{}".format(SOURCE_REGION), help='New Relic region of the source account.')

  # Target account info
  parser.add_argument("--{}".format(TARGET_ACCOUNT_ID), help='New Relic account ID key of the target account.')
  parser.add_argument("--{}".format(TARGET_API_KEY), help='New Relic API key of the target account.')
  parser.add_argument("--{}".format(TARGET_REGION), help='New Relic region of the target account.')

  args = vars(parser.parse_args())

  # Source account ID
  srcAccountId = args[SOURCE_ACCOUNT_ID]
  if srcAccountId == None:
    print('Account ID of the source New Relic account is not given!')
    return
  
  # Source API key
  srcApiKey = args[SOURCE_API_KEY]
  if srcApiKey == None:
    print('API key of the source New Relic account is not given!')
    return

  # Source region
  srcRegion = args[SOURCE_REGION]
  if srcRegion == None:
    print('Region of the source New Relic account is not given!')
    return
  elif srcRegion != "eu" and srcRegion != "us":
    print('New Relic region can be either us or eu!')
    return

  # Target account ID
  tgtAccountId = args[TARGET_ACCOUNT_ID]
  if tgtAccountId == None:
    print('Account ID of the target New Relic account is not given!')
    return
  
  # Target API key
  tgtApiKey = args[TARGET_API_KEY]
  if tgtApiKey == None:
    print('API key of the target New Relic account is not given!')
    return

  # Target region
  tgtRegion = args[TARGET_REGION]
  if tgtRegion == None:
    print('Region of the target New Relic account is not given!')
    return
  elif tgtRegion != "eu" and tgtRegion != "us":
    print('New Relic region can be either us or eu!')
    return

  ###########################################
  ### Fetch users from the source account ###
  ###########################################
  headers = {
    "Api-Key": srcApiKey,
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
      'https://api.eu.newrelic.com/graphql' if tgtRegion == "eu" else 'https://api.newrelic.com/graphql',
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

  ##############################################
  ### Create new users in the target account ###
  ##############################################
  for user in allUsers:
    print(user)

if __name__ == '__main__':
  main()