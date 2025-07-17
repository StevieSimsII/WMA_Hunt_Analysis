"""
Simple test to verify dashboard functionality
"""
import streamlit as st
import pandas as pd

st.title("🦌 Mississippi WMA Hunt Dashboard - Quick Test")

# Test CSV loading
try:
    archery_df = pd.read_csv('data/deer_archery_hunts_2025_26.csv')
    gun_df = pd.read_csv('data/deer_gun_hunts_2025_26.csv')
    pw_df = pd.read_csv('data/deer_primitive_weapon_hunts_2025_26.csv')
    group_df = pd.read_csv('data/deer_group_hunts_2025_26.csv')
    
    st.success("✅ All CSV files loaded successfully!")
    
    st.write(f"📊 **Data Summary:**")
    st.write(f"- Archery Hunts: {len(archery_df)}")
    st.write(f"- Gun Hunts: {len(gun_df)}")
    st.write(f"- Primitive Weapon Hunts: {len(pw_df)}")
    st.write(f"- Group Hunts: {len(group_df)}")
    
    total_hunts = len(archery_df) + len(gun_df) + len(pw_df) + len(group_df)
    st.write(f"- **Total Hunts: {total_hunts}**")
    
    st.subheader("Sample Data")
    st.write("Archery Hunts Sample:")
    st.dataframe(archery_df.head())
    
except Exception as e:
    st.error(f"❌ Error loading data: {e}")
    st.write("Current working directory files:")
    import os
    st.write(os.listdir('.'))

st.write("**Dashboard should be working!** ✅")
