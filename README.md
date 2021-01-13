# Matcha
Matcha is a dating site that allows people to meet based on their sexual preferences intrests and location, alot like tinder.

# Requirements
1. Python
2. pip 


# Application setup steps
1. Create the virtual enviroment 
    `python3 -m venv MatchaEnviron`
2. From the root folder change the source
    `source ./MatchaEnviron/bin/activate` to start | `dectivate` to stop
3. Create a new directory call it apps
    `cd ./MatchaEnviron && mkdir apps && cd apps`
4. Clone matcha into this directory
    `git clone http://github.com/rubzy0422/matcha && cd matcha`
5. Create the test data (Optional)
    `cd ./matcha/testdata/ && python3 data.py` 
    Use the UI to create new records. Select one and insert a record count.
    `cd ../`
6. Install dependencies
    `pip install -r requirements.txt`
7. Set Enviroment Variables
    open config file edit MAIL_USERNAME, MAIL_PASSWORD, SECRET_PASSWORD and remove the 	export code lines.
8. Run The application
    `python app.py`

# Architecture:
### Flask Blueprint Architecture
app -> create_app (initialize blueprints)  -> blueprints -> services
app -> blueprint -> serivce 

<b>Auth Blueprint</b> Enables users to register login or reset their passwords
<b>Chat Blueprint</b> Allows users to chat with other users in real time
<b>Error Blueprint</b> Allows for the error handeling of the application 
<b>Main Blueprint</b> Allows admin to make changes as he wishes or needs
<b>Users Blueprint</b> Contains buisness logic for user likes and views and so on

<i>static</i>		the folder where the  static files can be found.
<i>templates</i>	the folder containing the Blueprint templates aswell as shared templates.
<i>utils</i>		the folder that contains the utils that can be used by differnt blueprints.
<i>config</i>		the python file that contains all the needed configuration setup that needs to be shared on the application.
<i>db</i>		the connection method to the database aswell as the setup for all the tables.
<i>decorators</i>	the annotation decorators to ensure that a user is logged in or admin and so on.
    <i>app</i>		the application entry point


## Test outline 
1. Launch the webserver
2. Create an account 
3. Login
4. Edit profile
5. View profile suggestions.
6. Search / Filter
7. Geolocation
8. Populatity flexing
9. Notifications 
10. View a Profile
11. Like / Unlike
12. Block 
13. Messaging

## Expected Outcomes
1. The webserver launches
2. a account has been created and a email has been sent
3. a user can login after verifying his/ her password
4. a user can edit their profile 
5. a user should see reccomended profiles 
6. a user should be able to filter / search for a profile
7. Geolocation should be supported
8. People should have popularity ratings
9. You should be able to receive Notifications
10. You should be able to view a profile
11. You should be able to like / Unlike a profile
12. You should be able to block a profile
13. You should be able to send a message to a connected user and receive one back ````
