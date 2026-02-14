import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, date
# import database as db  # Disabled for now - to implement later
import requests
from io import BytesIO

# Google Sheet Configuration
GOOGLE_SHEET_ID = "1NLF3LTZbNybmSL8b7N3GSHwhfJD82Hxm-wkRiZooohk"

def get_google_sheet_url(sheet_id, sheet_name):
    """Generate URL to fetch Google Sheet as Excel"""
    # Use export URL for xlsx format
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx"

def fetch_google_sheet(sheet_id):
    """Fetch Google Sheet data directly"""
    url = get_google_sheet_url(sheet_id, None)
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        raise Exception(f"Failed to fetch Google Sheet: {str(e)}")

# Page configuration
st.set_page_config(
    page_title="Blue Star Investments - KPI Dashboard",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for light theme
st.markdown("""
<style>
    /* Force light theme */
    .stApp {
        background-color: #ffffff !important;
    }
    .main .block-container {
        background-color: #ffffff !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #f8f9fa !important;
    }
    section[data-testid="stSidebar"] * {
        color: #333333 !important;
    }
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-top: 0;
    }
    /* All text should be dark */
    h1, h2, h3, h4, h5, h6, p, span, div, label {
        color: #333333 !important;
    }
    .stMarkdown {
        color: #333333 !important;
    }
    /* Fix metric label visibility */
    [data-testid="stMetricLabel"] {
        color: #333333 !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stMetricLabel"] p {
        color: #333333 !important;
        font-weight: 600 !important;
    }
    [data-testid="stMetricValue"] {
        color: #1E3A5F !important;
        font-weight: 700 !important;
    }
    /* Style metric containers */
    [data-testid="metric-container"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Hierarchy mapping
HIERARCHY = {
    "North": {
        "Dakotasota": ["Bemidji, MN", "Grand Forks, ND", "Grand Rapids, MN", "Hibbing, MN", "Jamestown, ND", "Virginia, MN"],
        "Duluth": ["Cloquet, MN", "Duluth, MN (Superior St)", "Duluth, MN (West)", "Hermantown, MN", "Superior, WI"],
        "Mid-Atlantic": ["Ashland, VA", "Chester, VA", "Clinton, MD", "Lovingston, VA", "Mechanicsville, VA", "Palmyra, VA", "Richmond, VA (Forest Hill Ave)", "Shrewsbury, PA", "Sparks, MD", "Timonium, MD", "Windsor, VA"],
        "Nebraska": ["Columbus, NE", "Fremont, NE", "Grand Island, NE", "Kearney, NE", "Lincoln, NE (N. 26th)", "Lincoln, NE (27th St)", "Lincoln, NE (Pioneer Woods)"],
        "Sioux Falls": ["Harrisburg, SD", "Sioux Falls, SD (41st)", "Sioux Falls, SD (Louise)", "Sioux Falls, SD (Sycamore)", "Tea, SD"],
        "Southern Minnesota": ["Faribault, MN", "Mankato, MN (Madison)", "Mankato, MN (St. Andrews)", "New Ulm, MN", "Owatonna, MN", "Rochester, MN (37th)"]
    },
    "South Central": {
        "Acadiana": ["Breaux Bridge, LA", "Broussard, LA", "Crowley, LA", "Lafayette, LA (Ambassador)", "Lafayette, LA (Johnston)", "New Iberia, LA", "Opelousas, LA", "Scott, LA", "Youngsville, LA"],
        "East LA": ["Baton Rouge, LA (Coursey)", "Baton Rouge, LA (O'Neal)", "Baton Rouge, LA (Sherwood)", "Denham Springs, LA", "Gonzales, LA", "Hammond, LA", "Prairieville, LA", "Walker, LA"],
        "Kansas City": ["Excelsior Springs, MO", "Independence, MO (Noland)", "Kansas City, MO (Barry)", "Kearney, MO", "Lee's Summit, MO (3rd)", "Liberty, MO"]
    },
    "South East": {
        "East Florida": ["Jacksonville, FL (Baymeadows)", "Jacksonville, FL (Regency)", "Middleburg, FL", "Orange Park, FL", "St Augustine, FL"],
        "Georgia": ["Albany, GA", "Americus, GA", "Cordele, GA", "Moultrie, GA", "Thomasville, GA"],
        "West Florida": ["Bradenton, FL", "Brandon, FL", "Gibsonton, FL", "Largo, FL", "Palmetto, FL", "Riverview, FL", "Sarasota, FL", "Sun City, FL"]
    }
}

def load_data(file_path, sheet_name):
    """Load and parse the Excel data into structured format"""
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)

    # Column index mapping based on actual spreadsheet structure
    COL_MAP = {
        0: 'Entity',
        1: 'Member Net',
        2: 'Lead to Member %',
        3: 'Lead Booked %',
        4: 'Appt Show %',
        5: 'Appt Close %',
        6: 'OB Phone Calls/Day',
        7: 'Downpayment (w/o Sales Tax)',
        8: 'FC Booking %',
        9: 'Show %',
        10: 'Close %',
        11: 'Avg Deal',
        12: 'Avg FCs/Day',
        13: 'Downpayments',
        14: 'Downpayment %',
        15: 'TAV',
        16: 'Revenue',
        17: 'Remaining Draft',
        18: 'Projected Revenue',
        19: 'OB Phone Calls',
        20: 'New Leads',
        21: 'Appt Scheduled',
        22: 'Appt Show Count',
        23: 'Total Tours',
        24: 'Walk-Ins',
        25: 'New Members',
        26: 'Downpayment Amount',
        27: 'Square DPs',
        28: 'FCs Booked @ POS',
        29: 'FCs Made',
        30: 'FCs Scheduled',
        31: 'FCs Shows',
        32: 'FCs Closes',
        33: 'New Deals',
        34: 'Sales Tax',
        35: 'Locations'
    }

    def row_to_dict(row_idx):
        """Convert a row to a dictionary using column mapping"""
        result = {}
        for col_idx, col_name in COL_MAP.items():
            try:
                val = df.iloc[row_idx, col_idx]
                if pd.notna(val):
                    result[col_name] = val
            except:
                pass
        return result

    # Parse data
    data = {
        'company': None,
        'territories': {},
        'regions': {},
        'clubs': {}
    }

    # Get update timestamp
    update_time = str(df.iloc[0, 0]) if pd.notna(df.iloc[0, 0]) else "Unknown"

    # Row indices for different levels
    company_row = 2
    territory_rows = [5, 6, 7]  # North, South Central, South East

    # Parse company level
    data['company'] = row_to_dict(company_row)

    # Parse territories
    for row_idx in territory_rows:
        row_data = row_to_dict(row_idx)
        territory_name = row_data.get('Entity')
        if territory_name:
            data['territories'][territory_name] = row_data

    # Parse regions (rows 10-21)
    for row_idx in range(10, 22):
        row_data = row_to_dict(row_idx)
        region_name = row_data.get('Entity')
        if region_name:
            data['regions'][region_name] = row_data

    # Parse clubs - find all club sections
    current_region = None
    for row_idx in range(23, len(df)):
        entity_name = df.iloc[row_idx, 0]
        col1_value = df.iloc[row_idx, 1]

        if pd.isna(entity_name):
            continue

        # Check if this is a region header
        if col1_value == 'Member Net':
            current_region = entity_name
            continue

        # This is a club row
        if current_region and pd.notna(col1_value):
            club_data = row_to_dict(row_idx)
            club_data['Region'] = current_region
            # Find territory for this region
            for territory, regions in HIERARCHY.items():
                if current_region in regions:
                    club_data['Territory'] = territory
                    break
            data['clubs'][entity_name] = club_data

    return data, update_time

def format_currency(value):
    """Format value as currency"""
    if pd.isna(value) or value == '$ -':
        return "$0"
    try:
        return f"${float(value):,.2f}"
    except:
        return str(value)

def format_percent(value):
    """Format value as percentage"""
    if pd.isna(value):
        return "0%"
    try:
        return f"{float(value)*100:.1f}%"
    except:
        return str(value)

def format_number(value):
    """Format value as number"""
    if pd.isna(value):
        return "0"
    try:
        return f"{float(value):,.0f}"
    except:
        return str(value)

def safe_float(val):
    """Safely convert value to float"""
    try:
        return float(val) if pd.notna(val) else 0
    except:
        return 0

def display_metric_card(label, value, prefix="", suffix=""):
    """Display a metric with guaranteed visible label - light theme"""
    st.markdown(f"""
    <div style="background-color: #ffffff;
                padding: 15px;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                height: 100%;">
        <p style="color: #666666; font-size: 0.75rem; margin: 0 0 8px 0; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600;">{label}</p>
        <p style="color: #1E3A5F; font-size: 1.5rem; font-weight: 700; margin: 0;">{prefix}{value}{suffix}</p>
    </div>
    """, unsafe_allow_html=True)

# Modern color palette
COLORS = {
    'primary': '#0066CC',
    'secondary': '#00A3E0',
    'accent': '#34C759',
    'neutral': '#8E8E93',
    'light_bg': '#F5F5F7',
    'dark_text': '#1D1D1F',
    'positive': '#34C759',
    'negative': '#FF3B30',
}

# Clean gradient for bar charts
CHART_COLORS = ['#0066CC', '#00A3E0', '#5AC8FA', '#34C759', '#30D158']

def create_gauge_chart(value, title, max_val=1, color_scale=None):
    """Create a clean, modern gauge chart"""
    pct_value = value * 100 if value <= 1 else value

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=pct_value,
        title={'text': title, 'font': {'size': 13, 'color': '#666666'}},
        number={'suffix': '%', 'font': {'size': 28, 'color': '#1D1D1F', 'family': 'SF Pro Display, -apple-system, sans-serif'}},
        gauge={
            'axis': {'range': [0, 100], 'ticksuffix': '%', 'tickcolor': '#E5E5E5', 'tickwidth': 1},
            'bar': {'color': '#0066CC', 'thickness': 0.7},
            'bgcolor': '#F5F5F7',
            'borderwidth': 0,
            'steps': [
                {'range': [0, 100], 'color': '#F5F5F7'}
            ],
        }
    ))
    fig.update_layout(
        height=180,
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font={'family': 'SF Pro Display, -apple-system, sans-serif'}
    )
    return fig

def main():
    # Sidebar
    st.sidebar.image("https://images.squarespace-cdn.com/content/v1/63b4569f7fef3c5cee7bf1c4/b1325ffc-6798-46be-92ac-947cef1f7e12/BlueStar+Logo.png", width=200)
    st.sidebar.markdown("### KPI Dashboard")
    st.sidebar.markdown("---")

    # Data source - Live Google Sheet
    st.sidebar.markdown("**📂 Data Source**")

    file_path = None
    source_name = ""

    # Fetch from Google Sheets
    try:
        with st.sidebar.status("Fetching live data...", expanded=False) as status:
            file_path = fetch_google_sheet(GOOGLE_SHEET_ID)
            status.update(label="✓ Connected to Google Sheet", state="complete")
        source_name = "Live Google Sheet"
    except Exception as e:
        st.sidebar.error(f"Could not connect to Google Sheet.")
        st.sidebar.markdown("**Troubleshooting:**")
        st.sidebar.markdown("1. Open Google Sheet")
        st.sidebar.markdown("2. Click Share → Anyone with link → Viewer")
        st.error("Unable to connect to Google Sheet. Please check sharing settings.")
        return

    # File upload function kept for future use but hidden from UI
    # def load_from_upload():
    #     uploaded_file = st.sidebar.file_uploader("Upload Daily KPI Scorecard", type=['xlsx'])
    #     if uploaded_file:
    #         return uploaded_file, uploaded_file.name
    #     return None, None

    if file_path is None:
        st.error("No data source available.")
        return

    st.sidebar.caption(f"🌐 {source_name}")

    # Load available sheets
    try:
        xl = pd.ExcelFile(file_path)
        month_sheets = [s for s in xl.sheet_names if s not in ['Tracker Directory', 'Sources']]
        selected_month = st.sidebar.selectbox("Select Month", month_sheets)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return

    st.sidebar.markdown("---")

    # Load data with caching for better performance
    @st.cache_data(ttl=300)  # Cache for 5 minutes
    def load_cached_data(file_content, sheet_name):
        return load_data(file_content, sheet_name)

    # Load data
    try:
        data, update_time = load_data(file_path, selected_month)
    except Exception as e:
        st.error(f"Error parsing data: {e}")
        return

    st.sidebar.markdown("---")

    # View level selection
    view_level = st.sidebar.radio(
        "Dashboard Level",
        ["Company", "Territory", "Region", "Club"],
        index=0
    )

    # Dynamic filters based on view level
    selected_territory = None
    selected_region = None
    selected_club = None

    if view_level in ["Territory", "Region", "Club"]:
        selected_territory = st.sidebar.selectbox(
            "Select Territory",
            list(HIERARCHY.keys())
        )

    if view_level in ["Region", "Club"] and selected_territory:
        selected_region = st.sidebar.selectbox(
            "Select Region",
            list(HIERARCHY[selected_territory].keys())
        )

    if view_level == "Club" and selected_region:
        clubs_in_region = [c for c, d in data['clubs'].items() if d.get('Region') == selected_region]
        selected_club = st.sidebar.selectbox(
            "Select Club",
            clubs_in_region
        )

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Last Updated:** {update_time}")

    # Database section - DISABLED FOR NOW (to implement later)
    # Code preserved in database.py for future implementation

    st.sidebar.markdown("---")

    # Auto-refresh option for live data
    auto_refresh = st.sidebar.checkbox("Auto-refresh (5 min)", value=False, help="Automatically refresh data every 5 minutes")
    if auto_refresh:
        import time
        st.sidebar.caption("⏱️ Auto-refresh enabled")
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = time.time()
        if time.time() - st.session_state.last_refresh > 300:  # 5 minutes
            st.session_state.last_refresh = time.time()
            st.cache_data.clear()
            st.rerun()

    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    # Main content
    st.markdown('<h1 class="main-header">Blue Star Investments</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Anytime Fitness Franchise KPI Dashboard</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Determine which data to display
    if view_level == "Company":
        display_data = data['company']
        title = "Company Overview"
        subtitle = f"All Locations ({format_number(display_data.get('Locations', 81))} clubs)"
    elif view_level == "Territory":
        display_data = data['territories'].get(selected_territory, {})
        title = f"Territory: {selected_territory}"
        subtitle = f"{format_number(display_data.get('Locations', 0))} clubs"
    elif view_level == "Region":
        display_data = data['regions'].get(selected_region, {})
        title = f"Region: {selected_region}"
        subtitle = f"{selected_territory} Territory"
    else:  # Club
        display_data = data['clubs'].get(selected_club, {})
        title = f"Club: {selected_club}"
        subtitle = f"{selected_region} Region | {selected_territory} Territory"

    st.markdown(f"### {title}")
    st.markdown(f"*{subtitle}*")
    st.markdown("")

    # KPI Metrics Row 1 - Membership
    st.markdown("#### 📊 Membership Metrics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    member_net = display_data.get('Member Net', 0)
    new_members = display_data.get('New Members', 0)
    new_leads = display_data.get('New Leads', 0)
    walk_ins = display_data.get('Walk-Ins', 0)
    total_tours = display_data.get('Total Tours', 0)
    appt_scheduled = display_data.get('Appt Scheduled', 0)

    with col1:
        mn = safe_float(member_net)
        display_metric_card("Member Net", format_number(mn))

    with col2:
        display_metric_card("New Members", format_number(safe_float(new_members)))

    with col3:
        display_metric_card("New Leads", format_number(safe_float(new_leads)))

    with col4:
        display_metric_card("Walk-Ins", format_number(safe_float(walk_ins)))

    with col5:
        display_metric_card("Total Tours", format_number(safe_float(total_tours)))

    with col6:
        display_metric_card("Appts Scheduled", format_number(safe_float(appt_scheduled)))

    st.markdown("")

    # KPI Metrics Row 2 - Revenue
    st.markdown("#### 💰 Financial Metrics")
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    revenue = display_data.get('Revenue', 0)
    projected_rev = display_data.get('Projected Revenue', 0)
    remaining_draft = display_data.get('Remaining Draft', 0)
    tav = display_data.get('TAV', 0)
    downpayment = display_data.get('Downpayment (w/o Sales Tax)', 0)
    avg_deal = display_data.get('Avg Deal', 0)

    with col1:
        display_metric_card("Revenue (MTD)", f"{safe_float(revenue):,.2f}", prefix="$")

    with col2:
        display_metric_card("Projected Revenue", f"{safe_float(projected_rev):,.2f}", prefix="$")

    with col3:
        display_metric_card("Remaining Draft", f"{safe_float(remaining_draft):,.2f}", prefix="$")

    with col4:
        display_metric_card("TAV", f"{safe_float(tav):,.2f}", prefix="$")

    with col5:
        display_metric_card("Downpayments", f"{safe_float(downpayment):,.2f}", prefix="$")

    with col6:
        display_metric_card("Avg Deal Size", f"{safe_float(avg_deal):,.2f}", prefix="$")

    st.markdown("")

    # Top 5 PT Projected Revenue (only show at Company, Territory, Region levels)
    if view_level != "Club":
        st.markdown("#### 💪 Top 5 PT Projected Revenue")

        # Filter clubs based on current view level
        if view_level == "Company":
            filtered_clubs = data['clubs']
            top_title = "Top 5 PT Projected Revenue - Company Wide"
        elif view_level == "Territory":
            filtered_clubs = {k: v for k, v in data['clubs'].items() if v.get('Territory') == selected_territory}
            top_title = f"Top 5 PT Projected Revenue - {selected_territory}"
        else:  # Region
            filtered_clubs = {k: v for k, v in data['clubs'].items() if v.get('Region') == selected_region}
            top_title = f"Top 5 PT Projected Revenue - {selected_region}"

        # Build ranking data
        ranking_data = []
        for club_name, metrics in filtered_clubs.items():
            pt_proj_rev = safe_float(metrics.get('Projected Revenue', 0))
            pt_revenue = safe_float(metrics.get('Revenue', 0))
            avg_deal = safe_float(metrics.get('Avg Deal', 0))
            fc_closes = safe_float(metrics.get('FCs Closes', 0))
            region = metrics.get('Region', '')
            territory = metrics.get('Territory', '')
            ranking_data.append({
                'Club': club_name,
                'Region': region,
                'Territory': territory,
                'PT Projected Revenue': pt_proj_rev,
                'PT Revenue (MTD)': pt_revenue,
                'Avg Deal': avg_deal,
                'FC Closes': fc_closes
            })

        if ranking_data:
            df_ranking = pd.DataFrame(ranking_data)
            df_ranking = df_ranking.sort_values('PT Projected Revenue', ascending=False).head(5)

            col1, col2 = st.columns([2, 1])

            with col1:
                # Bar chart of top PT revenue locations
                fig = go.Figure(go.Bar(
                    x=df_ranking['PT Projected Revenue'],
                    y=df_ranking['Club'],
                    orientation='h',
                    marker_color='#34C759',
                    text=df_ranking['PT Projected Revenue'].apply(lambda x: f"${x:,.0f}"),
                    textposition='outside',
                    textfont={'size': 11, 'color': '#666666'}
                ))
                fig.update_layout(
                    title={'text': top_title, 'font': {'size': 14, 'color': '#333333'}},
                    height=280,
                    margin=dict(l=10, r=100, t=40, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis={'gridcolor': '#F0F0F0', 'tickprefix': '$', 'tickformat': ','},
                    yaxis={'gridcolor': '#F0F0F0', 'categoryorder': 'total ascending'}
                )
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                # Summary table
                st.markdown(f"**{top_title}**")
                df_display = df_ranking[['Club', 'PT Projected Revenue', 'PT Revenue (MTD)', 'Avg Deal']].copy()
                df_display['PT Projected Revenue'] = df_display['PT Projected Revenue'].apply(lambda x: f"${x:,.0f}")
                df_display['PT Revenue (MTD)'] = df_display['PT Revenue (MTD)'].apply(lambda x: f"${x:,.0f}")
                df_display['Avg Deal'] = df_display['Avg Deal'].apply(lambda x: f"${x:,.0f}")
                df_display = df_display.reset_index(drop=True)
                df_display.index = df_display.index + 1  # Start ranking at 1
                df_display.index.name = 'Rank'
                st.dataframe(df_display, use_container_width=True)

        st.markdown("")

    # Conversion Funnel
    st.markdown("#### 🎯 Sales Funnel Performance")

    lead_to_member = display_data.get('Lead to Member %', 0)
    lead_booked = display_data.get('Lead Booked %', 0)
    appt_show = display_data.get('Appt Show %', 0)
    appt_close = display_data.get('Appt Close %', 0)
    fc_booking = display_data.get('FC Booking %', 0)
    show_pct = display_data.get('Show %', 0)
    close_pct = display_data.get('Close %', 0)

    # Row 1: Main conversion gauges
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        try:
            val = float(lead_to_member) if pd.notna(lead_to_member) else 0
            fig = create_gauge_chart(val, "Lead → Member")
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.metric("Lead to Member %", format_percent(lead_to_member))

    with col2:
        try:
            val = float(lead_booked) if pd.notna(lead_booked) else 0
            fig = create_gauge_chart(val, "Lead → Booked")
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.metric("Lead Booked %", format_percent(lead_booked))

    with col3:
        try:
            val = float(appt_show) if pd.notna(appt_show) else 0
            fig = create_gauge_chart(val, "Appt Show Rate")
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.metric("Appt Show %", format_percent(appt_show))

    with col4:
        try:
            val = float(appt_close) if pd.notna(appt_close) else 0
            fig = create_gauge_chart(val, "Appt Close Rate")
            st.plotly_chart(fig, use_container_width=True)
        except:
            st.metric("Appt Close %", format_percent(appt_close))

    # Visual Funnel Chart - Clean modern design
    st.markdown("##### Sales Funnel")
    col1, col2 = st.columns([3, 2])

    with col1:
        # Create funnel data
        new_leads_val = safe_float(new_leads)
        appt_sched_val = safe_float(appt_scheduled)
        tours_val = safe_float(total_tours)
        new_members_val = safe_float(new_members)

        # Calculate conversion rates for display
        funnel_stages = ['New Leads', 'Appts Scheduled', 'Total Tours', 'New Members']
        funnel_values = [new_leads_val, appt_sched_val, tours_val, new_members_val]

        fig_funnel = go.Figure(go.Funnel(
            y=funnel_stages,
            x=funnel_values,
            textposition="inside",
            textinfo="value+percent initial",
            textfont={'size': 14, 'color': 'white', 'family': 'SF Pro Display, -apple-system, sans-serif'},
            marker=dict(
                color=['#0066CC', '#00A3E0', '#5AC8FA', '#34C759'],
                line={'width': 0}
            ),
            connector={'line': {'color': '#E5E5E5', 'width': 1}},
            opacity=0.9
        ))
        fig_funnel.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'family': 'SF Pro Display, -apple-system, sans-serif'}
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

    with col2:
        # FC Metrics in a cleaner layout
        st.markdown("**Fitness Consultation**")
        fc_metrics = [
            ("FC Booking %", fc_booking, True),
            ("FC Show %", show_pct, True),
            ("FC Close %", close_pct, True),
            ("Avg FCs/Day", display_data.get('Avg FCs/Day', 0), False)
        ]
        for label, val, is_pct in fc_metrics:
            if is_pct:
                display_val = f"{safe_float(val)*100:.1f}"
                display_metric_card(label, display_val, suffix="%")
            else:
                display_val = f"{safe_float(val):.2f}"
                display_metric_card(label, display_val)
            st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

    # Activity Metrics
    st.markdown("#### 📞 Activity Metrics")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        ob_calls = display_data.get('OB Phone Calls', 0)
        display_metric_card("OB Phone Calls (Total)", format_number(safe_float(ob_calls)))

    with col2:
        ob_calls_day = display_data.get('OB Phone Calls/Day', 0)
        display_metric_card("OB Calls/Day", f"{safe_float(ob_calls_day):.1f}")

    with col3:
        fcs_made = display_data.get('FCs Made', 0)
        display_metric_card("FCs Made", format_number(safe_float(fcs_made)))

    with col4:
        new_deals = display_data.get('New Deals', 0)
        display_metric_card("New Deals", format_number(safe_float(new_deals)))

    st.markdown("")

    # Comparison Charts (only show at Company/Territory/Region level)
    if view_level != "Club":
        st.markdown("---")
        st.markdown("#### 📈 Performance Comparison")

        if view_level == "Company":
            # Compare territories
            compare_data = data['territories']
            compare_title = "Territory"
            level_name = "Territories"
        elif view_level == "Territory":
            # Compare regions in this territory
            compare_data = {k: v for k, v in data['regions'].items()
                          if k in HIERARCHY.get(selected_territory, {})}
            compare_title = "Region"
            level_name = f"Regions in {selected_territory}"
        else:  # Region
            # Compare clubs in this region
            compare_data = {k: v for k, v in data['clubs'].items()
                          if v.get('Region') == selected_region}
            compare_title = "Club"
            level_name = f"Clubs in {selected_region}"

        if compare_data:
            # Build comprehensive comparison dataframe
            comparison_rows = []
            for name, metrics in compare_data.items():
                try:
                    row = {
                        'Entity': name,
                        'Revenue': float(metrics.get('Revenue', 0)) if pd.notna(metrics.get('Revenue')) else 0,
                        'Projected Revenue': float(metrics.get('Projected Revenue', 0)) if pd.notna(metrics.get('Projected Revenue')) else 0,
                        'New Members': float(metrics.get('New Members', 0)) if pd.notna(metrics.get('New Members')) else 0,
                        'Member Net': float(metrics.get('Member Net', 0)) if pd.notna(metrics.get('Member Net')) else 0,
                        'New Leads': float(metrics.get('New Leads', 0)) if pd.notna(metrics.get('New Leads')) else 0,
                        'Lead to Member %': float(metrics.get('Lead to Member %', 0)) * 100 if pd.notna(metrics.get('Lead to Member %')) else 0,
                        'Appt Show %': float(metrics.get('Appt Show %', 0)) * 100 if pd.notna(metrics.get('Appt Show %')) else 0,
                        'Appt Close %': float(metrics.get('Appt Close %', 0)) * 100 if pd.notna(metrics.get('Appt Close %')) else 0,
                        'OB Calls/Day': float(metrics.get('OB Phone Calls/Day', 0)) if pd.notna(metrics.get('OB Phone Calls/Day')) else 0,
                        'Avg Deal': float(metrics.get('Avg Deal', 0)) if pd.notna(metrics.get('Avg Deal')) else 0,
                        'TAV': float(metrics.get('TAV', 0)) if pd.notna(metrics.get('TAV')) else 0,
                    }
                    comparison_rows.append(row)
                except Exception as e:
                    pass

            if comparison_rows:
                df_compare = pd.DataFrame(comparison_rows)

                # Row 1: Revenue and Members side by side
                st.markdown(f"##### Financial Performance by {compare_title}")
                col1, col2 = st.columns(2)

                with col1:
                    df_sorted = df_compare.sort_values('Revenue', ascending=True)
                    fig = go.Figure(go.Bar(
                        x=df_sorted['Revenue'],
                        y=df_sorted['Entity'],
                        orientation='h',
                        marker_color='#0066CC',
                        text=df_sorted['Revenue'].apply(lambda x: f"${x:,.0f}"),
                        textposition='outside',
                        textfont={'size': 11, 'color': '#666666'}
                    ))
                    fig.update_layout(
                        title={'text': 'Revenue (MTD)', 'font': {'size': 14, 'color': '#333333'}},
                        height=max(280, len(df_compare) * 40),
                        margin=dict(l=10, r=80, t=40, b=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis={'tickprefix': '$', 'tickformat': ',', 'gridcolor': '#F0F0F0'},
                        yaxis={'gridcolor': '#F0F0F0'}
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    df_sorted = df_compare.sort_values('Projected Revenue', ascending=True)
                    fig = go.Figure(go.Bar(
                        x=df_sorted['Projected Revenue'],
                        y=df_sorted['Entity'],
                        orientation='h',
                        marker_color='#00A3E0',
                        text=df_sorted['Projected Revenue'].apply(lambda x: f"${x:,.0f}"),
                        textposition='outside',
                        textfont={'size': 11, 'color': '#666666'}
                    ))
                    fig.update_layout(
                        title={'text': 'Projected Revenue', 'font': {'size': 14, 'color': '#333333'}},
                        height=max(280, len(df_compare) * 40),
                        margin=dict(l=10, r=80, t=40, b=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis={'tickprefix': '$', 'tickformat': ',', 'gridcolor': '#F0F0F0'},
                        yaxis={'gridcolor': '#F0F0F0'}
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Row 2: Membership metrics
                st.markdown(f"##### Membership Performance by {compare_title}")
                col1, col2 = st.columns(2)

                with col1:
                    df_sorted = df_compare.sort_values('New Members', ascending=True)
                    fig = go.Figure(go.Bar(
                        x=df_sorted['New Members'],
                        y=df_sorted['Entity'],
                        orientation='h',
                        marker_color='#34C759',
                        text=df_sorted['New Members'].apply(lambda x: f"{x:.0f}"),
                        textposition='outside',
                        textfont={'size': 11, 'color': '#666666'}
                    ))
                    fig.update_layout(
                        title={'text': 'New Members', 'font': {'size': 14, 'color': '#333333'}},
                        height=max(280, len(df_compare) * 40),
                        margin=dict(l=10, r=60, t=40, b=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis={'gridcolor': '#F0F0F0'},
                        yaxis={'gridcolor': '#F0F0F0'}
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    # Member Net with positive/negative coloring
                    df_sorted = df_compare.sort_values('Member Net', ascending=True)
                    colors = ['#FF3B30' if x < 0 else '#34C759' for x in df_sorted['Member Net']]
                    fig = go.Figure(go.Bar(
                        x=df_sorted['Member Net'],
                        y=df_sorted['Entity'],
                        orientation='h',
                        marker_color=colors,
                        text=df_sorted['Member Net'].apply(lambda x: f"{x:+.0f}"),
                        textposition='outside',
                        textfont={'size': 11, 'color': '#666666'}
                    ))
                    fig.update_layout(
                        title={'text': 'Member Net (+/-)', 'font': {'size': 14, 'color': '#333333'}},
                        height=max(280, len(df_compare) * 40),
                        margin=dict(l=10, r=60, t=40, b=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis={'gridcolor': '#F0F0F0', 'zeroline': True, 'zerolinecolor': '#CCCCCC'},
                        yaxis={'gridcolor': '#F0F0F0'}
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Row 3: Lead generation
                st.markdown(f"##### Lead Generation by {compare_title}")
                col1, col2 = st.columns(2)

                with col1:
                    df_sorted = df_compare.sort_values('New Leads', ascending=True)
                    fig = go.Figure(go.Bar(
                        x=df_sorted['New Leads'],
                        y=df_sorted['Entity'],
                        orientation='h',
                        marker_color='#5AC8FA',
                        text=df_sorted['New Leads'].apply(lambda x: f"{x:.0f}"),
                        textposition='outside',
                        textfont={'size': 11, 'color': '#666666'}
                    ))
                    fig.update_layout(
                        title={'text': 'New Leads', 'font': {'size': 14, 'color': '#333333'}},
                        height=max(280, len(df_compare) * 40),
                        margin=dict(l=10, r=60, t=40, b=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis={'gridcolor': '#F0F0F0'},
                        yaxis={'gridcolor': '#F0F0F0'}
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    df_sorted = df_compare.sort_values('OB Calls/Day', ascending=True)
                    fig = go.Figure(go.Bar(
                        x=df_sorted['OB Calls/Day'],
                        y=df_sorted['Entity'],
                        orientation='h',
                        marker_color='#AF52DE',
                        text=df_sorted['OB Calls/Day'].apply(lambda x: f"{x:.1f}"),
                        textposition='outside',
                        textfont={'size': 11, 'color': '#666666'}
                    ))
                    fig.update_layout(
                        title={'text': 'OB Phone Calls/Day', 'font': {'size': 14, 'color': '#333333'}},
                        height=max(280, len(df_compare) * 40),
                        margin=dict(l=10, r=60, t=40, b=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        xaxis={'gridcolor': '#F0F0F0'},
                        yaxis={'gridcolor': '#F0F0F0'}
                    )
                    st.plotly_chart(fig, use_container_width=True)

                # Row 4: Conversion rates heatmap
                st.markdown(f"##### Conversion Rates by {compare_title}")

                conv_cols = ['Lead to Member %', 'Appt Show %', 'Appt Close %']
                df_heatmap = df_compare[['Entity'] + conv_cols].set_index('Entity')

                # Clean blue color scale for heatmap
                fig = px.imshow(df_heatmap,
                               labels=dict(x="Metric", y=compare_title, color="Rate %"),
                               color_continuous_scale=[[0, '#E8F4FD'], [0.5, '#5AC8FA'], [1, '#0066CC']],
                               aspect="auto",
                               text_auto='.1f')
                fig.update_layout(
                    title={'text': f'Conversion Rate Heatmap', 'font': {'size': 14, 'color': '#333333'}},
                    height=max(280, len(df_compare) * 35),
                    margin=dict(l=10, r=20, t=40, b=20),
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'family': 'SF Pro Display, -apple-system, sans-serif'}
                )
                fig.update_traces(textfont={'size': 12, 'color': '#333333'})
                st.plotly_chart(fig, use_container_width=True)

                # Row 5: Grouped bar chart for conversion rates
                df_melted = df_compare[['Entity'] + conv_cols].melt(
                    id_vars=['Entity'], var_name='Metric', value_name='Percentage'
                )

                fig = px.bar(df_melted, x='Entity', y='Percentage', color='Metric',
                            barmode='group',
                            color_discrete_sequence=['#0066CC', '#00A3E0', '#5AC8FA'])
                fig.update_layout(
                    title={'text': 'Conversion Rates Comparison', 'font': {'size': 14, 'color': '#333333'}},
                    height=380,
                    xaxis_tickangle=-45,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                               bgcolor='rgba(0,0,0,0)', font={'size': 11}),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis={'gridcolor': '#F0F0F0'},
                    yaxis={'gridcolor': '#F0F0F0', 'ticksuffix': '%', 'title': 'Conversion Rate (%)'}
                )
                st.plotly_chart(fig, use_container_width=True)

                # Row 6: Scatter plot - Revenue vs Members
                st.markdown(f"##### Revenue vs New Members Analysis")
                fig = px.scatter(df_compare, x='New Members', y='Revenue',
                               size='TAV', color='Lead to Member %',
                               hover_name='Entity',
                               color_continuous_scale=[[0, '#E8F4FD'], [0.5, '#5AC8FA'], [1, '#0066CC']],
                               labels={'Lead to Member %': 'Lead→Member %'})
                fig.update_layout(
                    title={'text': 'Revenue vs New Members (bubble size = TAV)', 'font': {'size': 14, 'color': '#333333'}},
                    height=420,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    xaxis={'gridcolor': '#F0F0F0'},
                    yaxis={'gridcolor': '#F0F0F0', 'tickprefix': '$', 'tickformat': ','}
                )
                fig.update_traces(marker={'line': {'width': 1, 'color': 'white'}})
                st.plotly_chart(fig, use_container_width=True)

                # Summary Table
                st.markdown(f"##### {level_name} - Summary Table")
                df_display = df_compare.copy()
                df_display['Revenue'] = df_display['Revenue'].apply(lambda x: f"${x:,.0f}")
                df_display['Projected Revenue'] = df_display['Projected Revenue'].apply(lambda x: f"${x:,.0f}")
                df_display['TAV'] = df_display['TAV'].apply(lambda x: f"${x:,.0f}")
                df_display['Avg Deal'] = df_display['Avg Deal'].apply(lambda x: f"${x:,.0f}")
                df_display['Lead to Member %'] = df_display['Lead to Member %'].apply(lambda x: f"{x:.1f}%")
                df_display['Appt Show %'] = df_display['Appt Show %'].apply(lambda x: f"{x:.1f}%")
                df_display['Appt Close %'] = df_display['Appt Close %'].apply(lambda x: f"{x:.1f}%")
                df_display['Member Net'] = df_display['Member Net'].apply(lambda x: f"{x:+.0f}")

                st.dataframe(df_display, use_container_width=True, hide_index=True)

    # Detailed Data Table
    st.markdown("---")
    st.markdown("#### Detailed Metrics")

    # Create a cleaner table view
    metrics_to_show = [
        ('Member Net', 'number'),
        ('New Members', 'number'),
        ('New Leads', 'number'),
        ('Walk-Ins', 'number'),
        ('Total Tours', 'number'),
        ('Lead to Member %', 'percent'),
        ('Lead Booked %', 'percent'),
        ('Appt Show %', 'percent'),
        ('Appt Close %', 'percent'),
        ('Revenue', 'currency'),
        ('Projected Revenue', 'currency'),
        ('TAV', 'currency'),
        ('Downpayment (w/o Sales Tax)', 'currency'),
        ('OB Phone Calls/Day', 'number'),
        ('Avg Deal', 'currency'),
        ('FCs Booking %', 'percent')
    ]

    table_data = []
    for metric, fmt in metrics_to_show:
        value = display_data.get(metric, 0)
        if fmt == 'currency':
            formatted = format_currency(value)
        elif fmt == 'percent':
            formatted = format_percent(value)
        else:
            formatted = format_number(value)
        table_data.append({'Metric': metric, 'Value': formatted})

    df_table = pd.DataFrame(table_data)

    col1, col2 = st.columns(2)
    with col1:
        st.dataframe(df_table.iloc[:len(df_table)//2], use_container_width=True, hide_index=True)
    with col2:
        st.dataframe(df_table.iloc[len(df_table)//2:], use_container_width=True, hide_index=True)

    # Historical Trends Section - DISABLED FOR NOW (to implement later)
    # Code preserved in database.py for future implementation

    # Drill-down navigation
    st.markdown("---")
    if view_level == "Company":
        st.markdown("**Quick Navigation:** Select a territory in the sidebar to drill down")
        cols = st.columns(3)
        for i, territory in enumerate(HIERARCHY.keys()):
            with cols[i]:
                if st.button(f"View {territory}", key=f"nav_{territory}"):
                    st.session_state['view_level'] = 'Territory'
                    st.session_state['selected_territory'] = territory
                    st.rerun()

if __name__ == "__main__":
    main()
