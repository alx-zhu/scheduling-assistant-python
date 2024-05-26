import streamlit as st
from datetime import datetime
from google_cloud_services import get_calendar_service
from googleapiclient.errors import HttpError
from time_helpers import get_events_today

@st.cache_resource()
def get_cached_calendar_service():
    return get_calendar_service()

def main():
    service = get_cached_calendar_service()
    st.title("Google Calendar Events")
    if st.button("Show Events"):
      events = get_events_today(service)
      # Prints the start and name of the next 10 events
      for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(start, event["summary"])
        st.write(f"{start}, {event["summary"]}")
        

if __name__ == "__main__":
    main()
