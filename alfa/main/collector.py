#!/bin/python3

"""
https://developers.google.com/admin-sdk/reports/reference/rest/v1/activities/list

dates: https://www.ietf.org/rfc/rfc3339.txt

"""
import json
from json.decoder import JSONDecodeError
import os
import os.path
from datetime import datetime

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build

from ..config import config
from ..config.__internals__ import internals
from ..utils.path import *

PORT = 8089

creds_path = os.path.join(
    internals["project"]["dirs"]["configs"], internals["project"]["files"]["creds"]
)
token_path = os.path.join(
    internals["project"]["dirs"]["configs"], internals["project"]["files"]["token"]
)

DATA_DIR = internals["project"]["dirs"]["data"]

creds_instructions = """
 === Missing "config/credentials.json" ===
1. Go to https://console.developers.google.com/cloud-resource-manager
2. Create a project
3. Go to https://console.developers.google.com/apis/dashboard and choose "Credentials", then "Oauth Client ID"
4. Select "web application" as application type
5. copy the resulting credentials to config/credentials.json 
"""


class Collector:
    """
    Begins authentication flow at init.

    the .query method collects logs. logs are given
    params:
        logtype: either as a string (single log, e.g. "admin"), a list ["admin", "drive"], or the string "all" to collect all logs
        user: str='all' | userId or email of user. 'all' => all users
        max_results: int=1000 | max results per page
        max_pages: int = None | max number of pages (requests per log)
        start_time: str=None | rfc3339 date string. must be less than end time
        end_time: str=None | rfc3339 date string. must be greater than start time
    """

    SCOPES = config["scopes"]

    def __init__(self) -> None:
        self.api_ready = False
        pass

    def __init_api_creds(self):
        """
        should be called before interacting with api
        """
        self.creds = self.get_credentials()
        self.service = self.connect_api()
        self.request_count = 0
        self.api_ready = True
        pass

    def __create_path(self, path: str):
        """create path if non-existent"""
        full_path = rel_path(path)
        if os.path.exists(full_path):
            return full_path
        os.makedirs(full_path)
        return full_path

    def get_credentials(self):
        creds = False
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path)

        if not creds or not creds.valid:
            if not os.path.exists(creds_path):
                print(creds_instructions)
                raise ValueError("missing config/credentials.json")
            if creds and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    creds_path, self.SCOPES
                )
                creds = flow.run_local_server(port=PORT)
            with open(token_path, "w") as token:
                token.write(creds.to_json())
        return creds

    def connect_api(self):
        service = build("admin", "reports_v1", credentials=self.creds)
        return service

    def query_one(
        self,
        logtype: str,
        user: str = "all",
        max_results: int = 1000,
        max_pages: int = None,
        start_time: str = None,
        end_time: str = None,
        **kwargs,
    ) -> list:
        """
        used by the .query method
        collects activities from a single logtype, and returns them as a list
        """
        activities = self.service.activities()
        req = activities.list(
            userKey=user,
            applicationName=logtype,
            maxResults=max_results,
            startTime=start_time,
            endTime=end_time,
        )
        page_index = 0

        result = []
        while req is not None:
            if max_pages and page_index > max_pages:
                break
            self.request_count += 1
            resp = req.execute()
            my_activities = resp.get("items", [])
            result += my_activities
            req = activities.list_next(req, resp)
            page_index += 1
        return result

    def query(
        self,
        logtype: str,
        user: str = "all",
        max_results: int = 1000,
        max_pages: int = None,
        start_time: str = None,
        end_time: str = None,
        save=False,
        nd=False,
        path=None,
        return_as_df=True,
        **kwargs,
    ) -> list:
        """
        Queries the API directly. Returns a DataFrame of all log files.
        Args:
          logtype: 'all' or a logtype such as 'admin' or 'login'.
          user: 'all' (default) or a userId or user email address
          max_results: maximum results per page (default 1000, max)
          max_pages: max number of pages (default: None, as many pages as available)
          start_time: in rfc3339 format
          end_time: in rfc3339 format
          save: should this query be saved directly to storage
          path: directory to save under
        """
        if not self.api_ready:  # first initialize the api
            self.__init_api_creds()

        if logtype == "all":
            logtype = config["logs"]  # all logs
        elif type(logtype) == str:
            logtype = [logtype]  # convert to list of len 1

        results = {"activities": dict()}
        total_activity_count = 0
        save_path = self.__default_path_name()
        if path:
            save_path = path
        for typ in logtype:
            res = self.query_one(
                typ, user, max_results, max_pages, start_time, end_time
            )
            results["activities"][typ] = res
            total_activity_count += len(res)
            print(f"{typ:>25}:", f"{len(res):>6}", "activities")
            if save and len(res):
                self.save({"activities": res}, save_path, typ + ".json", nd)

        if save:
            print("\n", total_activity_count, "activities saved to:", save_path)

        if return_as_df:
            return self.get_activities_df(results)
        return results

    def compute_df(self, activities_json: dict) -> pd.DataFrame:
        return pd.json_normalize(activities_json)

    def get_activities_df(self, data: dict) -> pd.DataFrame:
        """
        expects a json file in the form: {query: {...}, activities: [...] | {...}
        extracts the activities, normalizes, and returns as a dataframe.
        if activities is a dict, it assumes that the dict is in the form {'logtype': [...activities...]}, and
            appends a new column, 'logtype' to the dataframe
        """
        activities = data["activities"]
        if type(activities) == list:
            return pd.json_normalize(activities)
        if type(activities) == dict:
            prev_df = pd.DataFrame()
            for key in activities:
                df = pd.json_normalize(activities[key])
                df["logtype"] = key
                prev_df = pd.concat([prev_df, df], ignore_index=True)
            return prev_df
        return None

    def __default_path_name(self):
        """the default naming convention for paths. This is produced as a datetime string corresponding approx. to when the query was initiated"""
        return os.path.join(DATA_DIR, datetime.utcnow().strftime("%y%m%d.%H%M%S"))

    def save(self, data: dict, save_path: str, filename: str, nd: bool):
        """saves the raw JSON along with metadata"""
        if not (save_path[0] == "/" or save_path.startswith("./")):
            save_path = "./" + save_path
        if not save_path.endswith("/"):
            save_path = save_path + "/"
        full_path = self.__create_path(save_path)

        if "activities" in data and type(data["activities"]) == list and nd:
            with open(rel_path(full_path, filename), "w") as f:
                for record in data["activities"]:
                    f.write(json.dumps(record) + "\n")
        else:
            with open(rel_path(full_path, filename), "w") as f:
                json.dump(data, f)
        return data

    def load(self, json_file: str, as_activities_df: bool = True):
        '''
        loads a dataset from a json file. Expects to be normal JSON.
        If it encounters a JSONDecodeError, assumes it is in NDJSON format (newline delimited)
        and attempts to access each record separately.
        '''
        with open(json_file) as f:
            try:
                data = json.load(f)
            except JSONDecodeError:
                f.seek(0)
                activities = []
                for line in f:
                    activities.append(json.loads(line))
                data = {'activities': activities}
        if as_activities_df:
            return self.get_activities_df(data)
        return data

    def load_all(self, data_folder: str, as_activities_df: bool = True):
        all_files = os.listdir(data_folder)
        all_files = [os.path.join(data_folder, x) for x in all_files]
        only_json = filter(
            lambda x: os.path.isfile(x) and x.endswith(".json"), all_files
        )
        result = {"activities": {}}
        for f in only_json:
            data = self.load(f, as_activities_df=False)
            logtype = os.path.basename(f).split(".json")[0]
            activities = data["activities"]
            result["activities"][logtype] = activities
        if as_activities_df:
            return self.get_activities_df(result)
        return result
