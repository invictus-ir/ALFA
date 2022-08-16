# ALFA
## Automated Audit Log Forensic Analysis for Google Workspace
Copyright (c) 2022 Invictus Incident Response <br>
Authors [Greg Charitonos](https://www.linkedin.com/in/charitonos/) & [BertJanCyber](https://twitter.com/BertJanCyber) 

# Before you start
A note on supported operating systems, ALFA is tested on several Linux distributions (Debian and Ubuntu).
Using it on Windows/macOS might work or not, in our experience it's a mixed bag so use at your own risk. 

# Installation
1. Download this project
2. Navigate to the folder in your terminal and run ```pip install -e .``` or ```pip3 install -e .```


## Using ALFA
NOTE: For retrieving credentials.json, please see ```CREDENTIALS.md```

## Setup
1. The first step is to initialize ALFA do this by running ```alfa init projectname``` this command will create a new directory to store your configuration and data. E.g. ```alfa init project_x```
2. A new project has now been generated called 'project_x'. Within that folder copy your credentials.json into the config/ folder. **(See CREDENTIALS.md) for instructions. **
3. After you have copied over the credentials.json file you are ready to use ALFA.

ALFA has 3 options as explained below:

## 1. ALFA Acquire
## Acquire all Google Workspace Audit Logs
1. From inside "project_x" (or whatever name you chose before) run ```alfa acquire```
2. ALFA will now grab all logtypes for all users and save them to a subdirectory in the 'data' folder a .json file will be generated per logtype
3. To see what other options you have type ```alfa acquire -h``` 

## Advanced acquisitions with ALFA
You can do all kinds of filtering to limit the data you are acquiring some examples below:
- Only grab the 'admin' logtype ```alfa acquire --logtype=admin```
- Save the output to a specific folder ```alfa acquire -d /tmp/project_secret```
- Only grab logs for a specific user ```alfa acquire --user=insert_username```
- Grab logs within a defined timeperiod ```alfa acquire --start-time=2022-07-10T10:00:00Z --end-time=2022-07-11T14:26:01Z``` the timeformat is (RFC3339)

Now you know how to acquire data time for some fancy stuff to unleash the power of ALFA. 

## 2. ALFA Analyze
The analyze function automatically analysis all audit log data for a given Google Workspace to identify suspicious activity. 
### How this works
1. Categorization
Each individual event is categorized based on a mapping that is made alfa/config/event_to_mitre.yml. If an event matches that lists it is mapped to a technique that is part of the MITRE ATT&CK Cloud Framework (https://attack.mitre.org/matrices/enterprise/cloud/). 

2. Scoring
Next ALFA will analyze all mapped events in chronological order to try to identify kill chains or logical attack paths. 
E.G. An event that is mapped to the Persistence phase followed by an event that is mapped to the Credential Access phase will result in a higher score. 

3. Result
Ultimately ALFA will give the analyst a list of identified 'subchains' that can be further analyzed. 

### How to use ALFA analyze?
1. First run ```alfa analyze``` which will automatically identify (or not if none were found). It will also drop you in a shell where you can perform follow up activities. 
2. To get more information on a given subchain you can simply run A.subchains() which will show you the chain using the following format (number_of_first_event_in_chain,number_of_last_event_in_chain,killchain_score). Where a score 1 means a perfect chain was identified and the closer it gets to 0 the weaker the chain is.  
3. In order to access the suspicious events that caused this chain use ```A.aoi(export='activities.json')``` to export all identified subchains to a file, that you can then use for further analysis. 


## 3. ALFA Load 
## Load data from local storage
### From Local Storage
Use ```A = Alfa.load([logname])``` to load and analyse logs from local storage Use ```A = Alfa.load('all')``` to load all logs. Alfa *filters* benign activities out, by default. To load all activities and events, unfiltered, use ```Alfa.load([logname], filter=False)```. 


## Making Changes
### Adding new event mappings.
It is possible to edit the config/event_to_mitre.yml file directly, but ill-advised. The layout of this file is unintuitive. Instead, consider making amendments to utils/mappings.yml. Then repopulate config/event_to_mitre.yml by running utils/event_mitre_remap.py

### Amending Kill Chain Discovery methods
The kill chain discovery function utilizes hard-coded constants. These can be found in the config/config.yml.
Forensic analysts are advised to review the values and make amendments for their workspace as necessary. 
These constants are responsible for both the kill chain statistic (kcs) and kill chain discovery (subchains).

## FAQ
Want to know more about the statistics and algorithm used for ALFA, we wrote a blog post about it here(insert link)

## Known Errors
ValueError: missing config/credentials.json <br>
You have to add a credentials.json file to the project folder in the 'config' subdirectory. Instructions in the 'CREDENTIALS.md' file. 

OSError: [Errno 98] Address already in use
This means that port 8089 is already in use by another application, this could happen if you have a webserver running on this port and also Splunk uses port 8089 by default. Solution is to (temporarily) stop that port from being used as it's required for the authentication flow that the port is available. 

ValueError: Authorized user info was not in the expected format, missing fields refresh_token.
Sometimes the authorization info needs to be updated the easiest way to do this is removing the 'token.json' from the project_name/config folder. And then rerunning the command. If that still gives issues then remove token.json and credentials.json and reregister the OAuth application as described in 
```CREDENTIALS.MD```
