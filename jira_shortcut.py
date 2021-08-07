# This code sample uses the 'requests' library:
# http://docs.python-requests.org

# references
# 1. https://stackoverflow.com/questions/29996079/match-a-whole-word-in-a-string-using-dynamic-regex
# 2. https://stackoverflow.com/questions/63814822/check-if-input-consists-of-a-comma-separated-list-of-numbers

import os
import re
import requests
from requests.auth import HTTPBasicAuth
import json

# Objective of validate_input: make sure user input is in the  valid form
# What is the valid form? n or n,n,...,n; where n is a digit between 0 and upper_bounds minus 1
# input - user input (string), upper_bounds - number of entries in the selection list (int)
# return - True|False - boolean representing whether input matches valid form
def validate_input(input, upper_bounds):
   # reg expression base: ^[0-9](,[0-9]+)*$
   match_string = r'^[0-' + str(upper_bounds-1) + r'](,[0-' + str(upper_bounds-1) + r']+)*$' # reference 1
   pattern = re.compile(match_string) # reference 2
   match_result = re.search(pattern, input)
   if match_result:
      return True
   else:
      return False

# Objective of show_list_get_choice: display list and get user selection with validation
# Validation takes place in validate_input(input, upper_bounds)
# length - length of list (int), given_list - list to be displayed to user (array)
# return - query - a string with list items separated by a comma
def show_list_get_choice(length, given_list):
   # print list items
   for i in range(length):
      print("[", i, "] ", given_list[i])
   choice = input("Selection: ")
   match = validate_input(choice, length)
   while match == False:
      choice = input("Please make sure your selection contains only the given numbers in the following form: 1,2,3.\nSelection: ")
      match = validate_input(choice, length)
   split = choice.split(',')
   # changing value of split from number selection to corresponding list item
   for i in range(len(split)):
      split[i] = given_list[int(split[i])]
   query = ",".join(split)
   return query

if __name__ == "__main__":
   # variables added to ~/.zshrc file
   email = os.getenv('PI_EMAIL')
   token = os.getenv('JIRA_TOKEN')

   
   # projects
   projects = ["JAZZ", "STREET", "OP", "RAT"]
   p_length = len(projects)
   # types
   # New Feature has to be put in quotes bc JQL requires them when a name contains a space
   types = ["Bug", "Epic", "Improvement", "Initiative", "\"New Feature\"", "Spike", "Story", "Task"]
   t_length = len(types)
   # fix versions
   versions = ["Heat", "Ironpigs", "Jaguars", "Koalas", "Llamas", "Magic", "Nuggets", "Otters", "Pirates"]
   v_length = len(versions)
   # components
   # AND has to be put in quotes bc AND is a keyword in JQL
   components = ["iOS", "\"AND\"", "WWW", "QA"]
   c_length = len(components)

   print("We will now build your filter. Please answer the following prompts.\n")
   '''

   # get project name(s)
   print("Below is a list of available projects to choose from. Please enter the number(s) corresponding to your choice of project. If more than one, please separate each number with a comma (ex: 1,3,4).")
   p_query = show_list_get_choice(p_length, projects)

   # get issue type(s)
   print("Enter the number that corresponds to the issue types on which you would like to filter")
   type = input("[ 0 ]: All Standard Issue Types\n[ 1 ]: Specific Issue Types\nSelection: ")
   while type not in ("0", "1"): 
      type = input("Please enter either 0 or 1 to make your selection.\nSelection: ")
   # jira has a funtion for all standard issue types
   if type == "1":
      t_choice = "standardIssueTypes()"
      t_query = t_choice
   # figure out which issue types the user wnats
   else:
      print("Below is a list of the issue types you may select. Please enter the number(s) corresponding to your choice of issue type. If more than one, please separate each number with a comma (ex: 1,3,4).")
      t_query = show_list_get_choice(t_length, types)

   # get version(s)
   print("Below is a list of available versions to choose from. Please enter the number(s) corresponding to your choice of version. If more than one, please separate each number with a comma (ex: 1,3,4).")
   v_query = show_list_get_choice(v_length, versions)

   # get component(s)
   print("Below is a list of available components to choose from. Please enter the number(s) corresponding to your choice of component. If more than one, please separate each number with a comma (ex: 1,3,4).")
   c_query = show_list_get_choice(c_length, components)
   '''

   # building query
   p_query = "STREET"
   t_query = "Bug,Improvement,\"New Feature\",Story,Task"
   v_query = "Magic"
   c_query = "iOS,\"AND\",WWW,QA"
   jql_query = f"project in ({p_query}) AND issuetype in ({t_query}) AND fixVersion in ({v_query}) AND component in ({c_query})"

   #filter_name = input("What would you like to name your filter?\nName:")
   
   # project in (JAZZ, OP, RAT, STREET) AND issuetype in (Bug, Improvement) AND fixVersion = Magic AND component in ("AND", iOS, QA, WWW)
      
   
   endpoint = "/rest/api/3/search"
   url = f"https://penngineering.atlassian.net{endpoint}"

   # ideally would not have email & token hard coded.
   auth = HTTPBasicAuth(email, token)

   headers = {
      "Accept": "application/json",
      "Content-Type": "application/json"
   }

   payload = json.dumps( {
   "jql": "type = Bug and resolution is empty",
   "name": "Tamara test filter 1",
   "description": "Lists all open bugs"
   } )

   # jql_query = "project = JAZZ AND issuetype in (Bug, Improvement, \"New Feature\", Story, Task) AND fixVersion = Magic AND component in (\"AND\", iOS, QA, WWW)"
   all_results = False
   pointer = 0
   counter = 0
   key_list = []
   summary_list = []

   query = {
      'jql': jql_query,
      'fields': "summary",
      'maxResults': 500
   }

   while all_results == False:
      response = requests.request(
         "GET",
         url,
         #data=payload,
         headers=headers,
         params=query,
         auth=auth
      )

      holder = json.loads(response.text)
      # this is just to help me see what the response looks like
      result = json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))
      f = open("test.txt", "w")
      f.write(result)
      f.close()

      # check if results are paginated
      pointer = pointer + holder['maxResults']
      if pointer < holder['total']:
         all_results = False
         # append page results to lists
         for i in range(len(holder["issues"])):
            key_list.append(holder["issues"][i].get('key'))
            summary_list.append(holder["issues"][i].get('fields').get('summary'))
         # update query to start at 'next page'
         query = {
            'jql': jql_query,
            'fields': "summary",
            'maxResults': 500,
            'startAt': pointer
         }
      else:
         all_results = True
         # append page results to lists
         for i in range(len(holder["issues"])):
            key_list.append(holder["issues"][i].get('key'))
            summary_list.append(holder["issues"][i].get('fields').get('summary'))
   