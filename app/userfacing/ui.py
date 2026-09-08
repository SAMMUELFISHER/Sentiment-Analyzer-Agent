import os

import requests
import streamlit as st
import pandas as pd
import plotly.express as px


BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000"
)


st.set_page_config(
    page_title="AI Sentiment Analyzer",
    page_icon="📞",
    layout="wide"
)


# ---------------------------------------------------------
# Authentication
# ---------------------------------------------------------

def login():

    st.title("📞 AI Sentiment Analyzer")

    st.subheader("Login")

    username = st.text_input(
        "Username"
    )

    password = st.text_input(
        "Password",
        type="password"
    )

    if st.button(
        "Login",
        use_container_width=True
    ):

        valid_username = os.getenv(
            "APP_USERNAME",
            "admin"
        )

        valid_password = os.getenv(
            "APP_PASSWORD",
            "admin123"
        )

        if (
            username == valid_username
            and password == valid_password
        ):

            st.session_state["authenticated"] = True

            st.rerun()

        else:

            st.error(
                "Invalid username or password."
            )


if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False


if not st.session_state["authenticated"]:

    login()

    st.stop()


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("📞 AI Conversation Sentiment Analyzer")

st.caption(
    "Upload a phone-call transcript and generate AI-powered "
    "sentiment, emotions, conversation insights and KPIs."
)


if st.sidebar.button("Logout"):

    st.session_state["authenticated"] = False

    st.rerun()


# ---------------------------------------------------------
# File Upload
# ---------------------------------------------------------

uploaded_file = st.file_uploader(
    "Upload conversation transcript",
    type=["txt"]
)


if uploaded_file is None:

    st.info(
        "Upload a .txt conversation transcript to begin."
    )

    st.stop()


transcript = uploaded_file.read().decode(
    "utf-8",
    errors="ignore"
)


with st.expander("View transcript"):

    st.text_area(
        "Conversation",
        transcript,
        height=300
    )


# ---------------------------------------------------------
# Analyze
# ---------------------------------------------------------

if st.button(
    "🔍 Analyze Conversation",
    type="primary",
    use_container_width=True
):

    with st.spinner(
        "Analyzing conversation..."
    ):

        try:

            response = requests.post(
                f"{BACKEND_URL}/analyze",
                json={
                    "transcript": transcript
                },
                timeout=180
            )

            response.raise_for_status()

            st.session_state["analysis"] = response.json()

        except requests.RequestException as exc:

            st.error(
                f"Backend error: {exc}"
            )

            st.stop()


if "analysis" not in st.session_state:

    st.stop()


data = st.session_state["analysis"]


# ---------------------------------------------------------
# Overall Sentiment
# ---------------------------------------------------------

st.divider()

st.header("🎯 Overall Sentiment")


sentiment = data["overall_sentiment"]
confidence = data["overall_confidence"]


if sentiment == "Positive":

    sentiment_icon = "😊"

elif sentiment == "Negative":

    sentiment_icon = "😠"

else:

    sentiment_icon = "😐"


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Overall Sentiment",
        f"{sentiment_icon} {sentiment}"
    )


with col2:

    st.metric(
        "Confidence",
        f"{confidence * 100:.1f}%"
    )


with col3:

    st.metric(
        "Customer Sentiment Score",
        f"{data['kpis']['customer_sentiment_score']:.1f}/100"
    )


st.info(
    data["summary"]
)


# ---------------------------------------------------------
# Sentiment Breakdown
# ---------------------------------------------------------

st.header("📊 Sentiment Breakdown")


kpis = data["kpis"]


sentiment_df = pd.DataFrame(
    {
        "Sentiment": [
            "Positive",
            "Negative",
            "Neutral"
        ],
        "Percentage": [
            kpis["positive_percentage"],
            kpis["negative_percentage"],
            kpis["neutral_percentage"]
        ]
    }
)


