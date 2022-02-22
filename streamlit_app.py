import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
import leafmap.foliumap as leafmap
import requests
import json
from gtts import gTTS

st.set_page_config(layout="wide")
loc_button = Button(label="Get Device Location", max_width=150)
loc_button.js_on_event(
"button_click",
CustomJS(
    code="""
navigator.geolocation.getCurrentPosition(
    (loc) => {
        document.dispatchEvent(new CustomEvent("GET_LOCATION", {detail: {lat: loc.coords.latitude, lon: loc.coords.longitude}}))
    }
)
"""
),
)
result = streamlit_bokeh_events(
    loc_button,
    events="GET_LOCATION",
    key="get_location",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0,
)

if result:
    if "GET_LOCATION" in result:
        loc = result.get("GET_LOCATION")
        lat = loc.get("lat")
        lon = loc.get("lon")
        st.write(f"Lat, Lon: {lat}, {lon}")
        
        url="https://en.wikipedia.org/w/api.php?action=query&\
        format=json&\
        prop=extracts&\
        titles=Main%20Page&\
        generator=geosearch&\
        formatversion=latest&\
        exsentences=3&\
        exintro=1&\
        explaintext=1&\
        ggsradius=5000&\
        ggslimit=2&\
        ggscoord="+str(lat)+"|"+str(lon)
        print (url)
        r = requests.get(url)
        r_json=json.loads(r.text)
        speech=r_json["query"]["pages"][0]["extract"]
        st.json(r_json)

        #Speak

        mp3 = gTTS(speech, lang = 'en', slow = False)
        mp3.save('speech.mp3')
        audio_file = open('speech.mp3', 'rb')
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format='audio/wav')
        
        m = leafmap.Map(center=(lat, lon), zoom=16)
        m.add_basemap("ROADMAP")
        popup = f"lat, lon: {lat}, {lon}"
        m.add_marker(location=(lat, lon), popup=popup)
        m.to_streamlit()
