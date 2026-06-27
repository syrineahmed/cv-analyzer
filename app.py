import streamlit as st
import fitz
import requests
from bs4 import BeautifulSoup
from cv_analyzer import analyze_cv, translate_result
from translations import TRANSLATIONS

st.set_page_config(
    page_title="CV Analyzer AI",
    page_icon="🔍",
    layout="wide"
)

def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def extract_pdf(file):
    text = ""
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    for page in pdf:
        text += page.get_text()
    return text

def fetch_url(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.content, "html.parser")
    return soup.get_text(separator=" ", strip=True)[:3000]

load_css()

if "result" not in st.session_state:
    st.session_state.result = None
if "original_result" not in st.session_state:
    st.session_state.original_result = None
if "last_lang" not in st.session_state:
    st.session_state.last_lang = "English"

lang = st.selectbox("🌍 Language / Langue / اللغة", ["English", "Français", "العربية"])
t = TRANSLATIONS[lang]

if st.session_state.last_lang != lang and st.session_state.original_result is not None:
    with st.spinner(t["translating"]):
        if lang == "English":
            st.session_state.result = st.session_state.original_result
        else:
            st.session_state.result = translate_result(st.session_state.original_result, lang)
    st.session_state.last_lang = lang

st.title(t["title"])
st.write(t["subtitle"])
st.divider()

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"#### {t['job_label']}")
    job_upload_tab, job_text_tab, job_link_tab = st.tabs([
        t["upload_tab"], t["type_tab"], t["link_tab"]
    ])
    job = ""
    with job_upload_tab:
        job_file = st.file_uploader("PDF", type=["pdf"], label_visibility="hidden", key="job_pdf")
        if job_file:
            job = extract_pdf(job_file)
            st.success(t["job_upload_success"])
    with job_text_tab:
        job_typed = st.text_area("", height=200, placeholder=t["job_placeholder"], key="job_typed")
        if job_typed:
            job = job_typed
    with job_link_tab:
        job_url = st.text_input("", placeholder=t["url_placeholder"], key="job_url")
        if job_url:
            try:
                job = fetch_url(job_url)
                st.success(t["job_fetch_success"])
                st.text_area(t["url_preview"], value=job[:500] + "...", height=150, disabled=True)
            except Exception as e:
                st.error(f"{t['url_error']}: {e}")

with col2:
    st.markdown(f"#### {t['cv_label']}")
    cv_upload_tab, cv_text_tab = st.tabs([t["upload_tab"], t["type_tab"]])
    cv = ""
    with cv_upload_tab:
        cv_file = st.file_uploader("PDF", type=["pdf"], label_visibility="hidden", key="cv_pdf")
        if cv_file:
            cv = extract_pdf(cv_file)
            st.success(t["upload_success"])
    with cv_text_tab:
        cv_typed = st.text_area("", height=200, placeholder=t["cv_placeholder"], key="cv_typed")
        if cv_typed:
            cv = cv_typed

st.divider()

col1, col2, col3 = st.columns([1,2,1])
with col2:
    analyze_btn = st.button(t["analyze_btn"], use_container_width=True)

if analyze_btn:
    if job and cv:
        with st.spinner(t["analyzing"]):
            english_result = analyze_cv(job, cv, "English")
            st.session_state.original_result = english_result
            if lang == "English":
                st.session_state.result = english_result
            else:
                st.session_state.result = translate_result(english_result, lang)
            st.session_state.last_lang = lang
    else:
        st.warning(t["warning"])

if st.session_state.result is not None:
    result = st.session_state.result
    st.divider()
    st.markdown(f"## {t['results_title']}")

    score = result["score"]
    score_color = "#22c55e" if score >= 7 else "#f97316" if score >= 5 else "#ef4444"

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{t['match_score']}</div>
            <div class="metric-value" style="color:{score_color}">{score}/10</div>
            <div style="font-size:13px;color:#888">{result["score_label"]}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{t['strengths_found']}</div>
            <div class="metric-value" style="color:#22c55e">{len(result["strengths"])}</div>
            <div style="font-size:13px;color:#888">{t['key_advantages']}</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{t['skills_to_add']}</div>
            <div class="metric-value" style="color:#f97316">{len(result["weaknesses"])}</div>
            <div style="font-size:13px;color:#888">{t['missing_items']}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"#### {t['skills_breakdown']}")
    for skill in result["skills_match"]:
        st.markdown(f"**{skill['skill']}** — {skill['percent']}%")
        st.progress(skill["percent"] / 100)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### {t['top_strengths']}")
        for s in result["strengths"]:
            st.markdown(f'<div class="strength-item">{s}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f"#### {t['missing_skills']}")
        for w in result["weaknesses"]:
            st.markdown(f'<div class="weakness-item">{w}</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="advice-box"><strong>{t["key_advice"]}:</strong> {result["advice"]}</div>', unsafe_allow_html=True)