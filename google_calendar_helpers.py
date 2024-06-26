from datetime import datetime, time, timedelta
import tzlocal
from googleapiclient.errors import HttpError

local_tz = tzlocal.get_localzone()
local_tz_name = tzlocal.get_localzone_name()

def get_events_today(service):
  now = datetime.now(local_tz)
  start_of_today = datetime.combine(now.date(), datetime.min.time(), tzinfo=local_tz)
  start_of_tomorrow = start_of_today + timedelta(days=1)
  
  try:
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_today.isoformat(),
            timeMax=start_of_tomorrow.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
  except HttpError as error:
    print(f"An error occurred: {error}")
    events = []
  return events

def get_events_on_date(service, date):
  start_of_date = datetime.combine(date, time.min)
  end_of_date = datetime.combine(date, time.max)
  
  try:
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start_of_date.isoformat(),
            timeMax=end_of_date.isoformat(),
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
  except HttpError as error:
    print(f"An error occurred: {error}")
    events = []
  return events

# https://developers.google.com/calendar/api/v3/reference
def insert_event(service, summary: str, start_time: str, end_time: str, **kwargs):
  event = {
    'summary': summary,
    'start': {
      'dateTime': start_time,
      'timeZone': local_tz_name,
    },
    'end': {
      'dateTime': end_time,
      'timeZone': local_tz_name,
    },
  }

  try:
    event = service.events().insert(calendarId='primary', body=event).execute()
    event_link = event.get('htmlLink', "")
  except HttpError as error:
    print(f" An error occurred: {error}")
    event_link = ""

  print('Event created: %s' % (event_link))
  return event_link

  # event = {
  #   'summary': 'Google I/O 2015',
  #   'location': '800 Howard St., San Francisco, CA 94103',
  #   'description': 'A chance to hear more about Google\'s developer products.',
  #   'start': {
  #     'dateTime': '2015-05-28T09:00:00-07:00',
  #     'timeZone': 'America/Los_Angeles',
  #   },
  #   'end': {
  #     'dateTime': '2015-05-28T17:00:00-07:00',
  #     'timeZone': 'America/Los_Angeles',
  #   },
  #   'recurrence': [
  #     'RRULE:FREQ=DAILY;COUNT=2'
  #   ],
  #   'attendees': [
  #     {'email': 'lpage@example.com'},
  #     {'email': 'sbrin@example.com'},
  #   ],
  #   'reminders': {
  #     'useDefault': False,
  #     'overrides': [
  #       {'method': 'email', 'minutes': 24 * 60},
  #       {'method': 'popup', 'minutes': 10},
  #     ],
  #   },
  # }