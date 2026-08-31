import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import base64

# Import our custom modules
from modules import auth, users, competencies, courses, assessments, recommendations, knowledge, analytics

# Set page configuration
st.set_page_config(
    page_title="CapacityConnect | Competency-Driven LMS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern enterprise look (Linear/Stripe inspired)
st.markdown("""
<style>
    /* Force dark text on light backgrounds - override Streamlit defaults */
    .stApp, .stApp * {
        color: #0F172A !important;
    }

    /* Main Layout - force background */
    .stApp {
        background-color: #F8FAFC !important;
    }

    /* Main content area */
    .main .block-container {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
    }

    /* Typography */
    html, body, [class*="css"], .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6, label {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #0F172A !important;
    }

    /* Input fields - ensure readable text */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.2s !important;
    }

    .stButton > button:hover {
        background-color: #2563EB !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }

    .stButton > button[kind="secondary"] {
        background-color: #F1F5F9 !important;
        color: #334155 !important;
        border: 1px solid #E2E8F0 !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background-color: #E2E8F0 !important;
        color: #0F172A !important;
    }

    /* Cards/Containers */
    .stContainer, div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
    }

    /* Clean Cards */
    .cc-card {
        background-color: #FFFFFF !important;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        color: #0F172A !important;
    }

    .cc-kpi-val {
        font-size: 28px;
        font-weight: 700;
        color: #0F172A !important;
        margin: 4px 0;
    }

    .cc-kpi-change-pos {
        color: #10B981 !important;
        font-size: 14px;
        font-weight: 600;
    }

    .cc-kpi-change-neg {
        color: #EF4444 !important;
        font-size: 14px;
        font-weight: 600;
    }

    /* Priority Badges */
    .cc-badge {
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        display: inline-block;
    }
    .cc-badge-critical { background-color: #FEE2E2 !important; color: #991B1B !important; }
    .cc-badge-medium { background-color: #FEF3C7 !important; color: #92400E !important; }
    .cc-badge-low { background-color: #FEF9C3 !important; color: #854D0E !important; }
    .cc-badge-nogap { background-color: #D1FAE5 !important; color: #065F46 !important; }
    .cc-badge-progress { background-color: #DBEAFE !important; color: #1E40AF !important; }
    .cc-badge-draft { background-color: #F1F5F9 !important; color: #475569 !important; }

    /* Sidebar - force dark text */
    .stSidebar, .stSidebar * {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
    }

    .stSidebar .stButton > button {
        background-color: #F1F5F9 !important;
        color: #334155 !important;
        border: 1px solid #E2E8F0 !important;
    }

    .stSidebar .stButton > button:hover {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
    }

    .stSidebar .stButton > button[kind="primary"] {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
    }

    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #0F172A !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #64748B !important;
        font-size: 12px !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* Progress bars */
    .stProgress > div > div > div {
        background-color: #3B82F6 !important;
    }

    /* Radio/Checkbox labels */
    .stRadio > label, .stCheckbox > label {
        color: #0F172A !important;
    }

    .stRadio > div[role="radiogroup"] > label {
        background-color: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        margin: 8px 0 !important;
        color: #0F172A !important;
    }

    .stRadio > div[role="radiogroup"] > label:hover {
        background-color: #DBEAFE !important;
        border-color: #3B82F6 !important;
    }

    .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #DBEAFE !important;
        border-color: #3B82F6 !important;
    }

    /* Dataframe/Table */
    .stDataFrame, .stTable {
        color: #0F172A !important;
    }

    .stDataFrame [data-testid="stDataFrameResizable"] {
        background-color: #FFFFFF !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #F1F5F9 !important;
        border-radius: 8px !important;
        padding: 4px !important;
    }

    .stTabs [data-baseweb="tab"] {
        color: #475569 !important;
        font-weight: 500 !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #1E40AF !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1) !important;
    }

    /* Selectbox dropdown */
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #CBD5E1 !important;
    }

    /* Form submit button */
    .stFormSubmitButton > button {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #F8FAFC !important;
        color: #0F172A !important;
        font-weight: 600 !important;
    }

    .streamlit-expanderContent {
        background-color: #FFFFFF !important;
        color: #0F172A !important;
        border: 1px solid #E2E8F0 !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
    }

    /* File uploader */
    .stFileUploader > div {
        background-color: #F8FAFC !important;
        border: 2px dashed #CBD5E1 !important;
        border-radius: 12px !important;
    }

    /* Toast/Notifications */
    .stToast {
        background-color: #1E293B !important;
        color: #FFFFFF !important;
    }

    /* Learning Path Connection Nodes */
    .lp-node {
        padding: 16px;
        background-color: #FFFFFF !important;
        border-radius: 8px;
        border: 1px solid #E2E8F0;
        text-align: center;
        margin: 10px 0;
        color: #0F172A !important;
    }
    .lp-arrow {
        text-align: center;
        font-size: 20px;
        color: #64748B !important;
        margin: 5px 0;
    }

    /* Force all markdown text to be dark */
    .stMarkdown, .stMarkdown * {
        color: #0F172A !important;
    }

    /* Override any white text on white backgrounds */
    .element-container, .element-container * {
        color: #0F172A !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to render CSS cards in markdown
def draw_card(title, value, change="", target_goal=""):
    change_span = ""
    if change:
        if change.startswith("+") or "improvement" in change.lower():
            change_span = f'<span class="cc-kpi-change-pos">{change}</span>'
        else:
            change_span = f'<span class="cc-kpi-change-neg">{change}</span>'

    header_html = f"""
    <div class="cc-card">
        <div style="font-size: 12px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.05em;">{title}</div>
        <div class="cc-kpi-val">{value}</div>
        <div>{change_span} <span style="font-size: 12px; color: #64748B;">{target_goal}</span></div>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

# Helper function for rendering horizontal progress compare bars
def draw_competency_bar(name, current_val, required_val, gap, status):
    badge_class = f"cc-badge-{status.lower().replace(' ', '')}"
    status_badge = f'<span class="cc-badge {badge_class}">{status}</span>'

    # Generate visual scale
    bar_html = '<div style="display: flex; gap: 4px; margin-top: 8px; margin-bottom: 20px;">'
    for i in range(1, 6):
        if i <= current_val:
            # filled segment up to current
            color = "#3B82F6" # blue
            if i > required_val:
                color = "#10B981" # green (met/exceeded req)
            elif status == "Critical":
                color = "#EF4444" # red (critical gap segment)
            elif status == "Medium":
                color = "#F59E0B" # amber
        else:
            color = "#E2E8F0" # empty

        # Draw target indicators
        border_style = "border: 2px solid #0F172A;" if i == required_val else ""
        bar_html += f'<div style="flex: 1; height: 12px; background-color: {color}; border-radius: 2px; {border_style}" title="Level {i}"></div>'
    bar_html += '</div>'

    label_html = f"""
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 600; color: #1E293B;">{name}</span>
        <div style="display: flex; align-items: center; gap: 12px;">
            <span style="font-size: 13px; color: #64748B;">Current: <b>{current_val}/5</b> &bull; Required: <b>{required_val}/5</b></span>
            {status_badge}
        </div>
    </div>
    {bar_html}
    """
    st.markdown(label_html, unsafe_allow_html=True)

# Initialization of Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Dashboard"
if 'active_course_id' not in st.session_state:
    st.session_state.active_course_id = None
if 'active_assessment_id' not in st.session_state:
    st.session_state.active_assessment_id = None
if 'quiz_step' not in st.session_state:
    st.session_state.quiz_step = 0
if 'quiz_answers' not in st.session_state:
    st.session_state.quiz_answers = []

# ----------------- LOGIN PAGE -----------------
def render_login_page():
    left_col, right_col = st.columns([1.2, 1], gap="large")

    with left_col:
        st.write("")
        st.write("")
        st.write("")
        st.title("🎓 CapacityConnect")
        st.subheader("Competency-driven organizational learning.")
        st.markdown("""
        **Identify skill gaps. Personalize learning. Measure improvement. Build organizational capacity.**

        CapacityConnect is an AI-powered organizational capacity-building and learning portal designed to focus on what you need to learn. Unlike a traditional LMS, we connect employee profiles with role definitions, identify competency gaps, and dynamically suggest learning paths to drive measurable development.

        ### The Competency-Driven Learning Loop:
        1. **Assess** current capabilities via targeted modules.
        2. **Identify** gaps against role specific required levels.
        3. **Recommend** bite-sized courses aimed at closing gaps.
        4. **Learn** inline with interactive videos, readouts, and docs.
        5. **Evaluate** progress with auto-graded quizzes/assessments.
        6. **Improve** and update individual competency profiles live.
        """)

    with right_col:
        st.write("")
        st.write("")
        st.write("")
        with st.container(border=True):
            st.markdown("<h3 style='margin-top:0;'>Sign In</h3>", unsafe_allow_html=True)
            email = st.text_input("Work Email Address", placeholder="name@company.com")
            password = st.text_input("Password", type="password")
            remember = st.checkbox("Remember me on this device")

            if st.button("Sign In", use_container_width=True, type="primary"):
                user = auth.authenticate_user(email, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.toast(f"Welcome back, {user['name']}!")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

            st.divider()
            st.markdown("<p style='text-align: center; color: #64748B; font-size: 13px;'>Demo Accounts</p>", unsafe_allow_html=True)
            demo_cols = st.columns(2)
            with demo_cols[0]:
                if st.button("🗝️ Employee Demo", use_container_width=True):
                    # Login as Alex Johnson
                    user = auth.authenticate_user('alex.johnson@company.com', 'demo123')
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.toast(f"Logged in as demo employee: {user['name']}")
                    st.rerun()
            with demo_cols[1]:
                if st.button("🛡️ Admin Demo", use_container_width=True):
                    # Login as Admin
                    user = auth.authenticate_user('admin@company.com', 'admin123')
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.toast(f"Logged in as Administrator")
                    st.rerun()

# ----------------- SIDEBAR NAVIGATION -----------------
def render_sidebar():
    user = st.session_state.user
    st.sidebar.markdown("<h2 style='text-align: center; margin-bottom: 0px;'>🎓 CapacityConnect</h2>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p style='text-align: center; color: #64748B; font-size: 13px; font-style: italic; margin-top:-5px;'>Competency-driven learning</p>", unsafe_allow_html=True)

    st.sidebar.divider()

    # Employee Navigation Options
    st.sidebar.markdown("**MAIN**")

    pages = [
        {"name": "Dashboard", "icon": "📊"},
        {"name": "My Competencies", "icon": "🎯"},
        {"name": "Skill Gaps", "icon": "⚡"},
        {"name": "Learning Path", "icon": "🛤️"},
        {"name": "Courses", "icon": "📚"},
        {"name": "Knowledge Hub", "icon": "💡"}
    ]

    for page in pages:
        is_active = st.session_state.current_page == page["name"]
        style = "primary" if is_active else "secondary"
        if st.sidebar.button(f"{page['icon']} {page['name']}", use_container_width=True, type=style):
            st.session_state.current_page = page["name"]
            st.session_state.active_course_id = None
            st.session_state.active_assessment_id = None
            st.rerun()

    # Administrator Nav options
    if user['is_admin']:
        st.sidebar.write("")
        st.sidebar.markdown("**ADMINISTRATION**")
        admin_pages = [
            {"name": "Admin Overview", "icon": "🏢"},
            {"name": "Competencies Mgnt", "icon": "🧬"},
            {"name": "Course Builder", "icon": "🏗️"},
            {"name": "Role Competencies", "icon": "🗺️"},
            {"name": "Knowledge Review", "icon": "📥"}
        ]
        for page in admin_pages:
            is_active = st.session_state.current_page == page["name"]
            style = "primary" if is_active else "secondary"
            if st.sidebar.button(f"{page['icon']} {page['name']}", use_container_width=True, type=style):
                st.session_state.current_page = page["name"]
                st.session_state.active_course_id = None
                st.session_state.active_assessment_id = None
                st.rerun()

    st.sidebar.write("")
    st.sidebar.write("")
    st.sidebar.write("")
    st.sidebar.divider()

    # User profile/Logout
    with st.sidebar.container():
        st.markdown(f"**👤 {user['name']}**")
        st.markdown(f"<span style='font-size:12px; color: #64748B;'>{user['role']}</span>", unsafe_allow_html=True)
        st.markdown(f"<span style='font-size:11px; color: #94A3B8;'>{user['department']}</span>", unsafe_allow_html=True)
        if st.button("Log Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.current_page = "Dashboard"
            st.rerun()

# ----------------- EMPLOYEE DASHBOARD -----------------
def render_employee_dashboard():
    user = st.session_state.user

    # Check if there is a running course or assessment redirect
    if st.session_state.active_assessment_id:
        render_assessment_page()
        return
    if st.session_state.active_course_id:
        render_course_details()
        return

    profile = users.get_user_profile(user['user_id'])

    st.markdown(f"<h1>Good morning, {user['name']}</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748B; font-size:16px; margin-top:-15px;'>Here's your competency and learning overview.</p>", unsafe_allow_html=True)

    # KPI Row
    kpi_cols = st.columns(4)
    with kpi_cols[0]:
        # Overall Competency with target
        draw_card("Overall Competency", f"{profile['overall_competency_pct']}%", "+8% this month", "progress")
    with kpi_cols[1]:
        # Count critical gaps
        gaps = competencies.get_skill_gaps(user['user_id'])
        critical_count = sum(1 for g in gaps if g['status'] == 'Critical')
        draw_card("Critical Skill Gaps", str(critical_count), "Requires action" if critical_count > 0 else "All cleared", "")
    with kpi_cols[2]:
        # Active courses
        draw_card("Active Courses", str(profile['active_courses']), "", "In progress")
    with kpi_cols[3]:
        # Completed courses
        draw_card("Completed Courses", str(profile['completed_courses']), "", "Total finished")

    col1, col2 = st.columns([1.2, 1], gap="large")

    with col1:
        st.markdown("### Your Competency Overview")
        st.markdown("<p style='color: #64748B; font-size:13px;'>Comparison between your current level and target level for designation requirements.</p>", unsafe_allow_html=True)

        # Render horizontal comparison progress bars
        user_comps = competencies.get_skill_gaps(user['user_id'])
        for comp in user_comps[:6]:
            draw_competency_bar(
                comp['name'],
                comp['current_level'],
                comp['required_level'],
                comp['gap'],
                comp['status']
            )

        if st.button("View all competencies", type="secondary"):
            st.session_state.current_page = "My Competencies"
            st.rerun()

    with col2:
        st.markdown("### Priority Recommendations")
        st.markdown("<p style='color: #64748B; font-size:13px;'>Courses suggested based on your specific competency gaps.</p>", unsafe_allow_html=True)

        recs = recommendations.get_recommendations_for_user(user['user_id'], max_recommendations=3)
        if not recs:
            st.info("🎉 Excellent work! You have closed all required competency gaps for your role.")
        else:
            for rec in recs:
                with st.container(border=True):
                    # Title banner
                    st.markdown(f"#### {rec['title']}")
                    st.markdown(f"<span style='color: #3B82F6; font-size: 13px; font-weight:600;'>💡 {rec['reason']}</span>", unsafe_allow_html=True)
                    st.write(rec['description'][:120] + "...")

                    st.markdown(f"""
                    <span style='font-size:12px; color:#64748B;'>⏱️ Duration: <b>{rec['duration']}</b> &nbsp;|&nbsp; 🏷️ Difficulty: <b>{rec['difficulty']}</b></span>
                    """, unsafe_allow_html=True)

                    st.write("")
                    if st.button("Start Learning", key=f"start_rec_{rec['course_id']}", type="primary"):
                        # Enroll of the user in course
                        users.enroll_in_course(user['user_id'], rec['course_id'])
                        st.session_state.active_course_id = rec['course_id']
                        st.rerun()

# ----------------- MY COMPETENCIES PAGE -----------------
def render_my_competencies_page():
    user = st.session_state.user
    st.title("🎯 My Competency Map")
    st.markdown("Detailed breakdown of your capabilities, assessments, and targeted standards.")

    user_comps = competencies.get_skill_gaps(user['user_id'])

    # Format to Pandas DataFrame for rendering search/sort
    comp_list = []
    for comp in user_comps:
        comp_list.append({
            "Competency": comp['name'],
            "Current Level": f"{comp['current_level']} - {competencies.get_competency_level_label(comp['current_level'])}",
            "Required Level": f"{comp['required_level']} - {competencies.get_competency_level_label(comp['required_level'])}",
            "Gap Value": comp['gap'],
            "Status": comp['status']
        })
    df = pd.DataFrame(comp_list)

    col1, col2 = st.columns([1.2, 1], gap="large")

    with col1:
        st.subheader("Current Performance Matrix")

        # Display nicely styled table with st.dataframe or interactive elements
        st.dataframe(
            df,
            column_config={
                "Competency": st.column_config.TextColumn("Competency Domain", width="medium"),
                "Current Level": st.column_config.TextColumn("My Level"),
                "Required Level": st.column_config.TextColumn("Role Requirement"),
                "Gap Value": st.column_config.NumberColumn("Gap (Levels)"),
                "Status": st.column_config.TextColumn("Action Badge")
            },
            hide_index=True,
            use_container_width=True
        )

        # Assessment history
        st.subheader("Competency Assessment History")
        results_hist = assessments.get_user_results(user['user_id'])
        if not results_hist:
            st.info("You haven't completed any assessments yet.")
        else:
            hist_list = []
            for r in results_hist:
                status = "Passed ✅" if r['score'] >= r['passing_score'] else "Failed ❌"
                hist_list.append({
                    "Date": r['date'][:10],
                    "Assessment Title": r['assessment_title'],
                    "Score Obtained": f"{r['score']}%",
                    "Required Passing": f"{r['passing_score']}%",
                    "Status": status
                })
            st.table(pd.DataFrame(hist_list))

    with col2:
        st.subheader("Competency Radar Visual")

        # Generate radar chart for current vs required
        comp_names = [c['name'] for c in user_comps]
        curr_vals = [c['current_level'] for c in user_comps]
        req_vals = [c['required_level'] for c in user_comps]

        if comp_names:
            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=curr_vals,
                theta=comp_names,
                fill='toself',
                name='My Level',
                line_color='#2563EB',
                fillcolor='rgba(37, 99, 235, 0.2)'
            ))

            fig.add_trace(go.Scatterpolar(
                r=req_vals,
                theta=comp_names,
                fill='toself',
                name='Required Level',
                line_color='#EF4444',
                fillcolor='rgba(239, 68, 68, 0.1)'
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 5]
                    )
                ),
                showlegend=True,
                margin=dict(l=40, r=40, t=20, b=20)
            )

            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No mapped role competencies found.")

