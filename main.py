import os

import streamlit as st
from groq import Groq
import yagmail
from dotenv import load_dotenv

load_dotenv()

client: Groq = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

st.set_page_config(page_title="Transcript Summarizer", layout="centered")

st.title("📝 Transcript Summarizer & Emailer")

uploaded_file = st.file_uploader("Upload a transcript (.txt)", type=["txt"])

prompt_instruction = st.text_input("Enter custom instruction (e.g., 'Summarize in bullet points for executives')")

transcript_text = ""

if uploaded_file is not None:
    transcript_text = uploaded_file.read().decode("utf-8")
    st.text_area("Transcript Preview", transcript_text, height=200)

if st.button("Generate Summary"):
    if not transcript_text or not prompt_instruction:
        st.warning("Please upload a transcript and enter an instruction.")
    else:
        with st.spinner("Generating summary..."):
            try:
                response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that summarizes transcripts."},
                        {"role": "user", "content": f"Transcript:\n{transcript_text}\n\nInstruction: {prompt_instruction}"}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                summary = response.choices[0].message.content
                st.session_state['generated_summary'] = summary
            except Exception as e:
                st.error(f"Error generating summary: {e}")

if 'generated_summary' in st.session_state:
    st.subheader("✏️ Editable Summary")
    edited_summary = st.text_area("Edit the summary below before sending:", st.session_state['generated_summary'], height=300)
    st.session_state['edited_summary'] = edited_summary

if 'edited_summary' in st.session_state:
    st.subheader("📧 Share Summary via Email")
    recipients = st.text_input("Recipient email address(es) (comma-separated)")
    sender_email = st.text_input("Your email (Gmail only)", value=os.getenv("EMAIL_USER", ""))
    sender_password = st.text_input("Your Gmail App Password", type="password")

    if st.button("Send Email"):
        if not recipients or not sender_email or not sender_password:
            st.warning("Please fill in all email fields.")
        else:
            try:
                yag = yagmail.SMTP(user=sender_email, password=sender_password)
                recipient_list = [email.strip() for email in recipients.split(",")]
                yag.send(
                    to=recipient_list,
                    subject="Summary from Transcript",
                    contents=st.session_state['edited_summary']
                )
                st.success("Email sent successfully!")
            except Exception as e:
                st.error(f"Failed to send email: {e}")
