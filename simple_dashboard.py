"""
Mississippi WMA Draw Hunt Analysis Dashboard - Fixed Version
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
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
            df = pd.read_csv(file_path)
            df['hunt_method'] = hunt_type
            df['start_date'] = pd.to_datetime(df['start_date'])
            df['end_date'] = pd.to_datetime(df['end_date'])
            all_hunts.append(df)
        
        combined_df = pd.concat(all_hunts, ignore_index=True)
        return combined_df
        
    except Exception as e:
        st.error(f"Error loading hunt data: {e}")
        return pd.DataFrame()

def calculate_scores(df):
    """Calculate hunt scores."""
    if df.empty:
        return df
    
    df = df.copy()
    
    # Rut scoring
    def get_rut_score(date):
        if datetime(2025, 12, 29) <= date <= datetime(2026, 1, 4):
            return 5  # Peak Rut
        elif datetime(2025, 12, 16) <= date <= datetime(2025, 12, 28):
            return 4  # Pre-Peak Rut
        elif datetime(2025, 11, 15) <= date <= datetime(2025, 12, 15):
            return 3  # Pre-Rut
        else:
            return 2  # Other
    
    # Moon scoring (simplified)
    def get_moon_score(date):
        new_moons = [
            datetime(2025, 10, 21),
            datetime(2025, 11, 20), 
            datetime(2025, 12, 19),
            datetime(2026, 1, 20)
        ]
        
        best_score = 1
        for moon_date in new_moons:
            days_diff = abs((date - moon_date).days)
            if days_diff <= 2:
                best_score = max(best_score, 3)
            elif days_diff <= 5:
                best_score = max(best_score, 2)
        
        return best_score
    
    df['rut_score'] = df['start_date'].apply(get_rut_score)
    df['moon_score'] = df['start_date'].apply(get_moon_score)
    df['permit_score'] = np.minimum(df['permits_available'] / 10, 3)
    
    df['combined_score'] = (
        df['rut_score'] * 0.4 +
        df['moon_score'] * 0.3 +
        df['permit_score'] * 0.3
    ).round(2)
    
    return df

def main():
    st.title("🦌 Mississippi WMA Hunt Analysis Dashboard")
    st.markdown("### 2025-26 Season Analysis & Recommendations")
    
    # Load and process data
    df = load_hunt_data()
    
    if df.empty:
        st.error("No hunt data available. Please check your CSV files in the data/ folder.")
        st.stop()
    
    df = calculate_scores(df)
    
    # Sidebar filters
    st.sidebar.header("🎯 Filters")
    
    hunt_methods = st.sidebar.multiselect(
        "Hunt Methods",
        options=df['hunt_method'].unique(),
        default=df['hunt_method'].unique()
    )
    
    locations = st.sidebar.multiselect(
        "WMA Locations", 
        options=sorted(df['wma_location'].unique()),
        default=sorted(df['wma_location'].unique())
    )
    
    # Filter data
    filtered_df = df[
        (df['hunt_method'].isin(hunt_methods)) &
        (df['wma_location'].isin(locations))
    ]
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Overview", "🏆 Top Hunts", "📋 All Data"])
    
    with tab1:
        st.header("📊 Hunt Overview")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Hunts", len(filtered_df))
        with col2:
            st.metric("Total Permits", filtered_df['permits_available'].sum())
        with col3:
            st.metric("Unique Locations", filtered_df['wma_location'].nunique())
        with col4:
            st.metric("Avg Score", f"{filtered_df['combined_score'].mean():.2f}")
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            method_counts = filtered_df['hunt_method'].value_counts()
            fig1 = px.pie(values=method_counts.values, names=method_counts.index, 
                         title="Hunts by Method")
            st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            location_permits = filtered_df.groupby('wma_location')['permits_available'].sum().sort_values(ascending=False)
            fig2 = px.bar(x=location_permits.values, y=location_permits.index, 
                         orientation='h', title="Permits by Location")
            st.plotly_chart(fig2, use_container_width=True)
    
    with tab2:
        st.header("🏆 Top Hunt Recommendations")
        
        top_hunts = filtered_df.nlargest(10, 'combined_score')
        
        for idx, (_, hunt) in enumerate(top_hunts.iterrows(), 1):
            with st.expander(f"#{idx} - {hunt['hunt_name']} (Score: {hunt['combined_score']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Method:** {hunt['hunt_method']}")
                    st.write(f"**Location:** {hunt['wma_location']}")
                    st.write(f"**Date:** {hunt['start_date'].strftime('%m/%d/%Y')} - {hunt['end_date'].strftime('%m/%d/%Y')}")
                
                with col2:
                    st.write(f"**Permits:** {hunt['permits_available']}")
                    st.write(f"**Score:** {hunt['combined_score']}/5.0")
                    st.write(f"**Rut Score:** {hunt['rut_score']}/5")
                
                if hunt['rut_score'] >= 5:
                    st.success("🦌 PEAK RUT PERIOD")
                elif hunt['rut_score'] >= 4:
                    st.info("🎯 Pre-Peak Rut")
    
    with tab3:
        st.header("📋 All Hunt Data")
        
        st.dataframe(
            filtered_df[['hunt_name', 'hunt_method', 'wma_location', 'start_date', 'end_date', 
                        'permits_available', 'combined_score']],
            use_container_width=True
        )

if __name__ == "__main__":
    main()
