# Getting Your Credentials
This step by step guide takes you through the process of obtaining your API credentials.
You can also watch our YouTube video where we show you the whole process **insert link** <br><br>

It is recommended that you register a new project for log collection, separate from other projects.

## Permissions
First and foremost, the Admin SDK API used to collect the audit logs requires that the user has admin privileges. You can enable admin privileges through
the following tutorial: https://support.google.com/a/answer/172176

## Creating an OAuth app
1. Go to https://console.cloud.google.com/cloud-resource-manager
2. Create a project, or use an existing project.
3. Go to https://console.developers.google.com/apis/dashboard
    - Make sure your new project is selected, near the top-left of the website, close to the "Google Cloud Platform" logo, select your project
    - In the sidebar, choose "Credentials", then "Oauth Client ID"
4. Select "Create Credentials", choose "Oauth client ID"
5. At this point you may be prompted to "configure consent screen". This is dealt with in the next section. If you do not receive this prompt,
skip over to the section "Create OAuth ID"

## Configuring The Consent Screen (Optional)
1. Select "configure consent screen"
2. select the user type. If you do not know which to select, use the "Internal" type.
3. You will be prompted to fill in details about the "App"
  - give you app any unique name. It is recommended to use a descriptive name such as "Alfa Log Collecting"
  - fill out all the required fields. All other fields can be filled to your discretion.

### Adding Scopes (Optional)
You will now be prompted to "add or remove scopes". This step is not necessary, as it will not affect the outcome script.
However if you intend to grant access to third-parties, you may wish to disclose the scopes here.

## Create OAuth ID
1. Select "web application" as application type
2. Give the "web application" a descripting name, e.g."Alfa Log Collecting API"
3. Under "Authorised redirect URIs" add "http://localhost:8089/"
3. Click create. A popup will appear with your API credentials.
4. Download the JSON to ```config/credentials.json``` in your project's folder

## Enabling APIs
You will need to enable access to the Admin SDK.
1. go to https://console.cloud.google.com/apis/library/admin.googleapis.com
2. enable the SDK

## Afterword
Your credentials are now ready for use. When the first query is run, a browser window will open and you will be prompted to grant the appropriate permissions.
After this, a new 'token.json' file will appear in the config/ directory.

**NOTE**: A common error occurs regarding the "refresh token". This may happen if you delete the token.json file. This is due to a security feature of Google Cloud:
When you first grant permission to the script, the resulting token.json file contains a "refresh-token" parameter. This only occurs **once**. Subsequent recreation
of the token.json file will **not** include this token. 
To retrieve the token, you must delete the existing permissions and re-grant them.
The following explains how to remove third-party apps: https://support.google.com/accounts/answer/3466521
After removal, simply run a query and re-grant the permissions
