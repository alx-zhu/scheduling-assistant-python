import streamlit as st
from datetime import datetime
from google_cloud_services import get_calendar_service
from googleapiclient.errors import HttpError

@st.cache(allow_output_mutation=True)
def get_cached_calendar_service():
    return get_calendar_service()

def show_events():
    try:
        service = get_cached_calendar_service()

        # Call the Calendar API
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        st.write("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            st.write("No upcoming events found.")
            return

        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            st.write(f"{start} - {event['summary']}")

    except HttpError as error:
        st.write(f"An error occurred: {error}")

def main():
    st.title("Google Calendar Events")
    if st.button("Show Events"):
        show_events()

if __name__ == "__main__":
    main()
