import streamlit as st

st.set_page_config(
    page_title="Test App",
    page_icon="✅",
    layout="wide"
)

st.title("✅ Test App - Working")
st.write("If you see this, the app is working correctly.")
st.success("No redirect loops!")

if st.button("Click me"):
    st.balloons()
    st.write("Button clicked!")
