from testrail import *
import os 

 # variables added to ~/.zshrc file
email = os.getenv('PI_EMAIL')
token = os.getenv('TESTRAIL_TOKEN')
 
client = APIClient('http://hollywoodsports.testrail.io/')
client.user = email
client.password = token

case = client.send_get('get_users/8')
print(json.dumps(case, sort_keys=True, indent=4, separators=(",", ": ")))