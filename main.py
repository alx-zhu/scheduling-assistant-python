import streamlit as st
from datetime import datetime
import json
import tzlocal
from google_cloud_services import get_calendar_service
import google_calendar_helpers as gcal
from constants import (
    OPENAI_INITIAL_CONVERSATION,
    CALENDAR_OPTIONS,
    CUSTOM_CSS,
)
from openai import OpenAI
import time
from streamlit_calendar import calendar
from dotenv import load_dotenv

load_dotenv()


@st.cache_resource()
def get_cached_calendar_service():
    return get_calendar_service()


@st.cache_resource()
def get_cached_openai_service():
    return OpenAI(api_key=st.secrets["OPENAI"]["OPENAI_API_KEY"])


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
    if "message_count" not in st.session_state:
        st.session_state.message_count = 0

    if "display_conversation" not in st.session_state:
        st.session_state.display_conversation = []

    if "calendar_events" not in st.session_state:
        st.session_state.calendar_events = []
        events = gcal.get_events_today(service)
        for event in events:
            start = event["start"].get("dateTime", None)
            end = event["end"].get("dateTime", None)
            title = event["summary"]
            if start and end and title:
                st.session_state.calendar_events.append(
                    {
                        "title": title,
                        "start": start,
                        "end": end,
                    },
                )
        print(st.session_state.calendar_events)

    if "gpt_conversation" not in st.session_state:
        st.session_state.gpt_conversation = OPENAI_INITIAL_CONVERSATION

        # Add user's events today to the conversation history befor sending.
        st.session_state.gpt_conversation.append(
            {
                "role": "user",
                "content": f"Today is {datetime.now().date()} and I live in the timezone {tzlocal.get_localzone_name()}. Here are my events for today: {json.dumps(st.session_state.calendar_events)}",
            }
        )

        completion = open_ai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.gpt_conversation,
        )
        response = completion.choices[0].message.content

        response_object = json.loads(response)
        response_msg = response_object["message"]
        st.session_state.gpt_conversation.append(
            {"role": "assistant", "content": response}
        )
        st.session_state.display_conversation.append(
            {"role": "assistant", "content": response_msg.replace("\n", "  \n")}
        )
        print(response)

    # Streamlit Page
    st.title("Scheduling Assistant")

    # Main body
    calendar(
        events=st.session_state.calendar_events,
        options=CALENDAR_OPTIONS,
        custom_css=CUSTOM_CSS,
    )

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
            if st.session_state.message_count > 10:
                st.warning(
                    "You have passed your limit of 10 messages. In order to keep this service free, there is a 10 message limit per user. Please contact alexanderzhu07@gmail.com for any questions."
                )

            elif prompt := st.chat_input("Message the Scheduling Assistant"):
                st.session_state.message_count += 1

                # Display user message in chat message container
                with user_placeholder:
                    st.chat_message("user").markdown(prompt)
                # Add user message to chat history
                st.session_state.display_conversation.append(
                    {"role": "user", "content": prompt}
                )
                st.session_state.gpt_conversation.append(
                    {"role": "user", "content": prompt}
                )

                # Send message to Open AI
                completion = open_ai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=st.session_state.gpt_conversation,
                )

                response = completion.choices[0].message.content
                # try:
                #     response_object = json.loads(response, strict=False)
                #     print(response_object)
                # except json.JSONDecodeError as e:
                #     print(f"JSON decode error: {e}")

                # Parse the Open AI response into an object
                response_object = json.loads(response)
                print(response_object)
                response_msg = response_object["message"]
                response_events = response_object["events"]

                # Display assistant response in chat message container
                with assistant_placeholder:
                    with st.chat_message("assistant"):
                        # st.write_stream(response_generator(response_msg))
                        st.markdown(response_msg.replace("\n", "  \n"))

                # Add assistant response to chat history
                st.session_state.display_conversation.append(
                    {"role": "assistant", "content": response_msg}
                )
                st.session_state.gpt_conversation.append(
                    {"role": "assistant", "content": response}
                )

                # Add the event to the calendar if there are any
                # for now, limit to a single event
                if len(response_events) == 1:
                    for event in response_events:
                        eventLink = gcal.insert_event(
                            service, event["title"], event["start"], event["end"]
                        )
                        st.session_state.display_conversation.append(
                            {
                                "role": "assistant",
                                "content": f"View your new event in Google Calendar here: {eventLink}",
                            }
                        )
                        st.session_state.calendar_events.append(event)
                        st.rerun()


if __name__ == "__main__":
    main()

    # st.title("Google Calendar Events")
    # if st.button("Show Events"):
    #     events = gcal.get_events_today(service)
    #     # Prints the start and name of the next 10 events
    #     for event in events:
    #         start = event["start"].get("dateTime", event["start"].get("date"))
    #         print(start, event["summary"])
    #         st.write(f"{start} | {event['summary']}")

    # if st.button("Add Test Event"):
    #     now = datetime.now()
    #     later = now + timedelta(hours=1)
    #     eventLink = gcal.insert_event(
    #         service, "Test Event", now.isoformat(), later.isoformat()
    #     )
    #     st.write(f"New event created on Google Calendar: {eventLink}")
