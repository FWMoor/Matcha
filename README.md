# Matcha
Matcha is a dating site that allows people to meet based on their sexual preferences interests and location, a lot like tinder.

## Requirements

1. Python

2. pip

# Application setup

1. Create the virtual enviroment<br/>
`python3 -m venv MatchaEnviron`

1. From the root folder change the source<br/>
 `source ./MatchaEnviron/bin/activate` to start<br/> use `dectivate` to stop

1. Create a new directory call it apps<br/>
 `cd ./MatchaEnviron && mkdir apps && cd apps`

1. Clone matcha into this directory<br/>
 `git clone https://github.com/FWMoor/Matcha && cd matcha`


2. Create the test data (Optional)<br/>
 `python3 /matcha/testdata/data.py`<br/>
 Use the UI to create new records. Select one and insert a record count.

1. Install dependencies<br/>
 `pip install -r requirements.txt`

1. Set Enviroment Variables<br/>
open the config file edit atleast the following<br/> _MAIL_USERNAME_, _MAIL_PASSWORD_, _SECRET_PASSWORD_

1. Run The application<br/>
	`python app.py`

# Architecture:

## Flask Blueprint Architecture

app -> create_app (initialize blueprints) -> blueprints -> services

app -> blueprint -> service

**Auth Blueprint** Enables users to register login or reset their passwords

**Chat Blueprint** Allows users to chat with other users in real time

**Error Blueprint** Allows for the error handling of the application

**Main Blueprint** Allows admin to make changes as he wishes or needs

**Users Blueprint** Contains business logic for user likes and views and so on

**_Static_** the folder where the static files can be found.

**_Templates_** the folder containing the Blueprint templates as well as shared templates.

**_Utils_** the folder that contains the utilities that can be used by different blueprints.

**_Config_** the python file that contains all the needed configuration setup that needs to be shared on the application.

**_Db_** the connection method to the database as well as the setup for all the tables.

**_Decorators_** the annotation decorators to ensure that a user is logged in or admin and so on.

**_app_** the application entry point

# Testing
## Test outline

1. Launch the webserver
2. Create an account
3. Login
4. Edit profile
5. View profile suggestions.
6. Search / Filter
7. Geolocation
8. Popularity flexing
9. Notifications
10. View a Profile
11. Like / Unlike
12. Block
13. Messaging

## Expected Outcomes

1. The webserver launches
2. an Account has been created and an email has been sent
3. a User can login after verifying his/ her password
4. a User can edit their profile
5. a User should see recommended profiles
6. a User should be able to filter / search for a profile
7. Geolocation should be supported
8. People should have popularity ratings
9. You should be able to receive Notifications
10. You should be able to view a profile
11. You should be able to like / Unlike a profile
12. You should be able to block a profile
13. You should be able to send a message to a connected user and receive one back