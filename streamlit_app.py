import streamlit as st
from satire_maker import verify_api_key, make_a_satire_article, make_md_version_of_story, convert_md_to_pdf

st.set_page_config(page_title="Satire Maker", page_icon=":book:", layout="wide")

if "container_icon" not in st.session_state:
    st.session_state.container_icon = "running"

if "show_container" not in st.session_state:
    st.session_state.show_container = True

if "article" not in st.session_state:
    st.session_state.article = ""


st.title("Satire Maker")

col1, col2 = st.columns(2)

with col1:
    idea_for_satire = st.text_input("Enter an idea for a satire story:")
    go = st.button("Write it!", key="go")

with col2:
    def api_error():
        st.error("API error. Please try again.")

    if go:
        with st.status("Generating...", expanded=st.session_state.show_container, state=st.session_state.container_icon):
            st.write("Verifying API key...")
            verify_api_key()

            st.write("Contacting the API...")
            story = make_a_satire_article(idea_for_satire)

            st.write("Parsing API response...")
            try:
                story_dict = eval(story)
            except SyntaxError:
                api_error()
                st.session_state.container_icon = "error"
                # st.rerun()
                st.stop()
                

            st.write("Formatting story...")
            markdown = make_md_version_of_story(story_dict)
            

            st.write("Cashing story...")
            with open(markdown, "r") as f:
                st.session_state.article = f.read()

            st.write("Converting story to PDF...")
            convert_md_to_pdf(markdown)

            st.write("Done!")

            st.session_state.show_container_icon = False

            st.session_state.container_icon = "complete"

            # st.rerun()

        # st.download_button(label="Download Story", data=story, file_name="satire_story.md", mime="text/markdown")

st.divider()

if st.session_state.article != "":
    st.markdown(st.session_state.article.replace("\ ", ""))