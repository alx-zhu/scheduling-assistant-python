import streamlit as st
from datetime import datetime, timedelta
from google_cloud_services import get_calendar_service
from googleapiclient.errors import HttpError
import google_calendar_helpers as gcal
from constants import (
    OPENAI_INITIAL_CONVERSAION,
    CALENDAR_EVENTS,
    CALENDAR_OPTIONS,
    CUSTOM_CSS,
)
from openai import OpenAI
import time
from streamlit_calendar import calendar
import os


@st.cache_resource()
def get_cached_calendar_service():
    return get_calendar_service()


@st.cache_resource()
def get_cached_openai_service():
    print(os.environ.get("OPENAI_API_KEY"))
    return OpenAI()


def response_generator(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


def main():
    # Initialize service
    service = get_cached_calendar_service()
    # Initialize OpenAI Client
    open_ai = get_cached_openai_service()

    # Initialize session state
    if "display_conversation" not in st.session_state:
        st.session_state.display_conversation = []
    if "gpt_conversation" not in st.session_state:
        st.session_state.gpt_conversation = OPENAI_INITIAL_CONVERSAION
        completion = open_ai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.gpt_conversation,
        )
        response = completion.choices[0].message.content
        st.session_state.display_conversation.append(
            {"role": "assistant", "content": response}
        )
        print(response)

    st.title("Google Calendar Events")
    if st.button("Show Events"):
        events = gcal.get_events_today(service)
        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])
            st.write(f"{start} | {event['summary']}")

    if st.button("Add Test Event"):
        now = datetime.now()
        later = now + timedelta(hours=1)
        eventLink = gcal.insert_event(
            service, "Test Event", now.isoformat(), later.isoformat()
        )
        st.write(f"New event created on Google Calendar: {eventLink}")

    st.title("Scheduling Assistant")

    # Main body
    calendar(events=CALENDAR_EVENTS, options=CALENDAR_OPTIONS, custom_css=CUSTOM_CSS)

    # Sidebar
    with st.sidebar:
        with st.container(height=500):
            # Display chat history
            for message in st.session_state.display_conversation:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            user_placeholder = st.empty()
            assistant_placeholder = st.empty()

            # React to user input
            if prompt := st.chat_input("Message the Scheduling Assistant"):
                # Display user message in chat message container
                with user_placeholder:
                    st.chat_message("user").markdown(prompt)
                # Add user message to chat history
                st.session_state.display_conversation.append(
                    {"role": "user", "content": prompt}
                )

                response = f"Echo:\n{prompt}"
                # Display assistant response in chat message container
                with assistant_placeholder:
                    with st.chat_message("assistant"):
                        response = st.write_stream(response_generator(response))
                    # st.markdown(response)

                # Add assistant response to chat history
                st.session_state.display_conversation.append(
                    {"role": "assistant", "content": response}
                )


if __name__ == "__main__":
    main()
