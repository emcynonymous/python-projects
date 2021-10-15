import os
from typing import List
import json

import pandas as pd
from pandas import DataFrame
from requests import Response

from googl import Googl
from zoom import Zoom

ZOOM_API_KEY = os.environ.get("ZOOM_API_KEY")
ZOOM_API_SECRET = os.environ.get("ZOOM_API_SECRET")
ZOOM_MEETING_ID = os.environ.get("ZOOM_MEETING_ID")

SERVICE_ACCOUNT_FILE = f".secrets/{os.listdir('.secrets')[0]}"
SCOPES = ["https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/drive.file"]


if __name__ == "__main__":
    zoom = Zoom(ZOOM_API_KEY, ZOOM_API_SECRET)

    jwt_token: bytes = zoom.generate_jwt_token()
    response: Response = zoom.get_meeting_participants(ZOOM_MEETING_ID, jwt_token)
    list_of_participants: List[dict] = response.json().get("participants")

    while token := response.json().get("next_page_token"):
        response = zoom.get_meeting_participants(ZOOM_MEETING_ID, jwt_token, token)
        list_of_participants += response.json().get("participants")
        y = list_of_participants.text
        name = list_of_participants["name"]
        email = list_of_participants["user_email"]
        print(f"name {name} email {email}        ")

    df: DataFrame = pd.DataFrame(list_of_participants)

#    output_df: DataFrame = df.groupby(["id", "name", "user_email"]) \
#        .agg({"duration": ["sum"], "join_time": ["min"], "leave_time": ["max"]}) \
#        .reset_index() \
#        .rename(columns={"duration": "total_duration"})
    
