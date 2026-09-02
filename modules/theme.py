def get_light_css():
    return """
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
"""

def get_dark_css():
    return """
<style>
    /* Force light text on dark backgrounds - override Streamlit defaults */
    .stApp, .stApp * {
        color: #F8FAFC !important;
    }

    /* Main Layout - force background */
    .stApp {
        background-color: #0F172A !important;
    }

    /* Main content area */
    .main .block-container {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
    }

    /* Typography */
    html, body, [class*="css"], .stMarkdown, .stText, p, span, div, h1, h2, h3, h4, h5, h6, label {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: #F8FAFC !important;
    }

    /* Input fields - ensure readable text */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div,
    .stMultiSelect > div > div > div {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
    }

    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
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
        background-color: #60A5FA !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
    }

    .stButton > button[kind="secondary"] {
        background-color: #334155 !important;
        color: #F8FAFC !important;
        border: 1px solid #475569 !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background-color: #475569 !important;
        color: #F8FAFC !important;
    }

    /* Cards/Containers */
    .stContainer, div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
    }

    /* Clean Cards */
    .cc-card {
        background-color: #1E293B !important;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #334155;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        color: #F8FAFC !important;
    }

    .cc-kpi-val {
        font-size: 28px;
        font-weight: 700;
        color: #F8FAFC !important;
        margin: 4px 0;
    }

    .cc-kpi-change-pos {
        color: #34D399 !important;
        font-size: 14px;
        font-weight: 600;
    }

    .cc-kpi-change-neg {
        color: #F87171 !important;
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
    .cc-badge-critical { background-color: #7F1D1D !important; color: #FECACA !important; }
    .cc-badge-medium { background-color: #78350F !important; color: #FDE68A !important; }
    .cc-badge-low { background-color: #713F12 !important; color: #FEF08A !important; }
    .cc-badge-nogap { background-color: #064E3B !important; color: #A7F3D0 !important; }
    .cc-badge-progress { background-color: #1E3A8A !important; color: #BFDBFE !important; }
    .cc-badge-draft { background-color: #334155 !important; color: #CBD5E1 !important; }

    /* Sidebar - force light text */
    .stSidebar, .stSidebar * {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
    }

    .stSidebar .stButton > button {
        background-color: #334155 !important;
        color: #F8FAFC !important;
        border: 1px solid #475569 !important;
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
        color: #F8FAFC !important;
        font-size: 28px !important;
        font-weight: 700 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #94A3B8 !important;
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
        color: #F8FAFC !important;
    }

    .stRadio > div[role="radiogroup"] > label {
        background-color: #0F172A !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
        margin: 8px 0 !important;
        color: #F8FAFC !important;
    }

    .stRadio > div[role="radiogroup"] > label:hover {
        background-color: #1E3A8A !important;
        border-color: #3B82F6 !important;
    }

    .stRadio > div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #1E3A8A !important;
        border-color: #3B82F6 !important;
    }

    /* Dataframe/Table */
    .stDataFrame, .stTable {
        color: #F8FAFC !important;
    }

    .stDataFrame [data-testid="stDataFrameResizable"] {
        background-color: #1E293B !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #334155 !important;
        border-radius: 8px !important;
        padding: 4px !important;
    }

    .stTabs [data-baseweb="tab"] {
        color: #CBD5E1 !important;
        font-weight: 500 !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #1E293B !important;
        color: #60A5FA !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3) !important;
    }

    /* Selectbox dropdown */
    .stSelectbox [data-baseweb="select"] > div {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
    }

    /* Form submit button */
    .stFormSubmitButton > button {
        background-color: #3B82F6 !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: #0F172A !important;
        color: #F8FAFC !important;
        font-weight: 600 !important;
    }

    .streamlit-expanderContent {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
    }

    /* File uploader */
    .stFileUploader > div {
        background-color: #0F172A !important;
        border: 2px dashed #334155 !important;
        border-radius: 12px !important;
    }

    /* Toast/Notifications */
    .stToast {
        background-color: #334155 !important;
        color: #F8FAFC !important;
    }

    /* Learning Path Connection Nodes */
    .lp-node {
        padding: 16px;
        background-color: #1E293B !important;
        border-radius: 8px;
        border: 1px solid #334155;
        text-align: center;
        margin: 10px 0;
        color: #F8FAFC !important;
    }
    .lp-arrow {
        text-align: center;
        font-size: 20px;
        color: #94A3B8 !important;
        margin: 5px 0;
    }

    /* Force all markdown text to be dark */
    .stMarkdown, .stMarkdown * {
        color: #F8FAFC !important;
    }

    /* Override any white text on white backgrounds */
    .element-container, .element-container * {
        color: #F8FAFC !important;
    }
</style>
"""
