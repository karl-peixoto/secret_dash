import streamlit as st


def central_metric(label, value):
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-title">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
    """, unsafe_allow_html=True)