import streamlit as st
import openai
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import time

# Configure page layout and styling
st.set_page_config(
    page_title="AI Fragrance Studio",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a sophisticated premium look
st.markdown("""
<style>
    /* Main color palette: dark purple, gold accents, subtle grays */
    :root {
        --primary-color: #3a2f5b;
        --primary-dark: #2a1f4b;
        --accent-color: #b8973d;
        --accent-light: #d4b052;
        --light-bg: #f5f5f7;
        --dark-gray: #2d2d2d;
        --medium-gray: #444;
        --card-border: #eaeaea;
    }
    
    .main {
        background: linear-gradient(150deg, var(--light-bg) 0%, #fff 100%);
    }
    
    /* Custom header styling */
    h1 {
        color: var(--primary-color);
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        color: var(--primary-color);
        font-weight: 500;
    }
    
    /* Custom button styling */
    .stButton > button {
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--primary-dark) 100%);
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1.2rem;
        font-weight: 500;
        border: none;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, var(--primary-dark) 0%, var(--primary-color) 100%);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-1px);
    }
    
    /* Premium cards with subtle shadow and gold accent */
    .project-card {
        border: 1px solid var(--card-border);
        border-left: 3px solid var(--accent-color);
        border-radius: 6px;
        padding: 20px;
        margin-bottom: 15px;
        background-color: white;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        transition: all 0.2s ease;
    }
    .project-card:hover {
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
    
    /* Metric cards with gold accent */
    .metric-card {
        background-color: white;
        border-radius: 8px;
        border-top: 3px solid var(--accent-color);
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        padding: 18px;
    }
    .metric-card label {
        color: var(--medium-gray);
        font-size: 14px;
        font-weight: 500;
    }
    .metric-card [data-testid="stMetricValue"] {
        color: var(--primary-color);
        font-weight: 600;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background-color: var(--accent-color);
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 6px;
        border: 1px solid var(--card-border);
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 4px 4px 0px 0px;
        padding: 8px 16px;
        background-color: #f0f0f4;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #fcfcfc;
        border-right: 1px solid var(--card-border);
    }
    [data-testid="stSidebar"] [data-testid="stImage"] {
        text-align: center;
        display: block;
        margin: 0 auto;
    }
    
    /* Sliders styling */
    [data-testid="stSlider"] > div > div {
        background-color: var(--accent-light);
    }
    
    /* Custom div for fancy sections */
    .fancy-header {
        background: linear-gradient(90deg, var(--primary-color) 0%, var(--primary-dark) 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 6px;
        margin: 10px 0;
        font-size: 1.2em;
        font-weight: 500;
    }
    
    .gold-accent {
        color: var(--accent-color);
        font-weight: 600;
    }
    
    .info-box {
        background-color: rgba(58, 47, 91, 0.05);
        border-left: 3px solid var(--primary-color);
        padding: 15px;
        border-radius: 4px;
    }
    
    /* Custom tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted var(--accent-color);
    }
    .tooltip .tooltip-text {
        visibility: hidden;
        width: 200px;
        background-color: var(--dark-gray);
        color: white;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
</style>
""", unsafe_allow_html=True)

# Application header with premium styling
st.markdown("""
<div style="display: flex; align-items: center; background: linear-gradient(90deg, #3a2f5b 0%, #2a1f4b 100%); 
            padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);">
    <img src="https://cdn-icons-png.flaticon.com/512/2674/2674505.png" width="80" 
         style="filter: drop-shadow(0 0 5px rgba(255,255,255,0.3));">
    <div style="margin-left: 20px; color: white;">
        <h1 style="margin: 0; color: white; font-size: 2.2em; letter-spacing: -0.5px;">
            ESSENCE<span style="color: #d4b052; font-weight: 300;">&nbsp;STUDIO</span>
        </h1>
        <p style="margin: 5px 0 0 0; opacity: 0.9; font-size: 1.1em;">
            Advanced AI-Driven Fragrance Formulation Platform
        </p>
    </div>
</div>
""", unsafe_allow_html=True)

# Session state initialization for projects and formulations
if 'projects' not in st.session_state:
    st.session_state.projects = {
        "Summer Breeze": {
            "created": "2023-05-10",
            "formulations": 3,
            "profile": {"Fruity": 5, "Floral": 4, "Sweet": 3, "Fresh": 6},
            "description": "A light, refreshing summer fragrance with citrus and floral notes"
        },
        "Spicy Delight": {
            "created": "2023-06-15",
            "formulations": 5,
            "profile": {"Spicy": 6, "Woody": 4, "Sweet": 2},
            "description": "A warm, spicy fragrance with cinnamon and clove notes"
        },
        "Fresh Morning": {
            "created": "2023-07-01",
            "formulations": 4,
            "profile": {"Fresh": 7, "Herbal": 5, "Citrus": 4},
            "description": "A crisp, energizing scent with mint and citrus elements"
        }
    }

if 'current_project' not in st.session_state:
    st.session_state.current_project = None

if 'formulations' not in st.session_state:
    st.session_state.formulations = {}

# Sidebar for authentication and app settings
with st.sidebar:
    # Premium sidebar header
    st.markdown("""
    <div style="text-align:center; margin-bottom:20px;">
        <img src="https://cdn-icons-png.flaticon.com/512/2674/2674505.png" width="60" 
             style="filter: brightness(0.8); opacity: 0.9;">
        <h3 style="color:#3a2f5b; margin-top:10px; margin-bottom:5px;">ESSENCE STUDIO</h3>
        <p style="color:#666; font-size:0.85em; margin:0;">Professional Edition</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication section with premium styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f5f5f7 0%, #fff 100%); 
                padding: 12px; border-radius: 6px; border-left: 3px solid #b8973d; margin-bottom: 20px;">
        <h4 style="color: #3a2f5b; margin-top:0; margin-bottom:10px; font-size: 1.1em;">
            <span style="color: #b8973d;">✦</span> Authentication
        </h4>
    """, unsafe_allow_html=True)
    openai_api_key = st.text_input("API Key", type="password", 
                                 help="Your OpenAI API key is required for AI formulation generation")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # AI Model Settings with enhanced styling
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f5f5f7 0%, #fff 100%); 
                padding: 12px; border-radius: 6px; border-left: 3px solid #b8973d; margin-bottom: 20px;">
        <h4 style="color: #3a2f5b; margin-top:0; margin-bottom:10px; font-size: 1.1em;">
            <span style="color: #b8973d;">✦</span> AI Engine Settings
        </h4>
    """, unsafe_allow_html=True)
    model_choice = st.selectbox(
        "AI Model", 
        ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"], 
        index=0,
        help="Select the AI model that will power your fragrance formulations"
    )
    temperature = st.slider("Creativity", 0.0, 1.0, 0.7, 0.1, 
                          help="Higher values produce more creative results, lower values are more focused")
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display Settings with toggle switches
    st.markdown("""
    <div style="background: linear-gradient(135deg, #f5f5f7 0%, #fff 100%); 
                padding: 12px; border-radius: 6px; border-left: 3px solid #b8973d; margin-bottom: 20px;">
        <h4 style="color: #3a2f5b; margin-top:0; margin-bottom:10px; font-size: 1.1em;">
            <span style="color: #b8973d;">✦</span> Display Preferences
        </h4>
    """, unsafe_allow_html=True)
    show_molecular = st.toggle("Molecular Structures", True, 
                             help="Show molecular structure visualizations for ingredients")
    show_stability = st.toggle("Stability Analysis", True, 
                             help="Show stability and longevity analysis charts")
    show_advanced = st.toggle("Advanced Analytics", False, 
                            help="Enable advanced metrics and detailed analytics views")
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("""<hr style="margin: 30px 0; border: none; height: 1px; background: #ddd;">""", 
              unsafe_allow_html=True)
    
    # Project navigation with enhanced UI
    st.markdown("""
    <div style="background: linear-gradient(135deg, #3a2f5b 0%, #2a1f4b 100%); 
                padding: 15px; border-radius: 6px; margin-bottom: 20px; color: white;">
        <h4 style="margin:0 0 10px 0; color: white; font-size: 1.1em;">
            <span style="color: #d4b052;">✦</span> Project Navigation
        </h4>
    """, unsafe_allow_html=True)
    
    if st.session_state.projects:
        project_options = list(st.session_state.projects.keys())
        project_options.insert(0, "Create New Project")
        selected_project = st.selectbox("Select or Create", project_options, label_visibility="collapsed")
        
        if selected_project != "Create New Project":
            st.session_state.current_project = selected_project
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); padding: 8px; border-radius: 4px; margin-top: 10px;">
                <p style="margin:0; color: white; font-size: 0.9em;">
                    <span style="opacity: 0.8;">Current project:</span><br>
                    <strong>{selected_project}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Export Project Data", key="export_btn", 
                       help="Export your project as JSON for backup or sharing"):
                st.success("Project exported successfully!")
                time.sleep(1)
        else:
            st.session_state.current_project = None
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # User account section
    st.markdown("""
    <div style="position: absolute; bottom: 20px; left: 20px; right: 20px; text-align: center;">
        <img src="https://cdn-icons-png.flaticon.com/512/149/149071.png" width="40" 
             style="border-radius: 50%; border: 2px solid #b8973d; padding: 2px;">
        <p style="margin: 5px 0 0 0; color: #666; font-size: 0.85em;">
            Premium Account · <span style="color: #b8973d;">Active</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

if not openai_api_key:
    st.markdown("""
    <div style="background: linear-gradient(135deg, #3a2f5b 0%, #2a1f4b 100%); 
                padding: 25px; border-radius: 10px; text-align: center; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        <img src="https://cdn-icons-png.flaticon.com/512/6357/6357048.png" width="60" 
             style="margin-bottom: 15px; filter: drop-shadow(0 0 5px rgba(255,255,255,0.2));">
        <h2 style="color: white; margin-bottom: 15px; font-weight: 500;">Authentication Required</h2>
        <p style="color: white; opacity: 0.9; margin-bottom: 20px; font-size: 16px;">
            Please enter your OpenAI API key in the settings panel to access the full functionality of the Essence Studio platform.
        </p>
        <div style="background: rgba(255,255,255,0.15); padding: 12px; border-radius: 6px; backdrop-filter: blur(5px);">
            <p style="color: #d4b052; margin: 0; font-weight: 500;">
                Your key enables secure communication with our AI formulation engine.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()
else:
    client = openai.OpenAI(api_key=openai_api_key)

# Dashboard - shown when no project is selected
if st.session_state.current_project is None:
    st.markdown("""
    <div class="fancy-header">
        <i class="fas fa-chart-line"></i> Dashboard Overview
    </div>
    """, unsafe_allow_html=True)
    
    # Current date and time display
    current_time = datetime.now().strftime("%A, %B %d, %Y")
    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; margin-bottom: 20px;">
        <p style="color: #666; font-size: 1.1em;"><i>Welcome to your fragrance workspace</i></p>
        <p style="color: #666; font-size: 1.1em;">{current_time}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Project metrics in premium styled cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label="ACTIVE PROJECTS", value=len(st.session_state.projects))
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        total_formulations = sum(project["formulations"] for project in st.session_state.projects.values())
        st.metric(label="TOTAL FORMULATIONS", value=total_formulations)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label="TOP DESCRIPTOR", value="Fresh")
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label="SIGNATURE INGREDIENT", value="Citrus Oil")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Project overview graph
    st.subheader("Project Activity")
    
    # Sample project activity data
    project_dates = [project["created"] for project in st.session_state.projects.values()]
    project_names = list(st.session_state.projects.keys())
    formulation_counts = [project["formulations"] for project in st.session_state.projects.values()]
    
    # Create a DataFrame for the chart
    project_df = pd.DataFrame({
        'Project': project_names,
        'Date': pd.to_datetime(project_dates),
        'Formulations': formulation_counts
    })
    project_df = project_df.sort_values('Date')
    
    fig = px.bar(project_df, x='Project', y='Formulations', 
                 color='Formulations', 
                 color_continuous_scale='Blues',
                 labels={'Formulations': 'Number of Formulations'},
                 title='Formulations by Project')
    fig.update_layout(xaxis_title='Project', yaxis_title='Formulations', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    
    # Project cards with premium styling
    st.markdown("""
    <div class="fancy-header">
        <span style="float:left">📂 Your Project Portfolio</span>
        <span style="float:right; font-size: 0.8em; font-weight: normal; opacity: 0.8;">Premium Access</span>
        <div style="clear:both"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Display projects in a grid with enhanced styling
    cols = st.columns(3)
    for i, (name, details) in enumerate(st.session_state.projects.items()):
        with cols[i % 3]:
            # Enhanced project card with visual indicators
            st.markdown(f'''
            <div class="project-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h3 style="margin: 0; color: #3a2f5b;">{name}</h3>
                    <span style="background-color: #3a2f5b; color: white; padding: 3px 8px; 
                           border-radius: 12px; font-size: 0.7em;">ACTIVE</span>
                </div>
                <div style="display: flex; gap: 15px; margin-bottom: 10px; color: #666;">
                    <div>📅 {details['created']}</div>
                    <div>🧪 {details['formulations']} formulations</div>
                </div>
                <p style="color: #444; margin-bottom: 15px; font-size: 0.95em;">{details['description']}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            # Small radar chart for each project with improved styling
            profile_df = pd.DataFrame({
                'Attribute': list(details['profile'].keys()),
                'Value': list(details['profile'].values())
            })
            fig = px.line_polar(profile_df, r='Value', theta='Attribute', line_close=True)
            fig.update_layout(
                height=200, 
                margin=dict(l=20, r=20, t=20, b=20),
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 7],
                        linecolor='#3a2f5b',
                        gridcolor='#f0f0f0'
                    ),
                    angularaxis=dict(
                        linecolor='#3a2f5b',
                        gridcolor='#f0f0f0'
                    )
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#444')
            )
            fig.update_traces(
                fill='toself',
                fillcolor='rgba(184, 151, 61, 0.2)',
                line=dict(color='#b8973d', width=2)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            if st.button("Open Project", key=f"open_{name}"):
                st.session_state.current_project = name
                st.rerun()
    
    # Create New Project Form with premium styling
    st.markdown("""
    <div class="fancy-header" style="background: linear-gradient(90deg, #b8973d 0%, #d4b052 100%);">
        <i class="fas fa-plus-circle"></i> Create New Fragrance Project
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box" style="margin-bottom: 20px;">
        <p style="margin: 0; color: #444;">
            Create a new fragrance project by providing a name, description and sensory profile.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("new_project_form"):
        new_project_name = st.text_input("Project Name")
        new_project_desc = st.text_area("Project Description", placeholder="Describe your fragrance project...")
        
        col1, col2 = st.columns(2)
        with col1:
            fruity = st.slider("Fruity", 0, 7, 0)
            floral = st.slider("Floral", 0, 7, 0)
            spicy = st.slider("Spicy", 0, 7, 0)
            sweet = st.slider("Sweet", 0, 7, 0)
        with col2:
            woody = st.slider("Woody", 0, 7, 0)
            fresh = st.slider("Fresh", 0, 7, 0)
            herbal = st.slider("Herbal", 0, 7, 0)
            citrus = st.slider("Citrus", 0, 7, 0)
        
        submit_btn = st.form_submit_button("Create Project")
        
        if submit_btn and new_project_name:
            profile = {}
            for attr, val in [("Fruity", fruity), ("Floral", floral), ("Spicy", spicy), 
                              ("Sweet", sweet), ("Woody", woody), ("Fresh", fresh), 
                              ("Herbal", herbal), ("Citrus", citrus)]:
                if val > 0:
                    profile[attr] = val
            
            st.session_state.projects[new_project_name] = {
                "created": datetime.now().strftime("%Y-%m-%d"),
                "formulations": 0,
                "profile": profile,
                "description": new_project_desc
            }
            st.session_state.current_project = new_project_name
            st.success(f"Project '{new_project_name}' created successfully!")
            st.rerun()

# Project Workspace - shown when a project is selected
else:
    current = st.session_state.current_project
    
    # Project header with tabs for different modules
    st.header(f"Project: {current}")
    
    # Project progress indicator
    project_stages = ["Define Profile", "Generate Formulations", "Analyze Results", "Refine & Iterate"]
    current_stage = 1  # Example - could be stored in session state
    
    progress_col1, progress_col2 = st.columns([1, 3])
    with progress_col1:
        st.caption("Project Progress:")
    with progress_col2:
        progress = st.progress((current_stage) / len(project_stages))
    
    # Project workspace with tabs for each module
    tabs = st.tabs(["📋 Profile", "🧪 Formulation", "📊 Analysis", "🔄 Refinement"])
    
    # Module 1: Define Target Scent/Flavour Profile
    with tabs[0]:
        st.subheader("Define Target Scent/Flavour Profile")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            project_desc = st.text_area(
                "Natural Language Description", 
                value=st.session_state.projects[current].get("description", ""),
                height=150,
                placeholder="Describe your desired scent or flavour in detail..."
            )
            
            # Save description when changed
            if project_desc != st.session_state.projects[current].get("description", ""):
                st.session_state.projects[current]["description"] = project_desc
            
            # Structured sensory profile input
            st.write("Adjust Sensory Profile")
            
            # Get current profile or initialize empty
            profile = st.session_state.projects[current].get("profile", {})
            
            # All possible descriptors
            all_descriptors = ["Fruity", "Floral", "Spicy", "Sweet", "Sour", "Woody", 
                              "Creamy", "Nutty", "Fresh", "Herbal", "Citrus", "Earthy", 
                              "Green", "Musky", "Powdery", "Vanilla", "Amber", "Balsamic"]
            
            # Preset combinations
            preset_combinations = {
                "Floral Fresh": {"Floral": 6, "Fresh": 5, "Citrus": 3, "Green": 2},
                "Woody Oriental": {"Woody": 5, "Spicy": 4, "Amber": 3, "Vanilla": 2},
                "Citrus Aromatic": {"Citrus": 6, "Herbal": 4, "Fresh": 3},
                "Gourmand Sweet": {"Sweet": 5, "Vanilla": 4, "Creamy": 3, "Nutty": 2}
            }
            
            # Presets selector
            preset = st.selectbox("Quick Presets", ["Custom"] + list(preset_combinations.keys()))
            
            if preset != "Custom" and st.button("Apply Preset"):
                profile = preset_combinations[preset]
                st.session_state.projects[current]["profile"] = profile
                st.success(f"Applied {preset} preset")
                st.rerun()
            
            # Create multi-column layout for sliders
            slider_cols = st.columns(3)
            updated_profile = {}
            
            # Display sliders for all descriptors, showing current values if they exist
            for i, desc in enumerate(all_descriptors):
                with slider_cols[i % 3]:
                    value = profile.get(desc, 0)
                    new_value = st.slider(desc, 0, 7, value, key=f"slider_{desc}")
                    if new_value > 0:
                        updated_profile[desc] = new_value
            
            # Save updated profile
            if updated_profile != profile:
                st.session_state.projects[current]["profile"] = updated_profile
        
        with col2:
            # Visualization of the current sensory profile
            st.write("Current Sensory Profile")
            
            if profile:
                profile_df = pd.DataFrame({
                    'Attribute': list(profile.keys()),
                    'Value': list(profile.values())
                })
                
                fig = px.line_polar(profile_df, r='Value', theta='Attribute', line_close=True)
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 7]
                        )
                    ),
                    showlegend=False
                )