fig = px.pie(
    sentiment_df,
    names="Sentiment",
    values="Percentage",
    hole=0.45
)


fig.update_layout(
    height=400
)


st.plotly_chart(
    fig,
    use_container_width=True
)


# ---------------------------------------------------------
# KPI Dashboard
# ---------------------------------------------------------

st.header("📈 Call KPIs")


kpi_columns = st.columns(4)


with kpi_columns[0]:

    st.metric(
        "Customer Satisfaction",
        f"{kpis['customer_satisfaction_indicator']:.1f}%"
    )


with kpi_columns[1]:

    st.metric(
        "Resolution",
        f"{kpis['resolution_indicator']:.1f}%"
    )


with kpi_columns[2]:

    st.metric(
        "Escalation Risk",
        f"{kpis['escalation_risk']:.1f}%"
    )


with kpi_columns[3]:

    st.metric(
        "Frustration",
        f"{kpis['frustration_score']:.1f}%"
    )


kpi_columns_2 = st.columns(4)


with kpi_columns_2[0]:

    st.metric(
        "Agent Empathy",
        f"{kpis['empathy_score']:.1f}%"
    )


with kpi_columns_2[1]:

    st.metric(
        "Agent Helpfulness",
        f"{kpis['agent_helpfulness_score']:.1f}%"
    )


with kpi_columns_2[2]:

    st.metric(
        "Issue Resolved",
        "Yes" if kpis["issue_resolved"] else "No"
    )


with kpi_columns_2[3]:

    st.metric(
        "Escalation Required",
        "Yes" if kpis["escalation_required"] else "No"
    )


# ---------------------------------------------------------
# Sentence-level sentiment
# ---------------------------------------------------------

st.header("📝 Sentence-Level Sentiment")


sentence_data = data["sentence_sentiments"]


sentence_df = pd.DataFrame(sentence_data)


sentence_df["confidence"] = (
    sentence_df["confidence"] * 100
).round(1)


sentence_df = sentence_df.rename(
    columns={
        "sentence": "Sentence",
        "sentiment": "Sentiment",
        "confidence": "Confidence %",
        "reason": "Reason"
    }
)


st.dataframe(
    sentence_df,
    use_container_width=True,
    hide_index=True
)


# ---------------------------------------------------------
# Emotion Detection
# ---------------------------------------------------------

st.header("🧠 Emotion Analysis")


emotion_data = data["emotions"]


emotion_df = pd.DataFrame(
    emotion_data
)


if not emotion_df.empty:

    emotion_df["confidence"] = (
        emotion_df["confidence"] * 100
    ).round(1)

    emotion_df = emotion_df.rename(
        columns={
            "emotion": "Emotion",
            "confidence": "Confidence %"
        }
    )

    fig = px.bar(
        emotion_df,
        x="Emotion",
        y="Confidence %",
        text="Confidence %"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ---------------------------------------------------------
# Conversation Insights
# ---------------------------------------------------------

st.header("💡 Conversation Insights")


col1, col2 = st.columns(2)


with col1:

    st.subheader("Key Issues")

    for issue in data["key_issues"]:

        st.write(
            f"• {issue}"
        )


    st.subheader("Positive Points")

    for point in data["positive_points"]:

        st.write(
            f"• {point}"
        )


with col2:

    st.subheader("Negative Points")

    for point in data["negative_points"]:

        st.write(
            f"• {point}"
        )


    st.subheader("Recommendations")

    for recommendation in data["recommendations"]:

        st.write(
            f"• {recommendation}"
        )


# ---------------------------------------------------------
# Export
# ---------------------------------------------------------

st.header("⬇️ Export Analysis")


export_df = sentence_df.to_csv(
    index=False
)


st.download_button(
    label="Download Sentence Analysis CSV",
    data=export_df,
    file_name="sentence_sentiment_analysis.csv",
    mime="text/csv",
    use_container_width=True
)