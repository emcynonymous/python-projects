import os
from typing import List

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
    response: Response = zoom.get_meeting_registrants(ZOOM_MEETING_ID, jwt_token)
    list_of_registrants: List[dict] = response.json().get("registrants")

    while token := response.json().get("next_page_token"):
        response = zoom.get_meeting_registrants(ZOOM_MEETING_ID, jwt_token, token)
        list_of_registrants += response.json().get("registrants")

    df: DataFrame = pd.DataFrame(list_of_registrants).drop(columns=["purchasing_time_frame","comments","no_of_employees","role_in_purchase_process","job_title","industry","zip","org","custom_questions","state"])
    print(df.info())
    df.create_time = pd.to_datetime(df.create_time).dt.tz_convert("Asia/Singapore")

    df.sort_values(["create_time"], inplace=True)

    #meeting_date: str = df.create_time.tolist()[0].split(" ")[0]
    #print(f" last entry {meeting_date} ")
    #output_file: str = f"zoom_report_{meeting_date}"
    output_file: str = f"zoom_report_registered"

    googl = Googl(SERVICE_ACCOUNT_FILE, SCOPES)

    zoom_folder_id: str = googl.get_folder_id("Zoom") #Zoom
    sheet_id = googl.create_new_sheet(output_file, zoom_folder_id)
    result = googl.insert_df_to_sheet(sheet_id, df)
    sheet_link = googl.get_sheet_link(result.get("spreadsheetId"))

    print(f"Finished uploading Zoom report.\n"
          f"spreadsheetId: {result.get('updates').get('spreadsheetId')}\n"
          f"updatedRange: {result.get('updates').get('updatedRange')}\n"
          f"updatedRows: {result.get('updates').get('updatedRows')}\n"
          f"link: {sheet_link}")