# ----------------- SKILL GAPS SECTION -----------------
def render_skill_gaps_page():
    user = st.session_state.user
    st.title("⚡ Skill Gap Analysis")
    st.markdown("High priority items highlighting where your current competency levels fall below target.")

    gaps = competencies.get_skill_gaps(user['user_id'])

    # Gaps count summary cards
    c_cols = st.columns(3)
    critical_count = sum(1 for g in gaps if g['status'] == 'Critical')
    medium_count = sum(1 for g in gaps if g['status'] == 'Medium')
    low_count = sum(1 for g in gaps if g['status'] == 'Low')

    with c_cols[0]:
        st.metric("🔴 Critical Gaps", critical_count, help="Gap of 2+ levels")
    with c_cols[1]:
        st.metric("🟡 Medium Gaps", medium_count, help="Gap of 2 levels")
    with c_cols[2]:
        st.metric("🟢 Low/No Gaps", low_count, help="Gap of 1 or 0 levels")

    st.subheader("Target Action Plan")

    for gap in gaps:
        if gap['gap'] <= 0:
            continue

        with st.container(border=True):
            cols = st.columns([0.15, 0.55, 0.3])

            with cols[0]:
                if gap['status'] == 'Critical':
                    st.error("🚨 Critical")
                elif gap['status'] == 'Medium':
                    st.warning("⚠️ Medium")
                else:
                    st.info("💡 Low")

            with cols[1]:
                st.write(f"### {gap['name']}")
                st.write(gap['description'])
                st.write(f"**Current Label:** {competencies.get_competency_level_label(gap['current_level'])} &bull; **Required Target:** {competencies.get_competency_level_label(gap['required_level'])}")

            with cols[2]:
                # Connect to recommended course directly
                st.write("")
                st.write(f"**Gap Distance:** {gap['gap']} levels")
                rec_courses = courses.get_courses_for_competency(gap['competency_id'])
                if rec_courses:
                    target_course = rec_courses[0]
                    if st.button("Start Recommended Course", key=f"gap_course_{gap['competency_id']}", type="primary", use_container_width=True):
                        users.enroll_in_course(user['user_id'], target_course['course_id'])
                        st.session_state.active_course_id = target_course['course_id']
                        st.rerun()
                else:
                    st.info("No direct training modules mapped yet.")

