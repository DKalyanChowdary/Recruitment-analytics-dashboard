import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Recruitment Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">📊 Recruitment Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown('---')

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('data/recruitment_data.csv')
    df['Application_Date'] = pd.to_datetime(df['Application_Date'])
    df['Interview_Date'] = pd.to_datetime(df['Interview_Date'])
    return df

try:
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Department filter
    departments = ['All'] + sorted(df['Department'].unique().tolist())
    selected_dept = st.sidebar.selectbox("Select Department", departments)
    
    # Status filter
    statuses = ['All'] + sorted(df['Status'].unique().tolist())
    selected_status = st.sidebar.selectbox("Select Status", statuses)
    
    # Source filter
    sources = ['All'] + sorted(df['Source'].unique().tolist())
    selected_source = st.sidebar.selectbox("Select Source", sources)
    
    # Apply filters
    filtered_df = df.copy()
    if selected_dept != 'All':
        filtered_df = filtered_df[filtered_df['Department'] == selected_dept]
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['Status'] == selected_status]
    if selected_source != 'All':
        filtered_df = filtered_df[filtered_df['Source'] == selected_source]
    
    # Key Metrics Row
    st.header("📈 Key Metrics")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_candidates = len(filtered_df)
    hired_candidates = len(filtered_df[filtered_df['Status'] == 'Hired'])
    hire_rate = (hired_candidates / total_candidates * 100) if total_candidates > 0 else 0
    
    hired_df = filtered_df[filtered_df['Status'] == 'Hired']
    avg_time = hired_df['Time_to_Hire_Days'].mean() if len(hired_df) > 0 else 0
    avg_cost = hired_df['Cost_Per_Hire_INR'].mean() if len(hired_df) > 0 else 0
    
    with col1:
        st.metric("Total Candidates", f"{total_candidates}")
    with col2:
        st.metric("Hired", f"{hired_candidates}")
    with col3:
        st.metric("Hire Rate", f"{hire_rate:.1f}%")
    with col4:
        st.metric("Avg Time-to-Hire", f"{avg_time:.0f} days")
    with col5:
        st.metric("Avg Cost-per-Hire", f"₹{avg_cost:,.0f}")
    
    st.markdown('---')
    
    # Row 1: Status & Source Analysis
    st.header("🎯 Recruitment Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Recruitment Funnel by Status")
        status_counts = filtered_df['Status'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = ['#2ecc71', '#e74c3c', '#f39c12', '#3498db']
        ax.barh(status_counts.index, status_counts.values, color=colors[:len(status_counts)])
        ax.set_xlabel('Number of Candidates', fontsize=10)
        for i, v in enumerate(status_counts.values):
            ax.text(v + 2, i, str(v), va='center', fontweight='bold')
        plt.tight_layout()
        st.pyplot(fig)
    
    with col2:
        st.subheader("Source Effectiveness (Conversion Rate)")
        source_analysis = filtered_df.groupby('Source').agg({
            'Candidate_ID': 'count',
            'Status': lambda x: (x == 'Hired').sum()
        })
        source_analysis['Conversion_Rate'] = (source_analysis['Status'] / source_analysis['Candidate_ID'] * 100)
        source_analysis = source_analysis.sort_values('Conversion_Rate', ascending=True)
        
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.barh(source_analysis.index, source_analysis['Conversion_Rate'], color='#3498db')
        ax.set_xlabel('Conversion Rate (%)', fontsize=10)
        for i, v in enumerate(source_analysis['Conversion_Rate'].values):
            ax.text(v + 0.5, i, f'{v:.1f}%', va='center', fontweight='bold', fontsize=9)
        plt.tight_layout()
        st.pyplot(fig)
    
    st.markdown('---')
    
    # Row 2: Time & Cost Analysis
    st.header("⏱️ Time & Cost Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Time-to-Hire by Department")
        hired_only = filtered_df[filtered_df['Status'] == 'Hired']
        if len(hired_only) > 0:
            time_dept = hired_only.groupby('Department')['Time_to_Hire_Days'].mean().sort_values(ascending=False)
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.bar(range(len(time_dept)), time_dept.values, color='#e74c3c')
            ax.set_xticks(range(len(time_dept)))
            ax.set_xticklabels(time_dept.index, rotation=45, ha='right', fontsize=9)
            ax.set_ylabel('Days', fontsize=10)
            for i, v in enumerate(time_dept.values):
                ax.text(i, v + 2, f'{v:.0f}d', ha='center', fontweight='bold', fontsize=9)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No hired candidates in filtered data")
    
    with col2:
        st.subheader("Cost-per-Hire by Source")
        if len(hired_only) > 0:
            cost_source = hired_only.groupby('Source')['Cost_Per_Hire_INR'].mean().sort_values()
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.barh(cost_source.index, cost_source.values, color='#f39c12')
            ax.set_xlabel('Cost (INR)', fontsize=10)
            for i, v in enumerate(cost_source.values):
                ax.text(v + 1000, i, f'₹{v:,.0f}', va='center', fontweight='bold', fontsize=9)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No hired candidates in filtered data")
    
    st.markdown('---')
    
    # Row 3: Diversity & Trends
    st.header("👥 Diversity & Trends")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Gender Distribution (Hired)")
        if len(hired_only) > 0:
            gender_counts = hired_only['Gender'].value_counts()
            fig, ax = plt.subplots(figsize=(7, 5))
            colors_pie = ['#3498db', '#e74c3c', '#2ecc71']
            ax.pie(gender_counts.values, labels=gender_counts.index, autopct='%1.1f%%',
                   colors=colors_pie[:len(gender_counts)], startangle=90)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No hired candidates in filtered data")
    
    with col2:
        st.subheader("Monthly Hiring Trend")
        if len(hired_only) > 0:
            hired_monthly = hired_only.copy()
            hired_monthly['Month'] = hired_monthly['Application_Date'].dt.to_period('M').astype(str)
            monthly_hires = hired_monthly.groupby('Month').size()
            
            fig, ax = plt.subplots(figsize=(8, 5))
            ax.plot(range(len(monthly_hires)), monthly_hires.values, marker='o', 
                   linewidth=2, color='#2ecc71', markersize=6)
            ax.fill_between(range(len(monthly_hires)), monthly_hires.values, alpha=0.3, color='#2ecc71')
            ax.set_xlabel('Month', fontsize=10)
            ax.set_ylabel('Number of Hires', fontsize=10)
            ax.grid(True, alpha=0.3)
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No hired candidates in filtered data")
    
    st.markdown('---')
    
    # Data Table
    st.header("📋 Detailed Data")
    st.dataframe(filtered_df, use_container_width=True)
    
    # Download button
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name='recruitment_analytics.csv',
        mime='text/csv',
    )
    
    # Recommendations
    st.markdown('---')
    st.header("💡 Key Recommendations")
    
    # Calculate recommendations based on full dataset
    source_conv = df.groupby('Source').agg({
        'Candidate_ID': 'count',
        'Status': lambda x: (x == 'Hired').sum()
    })
    source_conv['Rate'] = (source_conv['Status'] / source_conv['Candidate_ID'] * 100)
    best_source = source_conv['Rate'].idxmax()
    worst_source = source_conv['Rate'].idxmin()
    
    rec1, rec2, rec3 = st.columns(3)
    with rec1:
        st.success(f"✅ **Focus on {best_source}**  \nHighest conversion rate: {source_conv.loc[best_source, 'Rate']:.1f}%")
    with rec2:
        st.warning(f"⚠️ **Re-evaluate {worst_source}**  \nLowest conversion rate: {source_conv.loc[worst_source, 'Rate']:.1f}%")
    with rec3:
        st.info(f"🎯 **Reduce Time-to-Hire**  \nCurrent: {df[df['Status']=='Hired']['Time_to_Hire_Days'].mean():.0f} days → Target: <30 days")

except FileNotFoundError:
    st.error("❌ Data file not found! Please ensure 'data/recruitment_data.csv' exists.")
    st.info("Run `python generate_data.py` first to create the dataset.")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown('---')
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem 0;'>
    <p>📊 Recruitment Analytics Dashboard | Built with Streamlit & Python</p>
    <p>💼 Data Analytics Portfolio Project</p>
</div>
""", unsafe_allow_html=True)
