from datetime import datetime, time, timedelta
import tzlocal
from googleapiclient.errors import HttpError

def get_start_of_today():
    local_tz = tzlocal.get_localzone()
    now = datetime.now(local_tz)
    start_of_today = datetime.combine(now.date(), time.min(), tzinfo=local_tz)
    return start_of_today.isoformat()

def get_events_today(service):
  start_of_today = get_start_of_today()
  start_of_tomorrow = start_of_today + timedelta(days=1)
  
  try:
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_today,
            timeMax=start_of_tomorrow,
            singleEvents=True,
            orderBy="startTime, endTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
  except HttpError as error:
    print(f"An error occurred: {error}")
    events = []
  return events