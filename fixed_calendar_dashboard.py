"""
Mississippi WMA Draw Hunt Analysis Dashboard - FIXED VERSION
Interactive Streamlit application for hunt analysis and recommendations
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import calendar
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Mississippi WMA Hunt Analysis",
    page_icon="🦌",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_hunt_data():
    """Load all hunt data from CSV files."""
    try:
        hunt_files = {
            'Archery': 'data/deer_archery_hunts_2025_26.csv',
            'Gun': 'data/deer_gun_hunts_2025_26.csv',
            'Primitive Weapon': 'data/deer_primitive_weapon_hunts_2025_26.csv',
            'Group': 'data/deer_group_hunts_2025_26.csv'
        }
        
        all_hunts = []
        
        for hunt_type, file_path in hunt_files.items():
            try:
                df = pd.read_csv(file_path)
                df['hunt_method'] = hunt_type
                df['start_date'] = pd.to_datetime(df['start_date'])
                df['end_date'] = pd.to_datetime(df['end_date'])
                all_hunts.append(df)
            except Exception as e:
                st.error(f"Error loading {hunt_type} data: {e}")
                continue
        
        if all_hunts:
            combined_df = pd.concat(all_hunts, ignore_index=True)
            return combined_df
        else:
            st.error("No hunt data could be loaded!")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Critical error in data loading: {e}")
        return pd.DataFrame()

@st.cache_data
def calculate_enhanced_scores(df):
    """Calculate enhanced scores for hunts."""
    if df.empty:
        return df
    
    df = df.copy()
    
    # Rut periods
    def get_rut_score(date):
        if datetime(2025, 12, 29) <= date <= datetime(2026, 1, 4):
            return 5  # Peak Rut
        elif datetime(2025, 12, 16) <= date <= datetime(2025, 12, 28):
            return 4  # Pre-Peak Rut
        elif datetime(2025, 10, 1) <= date <= datetime(2025, 12, 15):
            return 3  # Pre-Rut
        elif datetime(2026, 1, 5) <= date <= datetime(2026, 1, 20):
            return 3  # Post-Rut
        else:
            return 2  # Late Season
    
    def get_moon_score(date):
        new_moons = [
            datetime(2025, 10, 21),
            datetime(2025, 11, 20),
            datetime(2025, 12, 19),
            datetime(2026, 1, 20)
        ]
        
        best_score = 0
        for moon_date in new_moons:
            days_diff = abs((date - moon_date).days)
            if days_diff <= 2:
                phase_score = 3
            elif days_diff <= 7:
                phase_score = 1.5
            else:
                phase_score = 0
            best_score = max(best_score, phase_score)
        return best_score
    
    # Calculate scores
    df['rut_score'] = df['start_date'].apply(get_rut_score)
    df['moon_score'] = df['start_date'].apply(get_moon_score)
    
    # Combined score
    df['permit_score'] = (df['permits_available'] / 5).clip(upper=5)
    df['duration_score'] = df['duration_days'].clip(upper=4)
    
    df['combined_score'] = (
        df['permit_score'] * 0.3 +
        df['duration_score'] * 0.2 +
        df['moon_score'] * 0.2 +
        df['rut_score'] * 0.3
    ).round(2)
    
    return df

def show_overview(filtered_df, full_df):
    """Show overview statistics."""
    st.header("📊 Hunt Inventory Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Hunts", len(full_df))
    
    with col2:
        st.metric("Total Permits", full_df['permits_available'].sum())
    
    with col3:
        st.metric("Unique Locations", full_df['wma_location'].nunique())
    
    with col4:
        avg_score = full_df['combined_score'].mean()
        st.metric("Avg Hunt Score", f"{avg_score:.2f}/5.0")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Hunts by method
        method_counts = full_df['hunt_method'].value_counts()
        fig1 = px.pie(
            values=method_counts.values,
            names=method_counts.index,
            title="Hunts by Method"
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Permits by location
        location_permits = full_df.groupby('wma_location')['permits_available'].sum().sort_values(ascending=False)
        fig2 = px.bar(
            x=location_permits.values,
            y=location_permits.index,
            orientation='h',
            title="Total Permits by Location"
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

def show_recommendations(filtered_df):
    """Show top hunt recommendations."""
    st.header("🏆 Top Hunt Recommendations")
    
    if filtered_df.empty:
        st.warning("No hunts match current filters.")
        return
    
    # Top 10 hunts by score
    top_hunts = filtered_df.nlargest(10, 'combined_score')
    
    st.subheader("🥇 Top 10 Highest Scoring Hunts")
    
    for idx, hunt in top_hunts.iterrows():
        with st.expander(f"#{top_hunts.index.get_loc(idx)+1} - {hunt['hunt_name']} (Score: {hunt['combined_score']})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write("**Hunt Details:**")
                st.write(f"• Method: {hunt['hunt_method']}")
                st.write(f"• Location: {hunt['wma_location']}")
                st.write(f"• Date: {hunt['start_date'].strftime('%m/%d/%Y')} - {hunt['end_date'].strftime('%m/%d/%Y')}")
                st.write(f"• Duration: {hunt['duration_days']} days")
            
            with col2:
                st.write("**Permits & Scoring:**")
                st.write(f"• Permits: {hunt['permits_available']}")
                st.write(f"• Combined Score: {hunt['combined_score']}/5.0")
                st.write(f"• Rut Score: {hunt['rut_score']}/5")
                st.write(f"• Moon Score: {hunt['moon_score']:.1f}/3")
            
            with col3:
                st.write("**Competition Level:**")
                if hunt['combined_score'] >= 4.0:
                    st.error("🔥 Very High Competition")
                elif hunt['combined_score'] >= 3.5:
                    st.warning("⚠️ High Competition")
                elif hunt['combined_score'] >= 3.0:
                    st.info("ℹ️ Moderate Competition")
                else:
                    st.success("✅ Lower Competition")
                
                # Special notes
                if hunt['rut_score'] >= 5:
                    st.success("🦌 PEAK RUT PERIOD")
                elif hunt['rut_score'] >= 4:
                    st.info("🎯 Pre-Peak Rut")

def show_calendar_view(filtered_df):
    """Show hunt calendar view."""
    st.header("📅 Hunt Calendar View")
    
    if filtered_df.empty:
        st.warning("No hunts match current filters.")
        return
    
    # Calendar view options
    view_type = st.radio(
        "Calendar View Type:",
        options=["📅 Monthly Calendar", "📈 Timeline View", "📊 Gantt Chart"],
        index=0,
        horizontal=True
    )
    
    if "Monthly Calendar" in view_type:
        show_monthly_calendar(filtered_df)
    elif "Timeline View" in view_type:
        show_timeline_view(filtered_df)
    else:
        show_gantt_chart(filtered_df)

def show_monthly_calendar(df):
    """Show monthly calendar grid with hunts."""
    st.subheader("📅 Monthly Calendar View")
    
    # Month selector
    available_months = []
    for _, hunt in df.iterrows():
        start_month = hunt['start_date'].strftime('%Y-%m')
        end_month = hunt['end_date'].strftime('%Y-%m')
        available_months.extend([start_month, end_month])
    
    unique_months = sorted(list(set(available_months)))
    if not unique_months:
        st.info("No hunts available for calendar view.")
        return
    
    month_options = [datetime.strptime(m, '%Y-%m').strftime('%B %Y') for m in unique_months]
    
    selected_month_display = st.selectbox(
        "Select Month to View:",
        options=month_options,
        index=0
    )
    
    selected_month = datetime.strptime(selected_month_display, '%B %Y').strftime('%Y-%m')
    
    # Filter hunts for selected month
    month_start = datetime.strptime(selected_month, '%Y-%m')
    month_end = month_start.replace(day=calendar.monthrange(month_start.year, month_start.month)[1])
    
    month_hunts = df[
        (df['start_date'] <= month_end) & 
        (df['end_date'] >= month_start)
    ].copy()
    
    if month_hunts.empty:
        st.info(f"No hunts scheduled for {selected_month_display}")
        return
    
    st.write(f"**{len(month_hunts)} hunts scheduled for {selected_month_display}**")
    
    # Simple list view instead of complex calendar grid
    for _, hunt in month_hunts.iterrows():
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            st.write(f"**{hunt['hunt_name']}**")
            st.write(f"📍 {hunt['wma_location']}")
        
        with col2:
            st.write(f"📅 {hunt['start_date'].strftime('%m/%d')} - {hunt['end_date'].strftime('%m/%d')}")
            st.write(f"🎯 {hunt['permits_available']} permits")
        
        with col3:
            st.metric("Score", f"{hunt['combined_score']:.1f}")
            
            # Method icon
            icons = {'Archery': '🏹', 'Gun': '🔫', 'Primitive Weapon': '🏹', 'Group': '👥'}
            st.write(f"{icons.get(hunt['hunt_method'], '🎯')} {hunt['hunt_method']}")

def show_timeline_view(df):
    """Show timeline view of hunts."""
    st.subheader("📈 Hunt Timeline")
    
    # Create timeline chart
    timeline_data = []
    for _, hunt in df.iterrows():
        timeline_data.append({
            'Hunt': hunt['hunt_name'],
            'Start': hunt['start_date'],
            'End': hunt['end_date'],
            'Method': hunt['hunt_method'],
            'Location': hunt['wma_location'],
            'Score': hunt['combined_score'],
            'Permits': hunt['permits_available']
        })
    
    timeline_df = pd.DataFrame(timeline_data)
    
    if not timeline_df.empty:
        # Create Gantt chart using plotly
        fig = px.timeline(
            timeline_df,
            x_start='Start',
            x_end='End',
            y='Hunt',
            color='Method',
            hover_data=['Location', 'Score', 'Permits'],
            title="Hunt Timeline - All Selected Hunts"
        )
        
        fig.update_layout(
            height=max(400, len(timeline_df) * 25),
            xaxis_title="Date",
            yaxis_title="Hunts",
            showlegend=True
        )
        
        # Add rut period highlighting
        fig.add_vrect(
            x0="2025-12-29", x1="2026-01-04",
            fillcolor="red", opacity=0.2,
            annotation_text="Peak Rut", annotation_position="top left"
        )
        
        st.plotly_chart(fig, use_container_width=True)

def show_gantt_chart(df):
    """Show Gantt chart view of hunts."""
    st.subheader("📊 Hunt Gantt Chart")
    
    # Simple Gantt chart by location
    locations = df['wma_location'].unique()
    
    for location in locations:
        st.write(f"**{location}**")
        location_hunts = df[df['wma_location'] == location].sort_values('start_date')
        
        for _, hunt in location_hunts.iterrows():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.write(f"• {hunt['hunt_name']}")
            
            with col2:
                st.write(f"{hunt['start_date'].strftime('%m/%d')} - {hunt['end_date'].strftime('%m/%d')}")
            
            with col3:
                st.write(f"Score: {hunt['combined_score']:.1f}")

def show_data_explorer(filtered_df):
    """Show searchable data table."""
    st.header("📋 Hunt Data Explorer")
    
    if filtered_df.empty:
        st.warning("No hunts match current filters.")
        return
    
    # Search functionality
    search_term = st.text_input("🔍 Search hunts by name or location:")
    
    if search_term:
        mask = (
            filtered_df['hunt_name'].str.contains(search_term, case=False, na=False) |
            filtered_df['wma_location'].str.contains(search_term, case=False, na=False)
        )
        display_df = filtered_df[mask]
    else:
        display_df = filtered_df
    
    # Sort options
    sort_by = st.selectbox(
        "Sort by:",
        options=['combined_score', 'start_date', 'permits_available', 'hunt_name'],
        index=0
    )
    
    ascending = st.checkbox("Ascending order", value=False)
    
    display_df = display_df.sort_values(sort_by, ascending=ascending)
    
    # Display columns
    display_columns = [
        'hunt_name', 'hunt_method', 'wma_location', 'start_date', 'end_date',
        'permits_available', 'duration_days', 'combined_score', 'rut_score', 'moon_score'
    ]
    
    # Format dates for display
    display_df_formatted = display_df.copy()
    display_df_formatted['start_date'] = display_df_formatted['start_date'].dt.strftime('%m/%d/%Y')
    display_df_formatted['end_date'] = display_df_formatted['end_date'].dt.strftime('%m/%d/%Y')
    
    st.dataframe(
        display_df_formatted[display_columns],
        use_container_width=True,
        hide_index=True
    )

def main():
    """Main dashboard function."""
    
    # Title and header
    st.title("🦌 Mississippi WMA Hunt Analysis Dashboard")
    st.markdown("### 2025-26 Season Analysis & Recommendations")
    
    # Important notice
    st.info("""
    🚨 **IMPORTANT**: Applications open **July 15, 2025** and close **August 15, 2025**.  
    Ensure you have a current WMA User Permit before applying!
    """)
    
    # Load data
    df = load_hunt_data()
    
    if df.empty:
        st.error("❌ No hunt data available. Please check CSV files in the data/ folder.")
        st.stop()
    
    # Calculate enhanced scores
    df = calculate_enhanced_scores(df)
    
    st.success(f"✅ Loaded {len(df)} hunts successfully!")
    
    # Sidebar filters
    st.sidebar.header("🎯 Filters")
    
    # Hunt method filter
    hunt_methods = st.sidebar.multiselect(
        "Hunt Methods",
        options=df['hunt_method'].unique(),
        default=df['hunt_method'].unique()
    )
    
    # Location filter
    locations = st.sidebar.multiselect(
        "WMA Locations",
        options=sorted(df['wma_location'].unique()),
        default=sorted(df['wma_location'].unique())
    )
    
    # Score threshold
    min_score = st.sidebar.slider(
        "Minimum Hunt Score",
        min_value=0.0,
        max_value=5.0,
        value=0.0,
        step=0.1
    )
    
    # Filter data
    filtered_df = df[
        (df['hunt_method'].isin(hunt_methods)) &
        (df['wma_location'].isin(locations)) &
        (df['combined_score'] >= min_score)
    ]
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview", 
        "🏆 Top Recommendations", 
        "📅 Calendar View",
        "📋 Data Explorer"
    ])
    
    with tab1:
        show_overview(filtered_df, df)
    
    with tab2:
        show_recommendations(filtered_df)
    
    with tab3:
        show_calendar_view(filtered_df)
    
    with tab4:
        show_data_explorer(filtered_df)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
    📍 <b>Mississippi WMA Hunt Analysis Dashboard</b> | 🗓️ 2025-26 Season<br>
    📊 Data: MDWFP Official Hunt Schedule | 🌙 Moon phases & 🦌 Yazoo County rut timing integrated<br>
    ⚠️ <b>Disclaimer</b>: Hunt details subject to change. Always verify with MDWFP before applying.
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
