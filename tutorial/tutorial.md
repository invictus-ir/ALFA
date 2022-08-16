# ALFA Tutorial

## Setup
Having installed ALFA (see the [README](../README.md)), begin by initializing a new project directory.

```alfa init tutorial```

You should now have a new directory called "tutorial". ```cd`` into it.
Inside, you'll find a structure similar to the following:
```
.
├── config
│   └── config.yml
└── data
```

Ordinarily, you would place a ```credentials.json``` file into the "config" directory. This won't be necessary for the tutorial.
Instead, a pre-made dataset will be used.
```cd``` into the "data" directory, and
clone the sample dataset
[here](https://github.com/invictus-ir/gws_dataset.git).
```
git clone https://github.com/invictus-ir/gws_dataset.git
```

Your directory structure should now look like:
```
.
├── config
│   └── config.yml
└── data
    └── gws_dataset
        ├── LICENSE
        ├── README.md
        ├── admin.json
        ├── calendar.json
        ├── drive.json
        ├── groups_enterprise.json
        ├── login.json
        ├── token.json
        └── user_accounts.json
```

You are now ready to run ALFA against the dataset.

## Running ALFA
```cd``` back into the root of your project folder.
Load the entire gws_dataset directory using the following command:

```
alfa load -p data/gws_dataset
```
ALFA will automatically load every json file in the directory into its dataset.

You have dropped into a Python shell with access to an ALFA object, variable ```A```.
```A``` has 2 important attributes: ```A.events```, and ```A.activities```.

These are datasets that represent the events and activities present in the logs.
In Google Audit Logs, every action is represented by an "activity". Each "activity" contains a list of "events". These events are essentially building blocks for activities. When loaded, ALFA will automatically analyze the events and classify specific events in accordance with the "[MITRE ATT&CK Cloud Matrix Framework](https://attack.mitre.org/matrices/enterprise/cloud/)".

Events and activities have a lot of data. Let's explore the dataset to garner an understanding for the dataset.

```
A.events.shape # (rows, columns) 
A.activities.shape # (rows, columns)
```
We have 9825 events and 9789 activities. Too many to list off.
Let's select a random sample of 10 from each, and produce a summary, to get an idea of what kind of data we're looking at.
Starting with events:
```
summary(A.events.sample(10))

      name       activity_time                              activity_id
----  ---------  --------------------------------  --------------------
6417  authorize  2022-07-19 12:21:35.002000+00:00  -6241941505348084839
6295  authorize  2022-07-19 12:18:15.883000+00:00   4289095237957192984
6257  authorize  2022-07-19 12:17:15.685000+00:00  -3533409653085737212
5378  authorize  2022-07-19 10:51:12.786000+00:00  -3453280989539057832
6786  authorize  2022-07-19 12:31:54.947000+00:00   4287956763103796901
8773  authorize  2022-07-19 13:53:10.243000+00:00   4880599880504672506
7812  authorize  2022-07-19 13:00:25.098000+00:00   -872164451340203101
2310  authorize  2022-07-19 09:10:31.579000+00:00   7105495284863502655
3080  authorize  2022-07-19 09:31:51.872000+00:00   4333762167492228608
3902  authorize  2022-07-19 10:09:28.796000+00:00  -4366756655797941829
```

and moving onto activities:
```
summary(A.activities.sample(10))

                      id.time                   kind                    actor.email               id.applicationName
--------------------  ------------------------  ----------------------  ------------------------  --------------------
-6010887833366957832  2022-07-19T08:00:47.766Z  admin#reports#activity  admin@cloud-response.com  token
 7764407026099878510  2022-07-19T08:53:11.775Z  admin#reports#activity  admin@cloud-response.com  token
 2407139138637242658  2022-07-19T08:26:52.110Z  admin#reports#activity  admin@cloud-response.com  token
-6978932130952386443  2022-07-19T09:12:01.777Z  admin#reports#activity  admin@cloud-response.com  token
 2956946567129110438  2022-07-19T10:35:40.534Z  admin#reports#activity  admin@cloud-response.com  token
-5470615884955105544  2022-07-19T14:02:30.155Z  admin#reports#activity  admin@cloud-response.com  token
 4429007405214477146  2022-07-19T10:22:22.940Z  admin#reports#activity  admin@cloud-response.com  token
 3378976036216458085  2022-07-19T08:30:11.927Z  admin#reports#activity  admin@cloud-response.com  token
 6860468462391716631  2022-08-02T13:41:54.960Z  admin#reports#activity  admin@cloud-response.com  token
 1895767229440860272  2022-07-19T10:48:12.979Z  admin#reports#activity  admin@cloud-response.com  token
```

From the summary note the following:
 - Each event has a name, and belongs to an activity
 - Each activity has a kind. Some have emails belonging to the user that initiated that activity.

Suppose you wanted to take a deeper look at the events belonging to one of these activities.
We'll select the activity_id of first activity, "-6010887833366957832" for this example.

```
A.activities.loc['-6010887833366957832'].events

[{'name': 'authorize',
  'parameters': [{'name': 'client_id', 'value': '106850843410684334493'},
   {'name': 'app_name', 'value': '106850843410684334493'},
   {'name': 'client_type', 'value': 'WEB'},
   {'name': 'scope_data',
    'multiMessageValue': [{'parameter': [{'name': 'scope_name',
        'value': 'https://www.googleapis.com/auth/admin.reports.audit.readonly'},
       {'name': 'product_bucket', 'multiValue': ['GSUITE_ADMIN']}]}]},
   {'name': 'scope',
    'multiValue': ['https://www.googleapis.com/auth/admin.reports.audit.readonly']}],
  'attack.label': ['application_access_token.use_alternate_authentication_material.defense_evasion',
   'steal_application_access_token.credential_access'],
  'attack.category': ['defense_evasion', 'credential_access'],
  'attack.index': 4,
  'activity_id': '-6010887833366957832',
  'activity_time': Timestamp('2022-07-19 08:00:47.766000+0000', tz='UTC')}]