# ----------------- LEARNING PATH SECTION -----------------
def render_learning_path_page():
    user = st.session_state.user
    st.title("🛤️ Personalized Learning Path")
    st.markdown("Your custom sequence of learning activities tailored to close your role gaps systematically.")

    path = recommendations.get_learning_path_for_user(user['user_id'])

    # If learning path is empty, generate it from existing gaps
    if not path:
        if st.button("Auto-Generate Learning Path from Skill Gaps", type="primary"):
            path = recommendations.generate_learning_path_from_gaps(user['user_id'])
            st.success("Successfully generated your customized learning path!")
            st.rerun()
        else:
            st.info("You don't have a learning path configured yet. Click above to auto-build one.")
            return

    # Visual Connection Blocks
    st.subheader("Your Roadmap Progression")

    # Display overall progress
    total_steps = len(path)
    completed_steps = sum(1 for c in path if c['is_completed'])
    path_progress = round((completed_steps / total_steps) * 100) if total_steps > 0 else 0
    st.progress(path_progress / 100)
    st.write(f"**Learning Path Progress:** {completed_steps} of {total_steps} courses completed ({path_progress}%)")

    st.write("")

    for i, step in enumerate(path):
        is_completed = step['is_completed']
        status_label = "✅ Completed" if is_completed else ("🔵 Locked/Upcoming" if i > completed_steps else "🟡 Active Next Module")
        border_color = "#10B981" if is_completed else ("#3B82F6" if i == completed_steps else "#CBD5E1")

        with st.container(border=True):
            st.markdown(f"""
            <div style="border-left: 5px solid {border_color}; padding-left: 15px;">
                <span class="cc-badge" style="background-color: {border_color}33; color: {border_color[:7]}; font-size:12px;">Step {step['sequence_order']} - {status_label}</span>
                <h3 style="margin: 5px 0;">{step['title']}</h3>
                <p style="color:#64748B; margin-bottom:5px;">{step['description']}</p>
                <div style="font-size:12px; color: #64748B;">
                    ⏱️ {step['duration']} &nbsp;|&nbsp; 🏷️ {step['difficulty']} &nbsp;|&nbsp; 👨🏫 Instructor: {step['instructor']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.write("")
            if not is_completed and i == completed_steps:
                if st.button("Open Active Module", key=f"lp_course_{step['course_id']}", type="primary"):
                    users.enroll_in_course(user['user_id'], step['course_id'])
                    st.session_state.active_course_id = step['course_id']
                    st.rerun()

# ----------------- COURSE LIST SECTION -----------------
def render_courses_page():
    user = st.session_state.user

    # Check details redirect
    if st.session_state.active_course_id:
        render_course_details()
        return

    st.title("📚 Mapped Courses Catalog")
    st.markdown("All training courses designed to target organizational competencies.")

    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Search catalog...", placeholder="Search by title, instructor, or competency...")
    with col2:
        diff_filter = st.selectbox("Difficulty Filter", ["All", "Beginner", "Intermediate", "Advanced"])

    # Get all published courses
    all_courses = courses.get_published_courses()

    # Get user enrollment data
    user_enrolled = {c['course_id']: c for c in users.get_user_courses(user['user_id'])}

    # Format and Filter
    filtered_courses = []
    for c in all_courses:
        course_details = courses.get_course_by_id(c['course_id'])
        comp_names = [comp['name'] for comp in course_details['competencies']]

        # Search match
        if search_query:
            query = search_query.lower()
            match = (query in c['title'].lower() or
                     query in c['description'].lower() or
                     query in c['instructor'].lower() or
                     any(query in cmp.lower() for cmp in comp_names))
            if not match:
                continue

        # Difficulty filter match
        if diff_filter != "All" and c['difficulty'] != diff_filter:
            continue

        filtered_courses.append((c, course_details))

    if not filtered_courses:
        st.info("No courses match your query filters.")
        return

    # Render course grid cards
    grid_cols = st.columns(2)
    for idx, (c, details) in enumerate(filtered_courses):
        with grid_cols[idx % 2]:
            with st.container(border=True):
                st.write(f"### {c['title']}")
                st.write(f"👨🏫 **Instructor:** {c['instructor']}")
                st.write(c['description'][:140] + "...")

                # Associated competencies
                st.write("**Closes Skill Gaps in:**")
                comp_badges = " ".join([f'<span class="cc-badge cc-badge-progress">{comp["name"]} (Lvl {comp["target_level"]})</span>' for comp in details['competencies']])
                st.markdown(comp_badges, unsafe_allow_html=True)
                st.write("")

                st.markdown(f"⏱️ **Duration:** {c['duration']} &nbsp;|&nbsp; 🏷️ **Difficulty:** {c['difficulty']}")

                # Check status
                status_btn = "Start Course"
                btn_type = "primary"

                if c['course_id'] in user_enrolled:
                    usr_c = user_enrolled[c['course_id']]
                    if usr_c['status'] == 'completed':
                        status_btn = "Review Course (Completed)"
                        btn_type = "secondary"
                    else:
                        status_btn = f"Continue Course ({usr_c['progress']}% Complete)"
                        btn_type = "primary"

                st.write("")
                if st.button(status_btn, key=f"course_nav_{c['course_id']}", type=btn_type, use_container_width=True):
                    # Enroll if not already
                    if c['course_id'] not in user_enrolled:
                        users.enroll_in_course(user['user_id'], c['course_id'])
                    st.session_state.active_course_id = c['course_id']
                    st.rerun()

# ----------------- COURSE DETAIL PAGE -----------------
def render_course_details():
    user = st.session_state.user
    course_id = st.session_state.active_course_id

    course = courses.get_course_by_id(course_id)
    if not course:
        st.error("Course not found.")
        return

    # Get user progress details
    user_courses_map = {c['course_id']: c for c in users.get_user_courses(user['user_id'])}
    user_enrollment = user_courses_map.get(course_id, {'progress': 0, 'status': 'enrolled'})

    if st.button("⬅️ Back to Courses"):
        st.session_state.active_course_id = None
        st.rerun()

    st.title(course['title'])
    st.markdown(f"👨🏫 **Instructor:** {course['instructor']} &nbsp;|&nbsp; ⏱️ **Duration:** {course['duration']} &nbsp;|&nbsp; 🏷️ **Difficulty:** {course['difficulty']}")

    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        st.subheader("Course Overview")
        st.write(course['description'])

        st.subheader("Skills Addressed")
        st.write("Completing this course contributes to achieving target levels in:")
        for comp in course['competencies']:
            st.markdown(f"- **{comp['name']}** (Up to Level {comp['target_level']} - *{competencies.get_competency_level_label(comp['target_level'])}*)")

        st.subheader("Learning Plan Content")

        # Generate mock slide blocks based on course
        st.markdown(f"""
        1. **Module 1: Core Fundamentals**
           Detailed foundational review slides and documents.
        2. **Module 2: Practical Exercises**
           Hands-on practice problems.
        3. **Module 3: Code Workthrough & Review**
           Working with real-world examples.
        """)

        st.write("")
        st.info("💡 Review the content sections to prepare for the final assessment.")

    with col2:
        # Sticky action card representation
        with st.container(border=True):
            st.subheader("Your Enrollment Status")
            st.write(f"**Current Status:** {user_enrollment['status'].title().replace('_', ' ')}")

            progress = user_enrollment['progress']
            st.write(f"**Progress:** {progress}%")
            st.progress(progress / 100)

            if user_enrollment['status'] != 'completed':
                # Button to simulate reading course content
                if progress < 100:
                    if st.button("📓 Study Course Materials (+50% Progress)", use_container_width=True, type="primary"):
                        new_progress = min(progress + 50, 100)
                        users.update_course_progress(user['user_id'], course_id, new_progress)
                        st.toast("Updated course study progress!")
                        st.rerun()

                # Check for target assessments
                if course['assessments']:
                    assessment_id = course['assessments'][0]['assessment_id']

                    st.write("")
                    st.write("---")
                    st.write("### Assessment Ready")
                    st.write("Ready to test your comprehension? Passing updates your competency score.")

                    if st.button("⚔️ Take Assessment", use_container_width=True, type="primary" if progress >= 100 else "secondary"):
                        # Open assessment quiz
                        st.session_state.active_assessment_id = assessment_id
                        st.session_state.quiz_step = 0
                        st.session_state.quiz_answers = []
                        st.rerun()
            else:
                st.success("🎉 You have completed this course!")
                if course['assessments']:
                    assessment_id = course['assessments'][0]['assessment_id']
                    if st.button("Review Assessment Results", use_container_width=True):
                        # Show user result
                        st.session_state.active_assessment_id = assessment_id
                        st.session_state.quiz_step = -1 # Result node code
                        st.rerun()

# ----------------- ASSESSMENT / QUIZ INTERFACE -----------------
def render_assessment_page():
    user = st.session_state.user
    assessment_id = st.session_state.active_assessment_id

    assessment = assessments.get_assessment_by_id(assessment_id)
    if not assessment:
        st.error("Assessment not found.")
        return

    questions = assessment['questions']
    total_q = len(questions)

    # Result summary screen (quiz_step == -1)
    if st.session_state.quiz_step == -1:
        st.title(f"🏆 {assessment['title']}")
        st.subheader("Quiz Results & Feedback")

        result = assessments.get_user_result_for_assessment(user['user_id'], assessment_id)
        if not result:
            st.info("No prior scores found for this assessment.")
        else:
            passed = result['score'] >= result['passing_score']
            st.write(f"**Date Taken:** {result['date'][:16]}")
            st.write(f"**Score:** {result['score']}% &nbsp;|&nbsp; **Required Passing:** {result['passing_score']}%")

            if passed:
                st.success("🎉 Congratulations! You passed the assessment.")
                # Show updated competency feedback
                st.markdown("""
                ### Updated Competencies
                Based on your successful assessment, the affected competency level on your profile has been updated!
                """)

                # Simulate updating the competencies that this course targets
                course_details = courses.get_course_by_id(assessment['course_id'])
                for comp in course_details['competencies']:
                    # Update competency of this user to course target level
                    competencies.update_user_competency(user['user_id'], comp['competency_id'], comp['target_level'])
                    st.write(f"✅ **{comp['name']}** updated to **Level {comp['target_level']} - {competencies.get_competency_level_label(comp['target_level'])}**")
            else:
                st.error("❌ You did not meet the passing score. We recommend studying the course material and retaking the quiz.")

        if st.button("Back to Course"):
            st.session_state.active_assessment_id = None
            st.session_state.active_course_id = assessment['course_id']
            st.rerun()
        return

    # Render Active Question Quiz Form
    step = st.session_state.quiz_step

    st.markdown(f"<h2>{assessment['title']}</h2>", unsafe_allow_html=True)
    st.progress((step + 1) / total_q)
    st.markdown(f"<p style='color: #64748B;'>Question <b>{step + 1}</b> of <b>{total_q}</b></p>", unsafe_allow_html=True)

    q = questions[step]
    options = json.loads(q['options'])

    with st.container(border=True):
        st.markdown(f"### {q['question']}")

        selected_option = st.radio(
            "Select the correct answer:",
            options,
            key=f"q_{q['question_id']}"
        )

    st.write("")
    nav_cols = st.columns([1, 8, 1.5])

    with nav_cols[0]:
        if step > 0:
            if st.button("◀️ Previous"):
                st.session_state.quiz_step -= 1
                st.session_state.quiz_answers.pop()
                st.rerun()

    with nav_cols[2]:
        btn_label = "Submit Answers" if step == total_q - 1 else "Next Question ▶️"

        if st.button(btn_label, type="primary", use_container_width=True):
            # Save answer index
            ans_idx = options.index(selected_option)
            st.session_state.quiz_answers.append(ans_idx)

            if step == total_q - 1:
                # Grade quiz
                submission = assessments.submit_assessment_result(
                    user['user_id'],
                    assessment_id,
                    st.session_state.quiz_answers
                )

                # Check if passed, if so we update user competencies
                if submission['passed']:
                    # Update course progress to 100 (completion status)
                    users.update_course_progress(user['user_id'], assessment['course_id'], 100)
                    # Update competencies (targets)
                    course_details = courses.get_course_by_id(assessment['course_id'])
                    for comp in course_details['competencies']:
                        competencies.update_user_competency(
                            user['user_id'],
                            comp['competency_id'],
                            comp['target_level']
                        )

                # Redirect to result node
                st.session_state.quiz_step = -1
                st.toast("Assessment submitted successfully!")
                st.rerun()
            else:
                st.session_state.quiz_step += 1
                st.rerun()

# ----------------- KNOWLEDGE HUB SECTION -----------------
def render_knowledge_hub_page():
    user = st.session_state.user

    # Subpage check for contribution form
    if 'show_contrib_form' in st.session_state and st.session_state.show_contrib_form:
        render_knowledge_contrib_page()
        return

    st.title("💡 Centralized Knowledge Hub")
    st.markdown("Discover guidelines, best practices, FAQs, case studies, and tutorials shared across departments.")

    cols = st.columns([2.5, 1, 1, 1])
    with cols[0]:
        search_query = st.text_input("Search the hub...", placeholder="Enter keywords, competencies, or title...")
    with cols[1]:
        st.write("")
        st.write("")
        contrib_btn = st.button("➕ Contribute Knowledge", use_container_width=True, type="primary")
        if contrib_btn:
            st.session_state.show_contrib_form = True
            st.rerun()

    # Filters Row
    categories = ["All"] + knowledge.get_categories()
    depts = ["All"] + knowledge.get_departments()

    filter_cols = st.columns(2)
    with filter_cols[0]:
        cat_filter = st.selectbox("Filter by Category", categories)
    with filter_cols[1]:
        dept_filter = st.selectbox("Filter by Department", depts)

    # Get resources
    cat_val = None if cat_filter == "All" else cat_filter
    dept_val = None if dept_filter == "All" else dept_filter

    if search_query:
        resources = knowledge.search_knowledge_resources(search_query, cat_val, dept_val)
    else:
        resources = knowledge.get_all_knowledge_resources(status='published', category=cat_val, department=dept_val)

    if not resources:
        st.info("No knowledge resources found matching the filter parameters.")
        return

    st.write("")

    # Grid display
    r_cols = st.columns(2)
    for idx, r in enumerate(resources):
        with r_cols[idx % 2]:
            with st.container(border=True):
                st.markdown(f"### {r['title']}")
                st.markdown(f"<span class='cc-badge cc-badge-draft'>{r['category']}</span> &bull; <span style='font-size:12px; color:#64748B;'>🏢 Department: <b>{r['department']}</b></span>", unsafe_allow_html=True)
                st.write(r['description'])

                # Mapped competencies
                comp_badges = " ".join([f'<span class="cc-badge cc-badge-progress">{comp["name"]}</span>' for comp in r['competencies']])
                st.markdown(f"**Competencies:** {comp_badges}", unsafe_allow_html=True)

                st.write("")
                st.markdown(f"<span style='font-size:12px; color:#64748B;'>✍️ Author: {r['author_name']} &nbsp;|&nbsp; 📅 Shared: {r['created_at'][:10]}</span>", unsafe_allow_html=True)

                if r['file_path']:
                    st.write("")
                    st.markdown(f"💾 [Download Resource Document]({r['file_path']})")

# ----------------- KNOWLEDGE CONTRIBUTION FORM -----------------
def render_knowledge_contrib_page():
    user = st.session_state.user

    st.title("➕ Submit a Knowledge Resource")
    st.markdown("Contribute reports, best practices, case studies, or field guides to the organization.")

    if st.button("⬅️ Back to Knowledge Hub"):
        st.session_state.show_contrib_form = False
        st.rerun()

    with st.form("contrib_form"):
        title = st.text_input("Resource Title", placeholder="e.g. Best Practices for GIS Coordinate Mapping")
        description = st.text_area("Summary / Description", placeholder="Outline the contents of this contribution...")

        cols = st.columns(2)
        with cols[0]:
            category = st.selectbox("Content Category / Type", ["Guidelines", "Case Study", "Best Practices", "Tutorial", "FAQ", "Field Experience", "Training Reference"])
            department = st.selectbox("Select Department Focus", [user['department'], "Analytics", "Engineering", "Management"])
        with cols[1]:
            # Select target competencies addressed
            all_comps = competencies.get_all_competencies()
            comp_names = [c['name'] for c in all_comps]
            target_comps = st.multiselect("Relevant Competencies Addressed", comp_names)

        file_path = st.text_input("Linked Document File Path (Optional)", placeholder="/docs/guideline_mapping.pdf")

        st.write("")
        submit = st.form_submit_button("Submit contribution for Approval", type="primary")

        if submit:
            if not title or not description:
                st.error("Please fill in the required Title and Description fields.")
            else:
                # Find matching competency IDs
                comp_ids = [c['competency_id'] for c in all_comps if c['name'] in target_comps]

                # Create contribution with status 'pending_review'
                knowledge.create_knowledge_resource(
                    title=title,
                    description=description,
                    category=category,
                    department=department,
                    author_id=user['user_id'],
                    file_path=file_path,
                    competency_ids=comp_ids,
                    status='pending_review'
                )

                st.success("🎉 Thank you! Your contribution has been submitted. An administrator will review and publish it shortly.")
                st.session_state.show_contrib_form = False
                st.rerun()

# ----------------- ADMIN DASHBOARD / OVERVIEW -----------------
def render_admin_overview():
    st.title("🏢 Organization Capacity Analytics")
    st.markdown("Real-time telemetry measuring skill gaps, department alignment, and active competency development.")

    metrics = analytics.get_org_capacity_metrics()

    # Metrics Row
    m_cols = st.columns(4)
    with m_cols[0]:
        draw_card("Total Employees", str(metrics['total_employees']), "", "Monitored")
    with m_cols[1]:
        draw_card("Avg Competency Level", f"{metrics['avg_competency_pct']}%", "+3% this quarter", "Score")
    with m_cols[2]:
        draw_card("Active Critical Gaps", str(metrics['critical_gaps_count']), "-12 this month", "Needs Intervention")
    with m_cols[3]:
        draw_card("Knowledge Hub resources", str(metrics['total_resources']), "+4 additions", "Published")

    col1, col2 = st.columns([1.2, 1], gap="large")

    with col1:
        st.subheader("Critical Competency Skill Gaps")
        st.write("Percentage of all employees currently failing to meet required competency level for their roles.")

        gaps = analytics.get_top_skill_gaps()
        if not gaps:
            st.info("No active role competency gaps detected.")
        else:
            names = [g['competency'] for g in gaps]
            pcts = [g['pct_affected'] for g in gaps]

            # Draw simple bar chart with plotly
            fig = px.bar(
                x=pcts,
                y=names,
                orientation='h',
                labels={'x': '% Employees Affected', 'y': ''},
                color=pcts,
                color_continuous_scale=px.colors.sequential.Reds,
                text_auto=True
            )
            fig.update_layout(showlegend=False, height=350, margin=dict(l=40, r=40, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Competency Score by Department")

        dept_avgs = analytics.get_department_competency_averages()
        if not dept_avgs:
            st.info("No department averages computed.")
        else:
            depts = [d['department'] for d in dept_avgs]
            scores = [d['avg_competency_pct'] for d in dept_avgs]

            fig = px.bar(
                x=depts,
                y=scores,
                labels={'x': '', 'y': 'Average Score %'},
                color=scores,
                color_continuous_scale=px.colors.sequential.Viridis,
                text_auto=True
            )
            fig.update_layout(showlegend=False, height=350, margin=dict(l=40, r=40, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Training Demand by Targets")
    demand = analytics.get_training_demand_by_competency()
    if demand:
        d_df = pd.DataFrame(demand)
        st.bar_chart(d_df, x="competency_name", y="enrollment_count", use_container_width=True)

# ----------------- ADMIN COMPETENCY MANAGEMENT -----------------
def render_admin_competencies():
    st.title("🧬 Competency Domain Management")
    st.markdown("Create, edit, or archive skill competencies across the organization.")

    # Sub-form to create competency
    with st.expander("➕ Define New Competency"):
        name = st.text_input("Competency name", placeholder="e.g. Prompt Engineering")
        desc = st.text_area("Description", placeholder="Describe standard expectations...")

        if st.button("Save Domain"):
            if name:
                competencies.create_competency(name, desc)
                st.success("Successfully added domain.")
                st.rerun()
            else:
                st.error("Name is required.")

    st.subheader("Defined Competency Standards")
    all_c = competencies.get_all_competencies()
    c_df = pd.DataFrame(all_c)

    st.dataframe(
        c_df,
        column_config={
            "competency_id": "ID",
            "name": "Competency Name",
            "description": "Standard Specification"
        },
        use_container_width=True,
        hide_index=True
    )

# ----------------- ADMIN ROLE MAPPING -----------------
def render_role_mapping():
    st.title("🗺️ Role → Competency Mapping")
    st.markdown("Map competencies and required levels for specific organizational designations.")

    roles = competencies.get_all_roles()
    selected_role = st.selectbox("Select Role to Configure", roles)

    st.write(f"### Current Requirements for: **{selected_role}**")

    current_mappings = competencies.get_role_competencies(selected_role)
    if not current_mappings:
        st.info("No competencies mapped to this role yet.")
    else:
        # Display as key value settings
        for m in current_mappings:
            cols = st.columns([3, 1.5, 0.5])
            with cols[0]:
                st.write(f"**{m['name']}**")
            with cols[1]:
                # Update inline dropdown
                levels = [1, 2, 3, 4, 5]
                new_lvl = st.selectbox(
                    "Required Level",
                    levels,
                    index=levels.index(m['required_level']),
                    key=f"role_lvl_{m['competency_id']}"
                )
                if new_lvl != m['required_level']:
                    competencies.map_competency_to_role(selected_role, m['competency_id'], new_lvl)
                    st.toast("Updated required level!")
                    st.rerun()
            with cols[2]:
                st.write("")
                if st.button("🗑️", key=f"delete_mapping_{m['competency_id']}"):
                    competencies.remove_competency_from_role(selected_role, m['competency_id'])
                    st.toast("Removed competency mapping from role")
                    st.rerun()

    st.write("---")
    st.subheader("Add Competency Requirement")
    all_comps = competencies.get_all_competencies()
    mapped_ids = {m['competency_id'] for m in current_mappings}
    available_comps = [c for c in all_comps if c['competency_id'] not in mapped_ids]

    if not available_comps:
        st.info("All standard competencies are already mapped to this role.")
    else:
        with st.form("new_mapping_form"):
            comp_box = st.selectbox("Select Competency to Add", [c['name'] for c in available_comps])
            lvl_box = st.selectbox("Required Competency Level", [1, 2, 3, 4, 5])

            submit = st.form_submit_button("Add Requirement")
            if submit:
                target_comp = next(c for c in available_comps if c['name'] == comp_box)
                competencies.map_competency_to_role(selected_role, target_comp['competency_id'], lvl_box)
                st.success("Added requirement successfully!")
                st.rerun()

# ----------------- ADMIN COURSE BUILDER -----------------
def render_course_builder():
    st.title("🏗️ Course Module Builder")
    st.markdown("Create learning modules, associate competencies, and configure target levels.")

    with st.expander("➕ Create New Course Module"):
        with st.form("new_course_form"):
            title = st.text_input("Course Title", placeholder="e.g. Intermediate GIS Mapping")
            desc = st.text_area("Course Syllabus / Description")
            instructor = st.text_input("Instructor Name / Institution")

            cols = st.columns(3)
            with cols[0]:
                difficulty = st.selectbox("Target Difficulty", ["Beginner", "Intermediate", "Advanced"])
            with cols[1]:
                duration = st.text_input("Expected Duration", placeholder="e.g. 5 hours")
            with cols[2]:
                status = st.selectbox("Initial Publish Status", ["draft", "published"])

            submit_course = st.form_submit_button("Create Module")

            if submit_course:
                if title:
                    new_id = courses.create_course(title, desc, instructor, difficulty, duration, status)
                    st.success(f"Course '{title}' successfully created as ID: {new_id}!")
                    st.rerun()
                else:
                    st.error("Course title is required.")

    st.subheader("Published Learning Modules")
    all_courses = courses.get_all_courses()

    for c in all_courses:
        course_details = courses.get_course_by_id(c['course_id'])
        with st.container(border=True):
            cols = st.columns([4, 1.5])
            with cols[0]:
                st.markdown(f"### {c['title']} (`#{c['course_id']}`) &nbsp; <span class='cc-badge cc-badge-{c['status']}'>{c['status']}</span>", unsafe_allow_html=True)
                st.write(c['description'])
                st.write(f"👨🏫 **Instructor:** {c['instructor']} &nbsp;|&nbsp; ⏱️ **Duration:** {c['duration']} &nbsp;|&nbsp; 🏷️ **Difficulty:** {c['difficulty']}")

                # Mapped competencies
                st.write("**Target Competencies Addressed:**")
                comp_badges = " ".join([f'<span class="cc-badge cc-badge-progress">{comp["name"]} (Lvl {comp["target_level"]})</span>' for comp in course_details['competencies']])
                st.markdown(comp_badges if comp_badges else "*None configured yet*", unsafe_allow_html=True)

            with cols[1]:
                st.write("")
                # Configuration Actions
                if st.button("Archive Module", key=f"archive_{c['course_id']}"):
                    courses.update_course(c['course_id'], status='archived')
                    st.toast("Archived course module!")
                    st.rerun()

                # Config competency target mapping
                st.write("---")
                all_c = competencies.get_all_competencies()
                mapped_comp_ids = {comp['competency_id'] for comp in course_details['competencies']}
                avail = [comp for comp in all_c if comp['competency_id'] not in mapped_comp_ids]

                if avail:
                    comp_map_box = st.selectbox("Link Competency", [comp['name'] for comp in avail], key=f"comp_link_select_{c['course_id']}")
                    lvl_map_box = st.selectbox("Target Level", [1, 2, 3, 4, 5], key=f"comp_link_level_{c['course_id']}")

                    if st.button("Associate Skill", key=f"associate_btn_{c['course_id']}", use_container_width=True):
                        sel_comp = next(comp for comp in avail if comp['name'] == comp_map_box)
                        courses.add_competency_to_course(c['course_id'], sel_comp['competency_id'], lvl_map_box)
                        st.toast("Successfully mapped competency target!")
                        st.rerun()

# ----------------- ADMIN KNOWLEDGE HUB REVIEW -----------------
def render_knowledge_review():
    st.title("📥 Knowledge Hub Contribution Review")
    st.markdown("Approve or reject community-submitted articles and resources before publishing them to the public pool.")

    # Get resources pending review
    pending = knowledge.get_all_knowledge_resources(status='pending_review')

    if not pending:
        st.success("✨ All pending knowledge contributions have been reviewed!")
        return

    for r in pending:
        with st.container(border=True):
            cols = st.columns([4, 1.5])
            with cols[0]:
                st.markdown(f"### {r['title']}")
                st.markdown(f"<span class='cc-badge cc-badge-medium'>Pending Review</span> &bull; 🏷️ **Type:** {r['category']} &nbsp;|&nbsp; 🏢 **Dept:** {r['department']}", unsafe_allow_html=True)
                st.write(r['description'])
                if r['file_path']:
                    st.write(f"💾 **Linked path:** {r['file_path']}")

                # Mapped competencies
                comp_badges = " ".join([f'<span class="cc-badge cc-badge-progress">{comp["name"]}</span>' for comp in r['competencies']])
                st.markdown(f"**Tag competencies:** {comp_badges if comp_badges else '*None*'}", unsafe_allow_html=True)
                st.write(f"✍️ **Submitted by:** {r['author_name']}")

            with cols[1]:
                st.write("")
                st.write("")
                if st.button("✅ Approve & Publish", key=f"app_{r['resource_id']}", use_container_width=True):
                    knowledge.approve_knowledge_resource(r['resource_id'])
                    st.toast("Appeared in Knowledge Hub!")
                    st.rerun()
                if st.button("❌ Reject / Draft", key=f"rej_{r['resource_id']}", use_container_width=True):
                    knowledge.reject_knowledge_resource(r['resource_id'])
                    st.toast("Sent back to contributors drafts.")
                    st.rerun()

# ----------------- MAIN FLOW ROUTER -----------------
def main():
    if not st.session_state.logged_in:
        render_login_page()
    else:
        render_sidebar()

        # Render the correct main page based on session state
        page = st.session_state.current_page

        # Router
        if page == "Dashboard":
            render_employee_dashboard()
        elif page == "My Competencies":
            render_my_competencies_page()
        elif page == "Skill Gaps":
            render_skill_gaps_page()
        elif page == "Learning Path":
            render_learning_path_page()
        elif page == "Courses":
            render_courses_page()
        elif page == "Knowledge Hub":
            render_knowledge_hub_page()
        elif page == "Admin Overview":
            render_admin_overview()
        elif page == "Competencies Mgnt":
            render_admin_competencies()
        elif page == "Role Competencies":
            render_role_mapping()
        elif page == "Course Builder":
            render_course_builder()
        elif page == "Knowledge Review":
            render_knowledge_review()

if __name__ == "__main__":
    main()