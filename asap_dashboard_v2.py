"""
ASAP Data Dashboard - Bronx Community College
A comprehensive analytics platform for ASAP student success tracking
"""

import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

# ========== PAGE CONFIG ==========
st.set_page_config(
    page_title="ASAP Data Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CUSTOM CSS ==========
st.markdown("""
<style>
    /* Import beautiful fonts */
    @import url('https://fonts.googleapis.com/css2?family=Spectral:wght@400;600;700&family=Work+Sans:wght@300;400;500;600&display=swap');
    
    /* Global styling */
    html, body, [class*="css"] {
        font-family: 'Work Sans', sans-serif;
    }
    
    /* Headers with editorial font */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Spectral', serif !important;
        font-weight: 600 !important;
        color: #1a1a1a !important;
    }
    
    /* Main title styling */
    .main-title {
        font-family: 'Spectral', serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2E3192 0%, #1BFFFF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        line-height: 1.2;
    }
    
    .subtitle {
        font-family: 'Work Sans', sans-serif;
        font-size: 1.1rem;
        color: #666;
        font-weight: 300;
        margin-bottom: 2rem;
    }
    
    /* Metric cards with gradient accents */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 4px solid #2E3192;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2E3192;
        font-family: 'Spectral', serif;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        font-weight: 500;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2E3192 0%, #1a1f5c 100%);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Navigation buttons */
    .nav-button {
        background: rgba(255,255,255,0.1);
        border: 1px solid rgba(255,255,255,0.2);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        font-weight: 500;
    }
    
    .nav-button:hover {
        background: rgba(255,255,255,0.2);
        transform: translateX(5px);
    }
    
    .nav-button.active {
        background: rgba(27,255,255,0.2);
        border-color: #1BFFFF;
    }
    
    /* Data tables */
    .dataframe {
        font-size: 0.9rem;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-compliant {
        background: #d4edda;
        color: #155724;
    }
    
    .status-warning {
        background: #fff3cd;
        color: #856404;
    }
    
    .status-error {
        background: #f8d7da;
        color: #721c24;
    }
    
    /* Section headers */
    .section-header {
        border-left: 4px solid #1BFFFF;
        padding-left: 1rem;
        margin: 2rem 0 1rem 0;
    }
    
    /* Info boxes */
    .info-box {
        background: linear-gradient(135deg, rgba(46,49,146,0.05) 0%, rgba(27,255,255,0.05) 100%);
        border: 1px solid rgba(46,49,146,0.2);
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ========== DATABASE CONNECTION ==========
@st.cache_resource
def get_database_path():
    """Get database path - update this to your actual path"""
    return r"C:\Users\gioconda.prada-rinc\OneDrive - CUNY\BCC\ASAP_Data_System\asap_data.db"

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data(query):
    """Load data from database with caching"""
    db_path = get_database_path()
    if not os.path.exists(db_path):
        st.error(f"Database not found at: {db_path}")
        return pd.DataFrame()
    
    try:
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def load_benchmark_data():
    """Load benchmark compliance data"""
    query = """
    SELECT * FROM benchmark_compliance 
    WHERE ingestion_date = (SELECT MAX(ingestion_date) FROM benchmark_compliance)
    ORDER BY "Last Name", "First Name"
    """
    return load_data(query)

def load_fafsa_data():
    """Load FAFSA/TAP status data"""
    query = """
    SELECT * FROM fafsa_tap_status 
    WHERE report_date = (SELECT MAX(report_date) FROM fafsa_tap_status)
    ORDER BY "Last Name", "First Name"
    """
    return load_data(query)

def load_errors_data():
    """Load appointment errors data"""
    query = """
    SELECT * FROM appointment_errors 
    WHERE report_date = (SELECT MAX(report_date) FROM appointment_errors)
    ORDER BY "Scheduled Start Date" DESC
    """
    return load_data(query)

def load_wn_grades_data():
    """Load WN grades data"""
    query = """
    SELECT * FROM wn_grade_report 
    WHERE report_date = (SELECT MAX(report_date) FROM wn_grade_report)
    ORDER BY "Last Name", "First Name"
    """
    return load_data(query)

# ========== HELPER FUNCTIONS ==========
def create_kpi_card(label, value, delta=None, delta_color="normal"):
    """Create a styled KPI metric card"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value:,}</div>
        </div>
        """, unsafe_allow_html=True)

def display_data_table(df, title, download_filename=None):
    """Display a formatted data table with download option"""
    st.markdown(f'<div class="section-header"><h3>{title}</h3></div>', unsafe_allow_html=True)
    
    if df.empty:
        st.info("No data available")
        return
    
    # Display the table
    st.dataframe(df, use_container_width=True, height=400)
    
    # Download button
    if download_filename:
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download as CSV",
            data=csv,
            file_name=download_filename,
            mime="text/csv"
        )

# ========== NAVIGATION ==========
def render_sidebar():
    """Render sidebar navigation"""
    with st.sidebar:
        # ASAP Logo
        logo_path = r"C:\Users\gioconda.prada-rinc\OneDrive - CUNY\BCC\ASAP_Data_System\asap_logo.png"
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=True)
            st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
        else:
            st.markdown('<h1 style="color: white; margin-top: 0;">📊 ASAP Dashboard</h1>', unsafe_allow_html=True)
        
        st.markdown('<p style="color: rgba(255,255,255,0.7); margin-bottom: 2rem;">Bronx Community College</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        pages = {
            "🏠 Overview": "overview",
            "📋 Benchmark Compliance": "benchmark",
            "💰 FAFSA & TAP": "fafsa",
            "⚠️ Appointment Errors": "errors",
            "📝 WN Grades": "wn_grades"
        }
        
        if 'current_page' not in st.session_state:
            st.session_state.current_page = 'overview'
        
        for label, page_id in pages.items():
            if st.button(label, key=page_id, use_container_width=True):
                st.session_state.current_page = page_id
                st.rerun()
        
        st.markdown("---")
        
        # Info section
        st.markdown("""
        <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; margin-top: 2rem;">
            <p style="font-size: 0.85rem; margin: 0; opacity: 0.8;">
                <strong>Last Updated:</strong><br>
                Data refreshes every 5 minutes
            </p>
        </div>
        """, unsafe_allow_html=True)

# ========== PAGE: OVERVIEW ==========
def page_overview():
    """Main overview dashboard"""
    st.markdown('<h1 class="main-title">ASAP Data Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Comprehensive student success tracking and analytics</p>', unsafe_allow_html=True)
    
    # Load all data
    df_benchmark = load_benchmark_data()
    df_fafsa = load_fafsa_data()
    df_errors = load_errors_data()
    df_wn = load_wn_grades_data()
    
    # KPI Cards
    st.markdown("### 📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_students = len(df_benchmark) if not df_benchmark.empty else 0
        create_kpi_card("Total ASAP Students", total_students)
    
    with col2:
        fafsa_issues = len(df_fafsa) if not df_fafsa.empty else 0
        create_kpi_card("FAFSA/TAP Issues", fafsa_issues)
    
    with col3:
        appt_errors = len(df_errors) if not df_errors.empty else 0
        create_kpi_card("Appointment Errors", appt_errors)
    
    with col4:
        wn_students = len(df_wn) if not df_wn.empty else 0
        create_kpi_card("Students with WN", wn_students)
    
    st.markdown("---")
    
    # Quick insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 Benchmark Compliance")
        if not df_benchmark.empty and 'Compliance Status' in df_benchmark.columns:
            status_counts = df_benchmark['Compliance Status'].value_counts()
            
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title="Advisor Meeting Compliance",
                color_discrete_sequence=['#2E3192', '#1BFFFF', '#FF6B6B']
            )
            fig.update_layout(
                font=dict(family='Work Sans', size=12),
                title_font=dict(family='Spectral', size=16)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No benchmark data available")
    
    with col2:
        st.markdown("### ⚠️ Recent Errors")
        if not df_errors.empty:
            # Show top 5 recent errors
            recent_errors = df_errors.head(5)[['Student Name', 'Advisor', 'Scheduled Start Date']]
            st.dataframe(recent_errors, use_container_width=True, hide_index=True)
        else:
            st.success("No appointment errors! 🎉")
    
    # Quick actions
    st.markdown("---")
    st.markdown("### 🚀 Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("📋 View Benchmark Details", use_container_width=True):
            st.session_state.current_page = 'benchmark'
            st.rerun()
    with col2:
        if st.button("💰 View FAFSA Issues", use_container_width=True):
            st.session_state.current_page = 'fafsa'
            st.rerun()
    with col3:
        if st.button("⚠️ View All Errors", use_container_width=True):
            st.session_state.current_page = 'errors'
            st.rerun()
    with col4:
        if st.button("📝 View WN Grades", use_container_width=True):
            st.session_state.current_page = 'wn_grades'
            st.rerun()

# ========== PAGE: BENCHMARK COMPLIANCE ==========
def page_benchmark():
    """Benchmark compliance report page"""
    st.markdown('<h1 class="main-title">📋 Benchmark Compliance</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Advisor meeting compliance tracking</p>', unsafe_allow_html=True)
    
    df = load_benchmark_data()
    
    if df.empty:
        st.warning("No benchmark data available")
        return
    
    # Filters
    st.markdown("### 🔍 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'Advisor' in df.columns:
            advisors = ['All'] + sorted(df['Advisor'].dropna().unique().tolist())
            selected_advisor = st.selectbox("Select Advisor", advisors)
    
    with col2:
        if 'Cohort Name' in df.columns:
            cohorts = ['All'] + sorted(df['Cohort Name'].dropna().unique().tolist())
            selected_cohort = st.selectbox("Select Cohort", cohorts)
    
    with col3:
        if 'Compliance Status' in df.columns:
            statuses = ['All'] + sorted(df['Compliance Status'].dropna().unique().tolist())
            selected_status = st.selectbox("Compliance Status", statuses)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_advisor != 'All':
        filtered_df = filtered_df[filtered_df['Advisor'] == selected_advisor]
    if selected_cohort != 'All':
        filtered_df = filtered_df[filtered_df['Cohort Name'] == selected_cohort]
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['Compliance Status'] == selected_status]
    
    # Summary metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_kpi_card("Total Students", len(filtered_df))
    
    with col2:
        if 'Compliance Status' in filtered_df.columns:
            compliant = len(filtered_df[filtered_df['Compliance Status'] == 'Compliant'])
            create_kpi_card("Compliant", compliant)
    
    with col3:
        if 'Compliance Status' in filtered_df.columns:
            non_compliant = len(filtered_df[filtered_df['Compliance Status'] == 'Non-Compliant'])
            create_kpi_card("Non-Compliant", non_compliant)
    
    with col4:
        if 'Advisor' in filtered_df.columns:
            unique_advisors = filtered_df['Advisor'].nunique()
            create_kpi_card("Advisors", unique_advisors)
    
    # Visualizations
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Advisor' in filtered_df.columns and 'Compliance Status' in filtered_df.columns:
            st.markdown("### 👥 Compliance by Advisor")
            advisor_status = filtered_df.groupby(['Advisor', 'Compliance Status']).size().reset_index(name='Count')
            
            fig = px.bar(
                advisor_status,
                x='Advisor',
                y='Count',
                color='Compliance Status',
                title="Students by Advisor and Status",
                color_discrete_map={
                    'Compliant': '#2E3192',
                    'Non-Compliant': '#FF6B6B',
                    'Partially Compliant': '#FFD93D'
                }
            )
            fig.update_layout(
                font=dict(family='Work Sans'),
                title_font=dict(family='Spectral', size=16),
                xaxis_title="",
                yaxis_title="Number of Students"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Cohort Name' in filtered_df.columns:
            st.markdown("### 📚 Students by Cohort")
            cohort_counts = filtered_df['Cohort Name'].value_counts()
            
            fig = px.bar(
                x=cohort_counts.index,
                y=cohort_counts.values,
                title="Student Distribution by Cohort",
                color_discrete_sequence=['#1BFFFF']
            )
            fig.update_layout(
                font=dict(family='Work Sans'),
                title_font=dict(family='Spectral', size=16),
                xaxis_title="",
                yaxis_title="Number of Students",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.markdown("---")
    display_data_table(
        filtered_df,
        f"📊 Student Details ({len(filtered_df)} records)",
        f"benchmark_compliance_{datetime.now().strftime('%Y%m%d')}.csv"
    )

# ========== PAGE: FAFSA & TAP ==========
def page_fafsa():
    """FAFSA & TAP issues page"""
    st.markdown('<h1 class="main-title">💰 FAFSA & TAP Issues</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Financial aid application tracking</p>', unsafe_allow_html=True)
    
    df = load_fafsa_data()
    
    if df.empty:
        st.success("No FAFSA/TAP issues found! 🎉")
        return
    
    # Filters
    st.markdown("### 🔍 Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Advisor' in df.columns:
            advisors = ['All'] + sorted(df['Advisor'].dropna().unique().tolist())
            selected_advisor = st.selectbox("Select Advisor", advisors)
    
    with col2:
        if 'Cohort Name' in df.columns:
            cohorts = ['All'] + sorted(df['Cohort Name'].dropna().unique().tolist())
            selected_cohort = st.selectbox("Select Cohort", cohorts)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_advisor != 'All':
        filtered_df = filtered_df[filtered_df['Advisor'] == selected_advisor]
    if selected_cohort != 'All':
        filtered_df = filtered_df[filtered_df['Cohort Name'] == selected_cohort]
    
    # Summary metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_kpi_card("Students with Issues", len(filtered_df))
    
    with col2:
        if 'TAP_Status' in filtered_df.columns:
            tap_issues = filtered_df['TAP_Status'].notna().sum()
            create_kpi_card("TAP Issues", tap_issues)
    
    with col3:
        if 'EFC_Status' in filtered_df.columns:
            efc_issues = filtered_df['EFC_Status'].notna().sum()
            create_kpi_card("EFC Issues", efc_issues)
    
    with col4:
        if 'Advisor' in filtered_df.columns:
            unique_advisors = filtered_df['Advisor'].nunique()
            create_kpi_card("Advisors Affected", unique_advisors)
    
    # Issue breakdown
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Issues by Type")
        issue_counts = {
            'TAP Status': filtered_df['TAP_Status'].notna().sum() if 'TAP_Status' in filtered_df.columns else 0,
            'EFC Status': filtered_df['EFC_Status'].notna().sum() if 'EFC_Status' in filtered_df.columns else 0,
            'ATB': filtered_df['ATB'].notna().sum() if 'ATB' in filtered_df.columns else 0,
            'Tuition Group': filtered_df['Tuition_Group'].notna().sum() if 'Tuition_Group' in filtered_df.columns else 0
        }
        
        fig = px.bar(
            x=list(issue_counts.keys()),
            y=list(issue_counts.values()),
            title="Number of Students by Issue Type",
            color_discrete_sequence=['#2E3192']
        )
        fig.update_layout(
            font=dict(family='Work Sans'),
            title_font=dict(family='Spectral', size=16),
            xaxis_title="",
            yaxis_title="Number of Students",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Advisor' in filtered_df.columns:
            st.markdown("### 👥 Issues by Advisor")
            advisor_counts = filtered_df['Advisor'].value_counts().head(10)
            
            fig = px.bar(
                x=advisor_counts.values,
                y=advisor_counts.index,
                orientation='h',
                title="Top 10 Advisors by Student Count",
                color_discrete_sequence=['#1BFFFF']
            )
            fig.update_layout(
                font=dict(family='Work Sans'),
                title_font=dict(family='Spectral', size=16),
                xaxis_title="Number of Students",
                yaxis_title="",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.markdown("---")
    display_data_table(
        filtered_df,
        f"📊 Student Details ({len(filtered_df)} records)",
        f"fafsa_tap_issues_{datetime.now().strftime('%Y%m%d')}.csv"
    )

# ========== PAGE: APPOINTMENT ERRORS ==========
def page_errors():
    """Appointment errors page"""
    st.markdown('<h1 class="main-title">⚠️ Appointment Errors</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Missing appointments and data entry errors</p>', unsafe_allow_html=True)
    
    df = load_errors_data()
    
    if df.empty:
        st.success("No appointment errors! 🎉")
        return
    
    # Filters
    st.markdown("### 🔍 Filters")
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Advisor' in df.columns:
            advisors = ['All'] + sorted(df['Advisor'].dropna().unique().tolist())
            selected_advisor = st.selectbox("Select Advisor", advisors)
    
    with col2:
        error_types = ['All', 'Missing Letters', 'Duplicate A', 'Duplicate B', 'B - Two-Way Electronic']
        selected_error = st.selectbox("Error Type", error_types)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_advisor != 'All':
        filtered_df = filtered_df[filtered_df['Advisor'] == selected_advisor]
    
    if selected_error != 'All':
        if selected_error == 'Missing Letters':
            filtered_df = filtered_df[filtered_df['Missing Letters'].notna() & (filtered_df['Missing Letters'] != '')]
        elif selected_error == 'Duplicate A':
            filtered_df = filtered_df[filtered_df['Duplicate A?'] == 'Yes']
        elif selected_error == 'Duplicate B':
            filtered_df = filtered_df[filtered_df['Duplicate B?'] == 'Yes']
        elif selected_error == 'B - Two-Way Electronic':
            filtered_df = filtered_df[filtered_df['B - Two-Way Electronic?'] == 'Yes']
    
    # Summary metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_kpi_card("Total Errors", len(filtered_df))
    
    with col2:
        missing = len(filtered_df[filtered_df['Missing Letters'].notna() & (filtered_df['Missing Letters'] != '')])
        create_kpi_card("Missing Letters", missing)
    
    with col3:
        dup_a = len(filtered_df[filtered_df['Duplicate A?'] == 'Yes'])
        create_kpi_card("Duplicate A", dup_a)
    
    with col4:
        dup_b = len(filtered_df[filtered_df['Duplicate B?'] == 'Yes'])
        create_kpi_card("Duplicate B", dup_b)
    
    # Visualizations
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Advisor' in filtered_df.columns:
            st.markdown("### 👥 Errors by Advisor")
            advisor_counts = filtered_df['Advisor'].value_counts().head(10)
            
            fig = px.bar(
                x=advisor_counts.values,
                y=advisor_counts.index,
                orientation='h',
                title="Top 10 Advisors by Error Count",
                color_discrete_sequence=['#FF6B6B']
            )
            fig.update_layout(
                font=dict(family='Work Sans'),
                title_font=dict(family='Spectral', size=16),
                xaxis_title="Number of Errors",
                yaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Error Type Distribution")
        error_counts = {
            'Missing Letters': len(filtered_df[filtered_df['Missing Letters'].notna() & (filtered_df['Missing Letters'] != '')]),
            'Duplicate A': len(filtered_df[filtered_df['Duplicate A?'] == 'Yes']),
            'Duplicate B': len(filtered_df[filtered_df['Duplicate B?'] == 'Yes']),
            'Two-Way Electronic': len(filtered_df[filtered_df['B - Two-Way Electronic?'] == 'Yes'])
        }
        
        fig = px.pie(
            values=list(error_counts.values()),
            names=list(error_counts.keys()),
            title="Error Types",
            color_discrete_sequence=['#FF6B6B', '#FFD93D', '#1BFFFF', '#2E3192']
        )
        fig.update_layout(
            font=dict(family='Work Sans'),
            title_font=dict(family='Spectral', size=16)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.markdown("---")
    display_data_table(
        filtered_df,
        f"📊 Error Details ({len(filtered_df)} records)",
        f"appointment_errors_{datetime.now().strftime('%Y%m%d')}.csv"
    )

# ========== PAGE: WN GRADES ==========
def page_wn_grades():
    """WN grades report page"""
    st.markdown('<h1 class="main-title">📝 WN Grades Report</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Students with warning/non-passing grades</p>', unsafe_allow_html=True)
    
    df = load_wn_grades_data()
    
    if df.empty:
        st.success("No WN grades found! 🎉")
        return
    
    # Filters
    st.markdown("### 🔍 Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'Advisor' in df.columns:
            advisors = ['All'] + sorted(df['Advisor'].dropna().unique().tolist())
            selected_advisor = st.selectbox("Select Advisor", advisors)
    
    with col2:
        if 'Cohort' in df.columns:
            cohorts = ['All'] + sorted(df['Cohort'].dropna().unique().tolist())
            selected_cohort = st.selectbox("Select Cohort", cohorts)
    
    with col3:
        if 'Support Level' in df.columns:
            levels = ['All'] + sorted(df['Support Level'].dropna().unique().tolist())
            selected_level = st.selectbox("Support Level", levels)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_advisor != 'All':
        filtered_df = filtered_df[filtered_df['Advisor'] == selected_advisor]
    if selected_cohort != 'All':
        filtered_df = filtered_df[filtered_df['Cohort'] == selected_cohort]
    if selected_level != 'All':
        filtered_df = filtered_df[filtered_df['Support Level'] == selected_level]
    
    # Summary metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        create_kpi_card("Students with WN", len(filtered_df))
    
    with col2:
        if 'Advisor' in filtered_df.columns:
            unique_advisors = filtered_df['Advisor'].nunique()
            create_kpi_card("Advisors Affected", unique_advisors)
    
    with col3:
        if 'Cohort' in filtered_df.columns:
            unique_cohorts = filtered_df['Cohort'].nunique()
            create_kpi_card("Cohorts Affected", unique_cohorts)
    
    with col4:
        if 'Support Level' in filtered_df.columns:
            high_support = len(filtered_df[filtered_df['Support Level'].str.contains('High', case=False, na=False)])
            create_kpi_card("High Support", high_support)
    
    # Visualizations
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if 'Advisor' in filtered_df.columns:
            st.markdown("### 👥 WN Grades by Advisor")
            advisor_counts = filtered_df['Advisor'].value_counts().head(10)
            
            fig = px.bar(
                x=advisor_counts.values,
                y=advisor_counts.index,
                orientation='h',
                title="Top 10 Advisors by Student Count",
                color_discrete_sequence=['#2E3192']
            )
            fig.update_layout(
                font=dict(family='Work Sans'),
                title_font=dict(family='Spectral', size=16),
                xaxis_title="Number of Students",
                yaxis_title=""
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        if 'Support Level' in filtered_df.columns:
            st.markdown("### 📊 WN by Support Level")
            level_counts = filtered_df['Support Level'].value_counts()
            
            fig = px.pie(
                values=level_counts.values,
                names=level_counts.index,
                title="Student Distribution by Support Level",
                color_discrete_sequence=['#2E3192', '#1BFFFF', '#FFD93D']
            )
            fig.update_layout(
                font=dict(family='Work Sans'),
                title_font=dict(family='Spectral', size=16)
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Data table
    st.markdown("---")
    
    # Show key columns first
    display_cols = ['EMPLID', 'First Name', 'Last Name', 'Advisor', 'Cohort', 'Support Level', 'Subject Info']
    available_cols = [col for col in display_cols if col in filtered_df.columns]
    
    display_data_table(
        filtered_df[available_cols],
        f"📊 Student Details ({len(filtered_df)} records)",
        f"wn_grades_{datetime.now().strftime('%Y%m%d')}.csv"
    )

# ========== MAIN APP ==========
def main():
    """Main application"""
    render_sidebar()
    
    # Route to appropriate page
    page = st.session_state.get('current_page', 'overview')
    
    if page == 'overview':
        page_overview()
    elif page == 'benchmark':
        page_benchmark()
    elif page == 'fafsa':
        page_fafsa()
    elif page == 'errors':
        page_errors()
    elif page == 'wn_grades':
        page_wn_grades()

if __name__ == "__main__":
    main()
