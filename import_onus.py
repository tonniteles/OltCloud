import time
import API_OltCloud
import json

api = API_OltCloud.OltCloudAPI()

# Get all ONTs and save to a JSON file every 30 seconds
while True:
  onts = api.get_all_onts()
  with open('onts.json', 'w') as outfile:
      json.dump(onts, outfile)
  time.sleep(30)