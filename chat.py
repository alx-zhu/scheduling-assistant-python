import streamlit as st
import time
from streamlit_calendar import calendar

calendar_options = {
    "editable": "true",
    "selectable": "true",
    "headerToolbar": {
        "left": "today",
        "center": "title",
        "right": "prev,next",
    },
    # "slotMinTime": "06:00:00",
    # "slotMaxTime": "18:00:00",
    # "initialView": "timelineDay",
    "initialView": "timeGridDay",
}
calendar_events = [
    {
        "title": "Event 1",
        "start": "2024-05-26T08:30:00",
        "end": "2024-05-26T10:30:00",
    },
    {
        "title": "Event 2",
        "start": "2024-05-26T07:30:00",
        "end": "2024-05-26T10:30:00",
    },
    {
        "title": "Event 3",
        "start": "2024-05-26T10:40:00",
        "end": "2024-05-26T12:30:00",
    }
]
custom_css="""
    .fc-event-past {
        opacity: 0.8;
    }
    .fc-event-time {
        font-style: italic;
    }
    .fc-event-title {
        font-weight: 700;
    }
    .fc-toolbar-title {
        font-size: 2rem;
    }
"""

def response_generator(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)

st.title("Scheduling Assistant")

# Main body
calendar(events=calendar_events, options=calendar_options, custom_css=custom_css)

# Sidebar
with st.sidebar:
  with st.container(height=500):
    # Initialize chat history
    if "messages" not in st.session_state:
      st.session_state.messages = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
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
      st.session_state.messages.append({"role": "user", "content": prompt})

      response = f"Echo:\n{prompt}"
      # Display assistant response in chat message container
      with assistant_placeholder:
        with st.chat_message("assistant"):
          response = st.write_stream(response_generator(response))
        # st.markdown(response)
            
      # Add assistant response to chat history
      st.session_state.messages.append({"role": "assistant", "content": response})