```

Reading through the mess of data, we see it's an authorize event (like the events in our sample). Aside from the data that Google provides, the events are also marked with an "attack.label", "attack.category" and "attack.index".

These columns are added by ALFA during analysis. "attack.label" contains a list of the *full* MITRE ATT&CK path. "attack.category" is the last portion of the path, and the index is a value that corresponds to the label. The higher the "attack.index", the further along the event is in the MITRE ATT&CK Cloud Matrix Framework. This is useful for calculating "Kill Chains", as will be explored in the following section.

## Kill Chain Analysis
Every ALFA object (```A```) is a collection of activities and events. The events can be analysed to assess how closely they fit a "kill chain", using the "kill chain statistic".
The "kill chain statistic", or kcs, is defined as the "tendency for a set of chronologically ordered events to escalate up the MITRE ATT&CK Cloud Matrix Framework". In other words, "how well does my dataset fit a kill chain?". It is a floating point score between -1 and 1. 1 indicates a perfect kill chain, -1 indicates moving in the complete opposite direction. A score close to 0 indicates undirected events (no pattern).

Let's grab the kcs for the entire dataset:
```
A.kcs()

0.09208973121583104
```

We have a score just shy of 0.1. This low score is to be expected for the entire dataset. However, there may exist kill chains _within_ the dataset. To discern these, ALFA has a "subchains" method. Let's find some subchains.

```
summary( A.subchains() )

----  ----  --------
9428  9435  0.928571
9680  9687  0.857143
  12    19  0.714286
  26    33  0.714286
  33    40  0.714286
 151   158  0.714286
9366  9373  0.714286
9814  9821  0.714286
  76    83  0.714286
9500  9507  0.714286
----  ----  --------

```

Here we have a list of kill chains, each with 3 values. The first value is the start index of the kill chain. This is index of the first event in the kill chain. e.g
```A.events.loc[9428]```. The second value is the end_index of the kill chain. Lastly, there is the kcs for the given kill chain. Note that the subchains are ordered by highest-kcs first.

0.93 is a very high score! Let's take a closer look at those events:
```
summary(A.events[9428:9435])

      name                activity_time                              activity_id
----  ------------------  --------------------------------  --------------------
9428  change_user_access  2022-08-02 07:12:37.638000+00:00  -8593694044162584673
9429  create              2022-08-02 07:12:37.638000+00:00  -8593694044162584673
9430  change_acl_editors  2022-08-02 07:12:37.638000+00:00  -8593694044162584673
9431  add_to_folder       2022-08-02 07:12:37.638000+00:00  -8593694044162584673
9432  login_verification  2022-08-02 07:13:37.996000+00:00          258855114937
9433  login_success       2022-08-02 07:13:37.996000+00:00          258855114937
9434  download            2022-08-02 07:13:57.079000+00:00   3276112931527544503
```

The event names can help display an overview of what occurred in this moment. By displaying the activity_time, they can also help direct you at particular points in the log which may be of interest.

Perhaps looking at the activities these events belong to is helpful. Note that there are only 3 activities associated with these 7 events.

```
summary( A.events[9428:9435].activities() )
                      id.time                   kind                    actor.email                   id.applicationName
--------------------  ------------------------  ----------------------  ----------------------------  --------------------
-8593694044162584673  2022-08-02T07:12:37.638Z  admin#reports#activity  workspace@cloud-response.com  drive
        258855114937  2022-08-02T09:32:37.406Z  admin#reports#activity  workspace@cloud-response.com  login
 3276112931527544503  2022-08-02T07:13:57.079Z  admin#reports#activity  workspace@cloud-response.com  drive

```

Here we can see which account is associated with the behavior, and where it originated from.

## Activities of Interest

As mentioned above, finding interesting activities can aid the discovery of interesting portions of the dataset.
To automate this, one can utilise "activites of interest" (aoi) method:

```
In [26]: summary( A.aoi() )
                      id.time                   kind                    actor.email                    id.applicationName
--------------------  ------------------------  ----------------------  -----------------------------  --------------------
-8637423948085216889  2022-03-14T18:07:54.887Z  admin#reports#activity  admin@cloud-response.com       admin
        768087181562  2022-03-19T15:24:52.241Z  admin#reports#activity  greg@cloud-response.com        login
-7684398170435703864  2022-03-14T20:36:48.966Z  admin#reports#activity  greg@cloud-response.com        calendar
-5686198897511485377  2022-03-19T19:38:47.642Z  admin#reports#activity  admin@cloud-response.com       groups_enterprise
 4000677510509368906  2022-03-19T21:13:29.295Z  admin#reports#activity  greg@cloud-response.com        token
-4185571506150141986  2022-03-19T21:31:14.993Z  admin#reports#activity  greg@cloud-response.com        token
 8275857749769031410  2022-03-19T21:35:04.656Z  admin#reports#activity  greg@cloud-response.com        token
-4582372916506076442  2022-03-19T22:17:46.663Z  admin#reports#activity  admin@cloud-response.com       token
        722534617001  2022-08-15T16:24:08.797Z  admin#reports#activity  admin@cloud-response.com       login
...
```

The ```aoi``` method will return a list of all activities whose events appeared in a subchain. As such, it's a quick shortcut for finding interesting sections of the logs.

These activities can be exported to a json file, to be fed into a tool of your choosing:
```
A.aoi(export='wow.json')
```


