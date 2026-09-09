import os

from dotenv import load_dotenv

load_dotenv()

import requests
import streamlit as st
import pandas as pd
import plotly.express as px


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000",
)


APP_USERNAME = os.getenv(
    "APP_USERNAME",
    "admin",
)


APP_PASSWORD = os.getenv(
    "APP_PASSWORD",
    "admin123",
)


USER_ID = APP_USERNAME


st.set_page_config(
    page_title="AI Sentiment Analyzer",
    page_icon="📞",
    layout="wide",
)


def login():

    st.title(
        "📞 AI Sentiment Analyzer"
    )

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password",
    )

    if st.button(
        "Login",
        use_container_width=True,
    ):

        if (
            username == APP_USERNAME
            and password == APP_PASSWORD
        ):

            st.session_state[
                "authenticated"
            ] = True

            st.session_state[
                "user_id"
            ] = username

            st.rerun()

        else:

            st.error(
                "Invalid username or password."
            )


if "authenticated" not in st.session_state:

    st.session_state[
        "authenticated"
    ] = False


if not st.session_state["authenticated"]:

    login()

    st.stop()


st.title(
    "📞 AI Conversation Sentiment Analyzer"
)

st.caption(
    "Analyze sentiment, emotions and "
    "contact-center KPIs from a phone-call transcript."
)


if st.sidebar.button("Logout"):

    st.session_state[
        "authenticated"
    ] = False

    st.rerun()


uploaded_file = st.file_uploader(
    "Upload conversation transcript",
    type=["txt"],
)


if uploaded_file is None:

    st.info(
        "Upload a .txt transcript to begin."
    )

    st.stop()


transcript = uploaded_file.read().decode(
    "utf-8",
    errors="ignore",
)


with st.expander("View Transcript"):

    st.text_area(
        "Transcript",
        transcript,
        height=300,
    )


if st.button(
    "🔍 Analyze Conversation",
    type="primary",
    use_container_width=True,
):

    with st.spinner(
        "Analyzing conversation..."
    ):

        try:

            response = requests.post(

                f"{BACKEND_URL}/analyze",

                json={
                    "transcript": transcript,
                    "user_id": st.session_state[
                        "user_id"
                    ],
                },

                timeout=120,
            )

            if response.status_code == 429:

                st.warning(
                    "Rate limit reached. "
                    "Please wait and try again."
                )

                st.stop()


            if response.status_code != 200:

                st.error(
                    response.text
                )

                st.stop()


            st.session_state[
                "analysis"
            ] = response.json()


        except requests.exceptions.Timeout:

            st.error(
                "The AI service took too long "
                "to respond. Please try again."
            )

            st.stop()


        except requests.exceptions.RequestException as exc:

            st.error(
                f"Backend connection failed: {exc}"
            )

            st.stop()


if "analysis" not in st.session_state:

    st.stop()


data = st.session_state[
    "analysis"
]

kpis = data["kpis"]


st.divider()

st.header(
    "🎯 Overall Sentiment"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Sentiment",
        data["overall_sentiment"],
    )


with col2:

    st.metric(
        "Confidence",
        f"{data['overall_confidence'] * 100:.1f}%",
    )


with col3:

    st.metric(
        "Sentiment Score",
        f"{kpis['customer_sentiment_score']:.1f}/100",
    )


st.info(
    data["summary"]
)


st.header(
    "📊 Sentiment Breakdown"
)


sentiment_df = pd.DataFrame(
    {
        "Sentiment": [
            "Positive",
            "Negative",
            "Neutral",
        ],

        "Percentage": [
            kpis["positive_percentage"],
            kpis["negative_percentage"],
            kpis["neutral_percentage"],
        ],
    }
)


fig = px.pie(
    sentiment_df,
    names="Sentiment",
    values="Percentage",
    hole=0.4,
)


st.plotly_chart(
    fig,
    use_container_width=True,
)


st.header(
    "📈 Call KPIs"
)


cols = st.columns(4)


with cols[0]:

    st.metric(
        "Customer Satisfaction",
        f"{kpis['customer_satisfaction_indicator']:.1f}%",
    )


with cols[1]:

    st.metric(
        "Resolution",
        f"{kpis['resolution_indicator']:.1f}%",
    )


with cols[2]:

    st.metric(
        "Escalation Risk",
        f"{kpis['escalation_risk']:.1f}%",
    )


with cols[3]:

    st.metric(
        "Frustration",
        f"{kpis['frustration_score']:.1f}%",
    )


cols = st.columns(4)


with cols[0]:

    st.metric(
        "Agent Empathy",
        f"{kpis['empathy_score']:.1f}%",
    )


with cols[1]:

    st.metric(
        "Agent Helpfulness",
        f"{kpis['agent_helpfulness_score']:.1f}%",
    )


with cols[2]:

    st.metric(
        "Issue Resolved",
        "Yes"
        if kpis["issue_resolved"]
        else "No",
    )


with cols[3]:

    st.metric(
        "Escalation Required",
        "Yes"
        if kpis["escalation_required"]
        else "No",
    )


st.header(
    "📝 Sentence-Level Sentiment"
)


sentence_df = pd.DataFrame(
    data["sentence_sentiments"]
)


sentence_df["confidence"] = (
    sentence_df["confidence"] * 100
).round(1)


st.dataframe(
    sentence_df,
    use_container_width=True,
    hide_index=True,
)


st.header(
    "🧠 Emotion Analysis"
)


emotion_df = pd.DataFrame(
    data["emotions"]
)


if not emotion_df.empty:

    emotion_df["confidence"] = (
        emotion_df["confidence"] * 100
    ).round(1)


    fig = px.bar(
        emotion_df,
        x="emotion",
        y="confidence",
        text="confidence",
    )


    st.plotly_chart(
        fig,
        use_container_width=True,
    )


st.header(
    "💡 Conversation Insights"
)


col1, col2 = st.columns(2)


with col1:

    st.subheader(
        "Key Issues"
    )

    for item in data["key_issues"]:

        st.write(
            f"• {item}"
        )


    st.subheader(
        "Positive Points"
    )

    for item in data["positive_points"]:

        st.write(
            f"• {item}"
        )


with col2:

    st.subheader(
        "Negative Points"
    )

    for item in data["negative_points"]:

        st.write(
            f"• {item}"
        )


    st.subheader(
        "Recommendations"
    )

    for item in data["recommendations"]:

        st.write(
            f"• {item}"
        )