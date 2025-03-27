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

# Custom CSS for a more professional look
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton button {
        background-color: #4682B4;
        color: white;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
    .stButton button:hover {
        background-color: #36648B;
    }
    .project-card {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 10px;
        background-color: white;
    }
    .metric-card {
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        padding: 15px;
    }
    h1, h2, h3 {
        color: #36648B;
    }
    .stProgress .st-bo {
        background-color: #4682B4;
    }
    .stDataFrame {
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Application header
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/2674/2674505.png", width=80)
with col2:
    st.title("AI-driven Flavour & Fragrance Studio")
    st.markdown("*Professional toolkit for fragrance formulation and development*")

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
    st.header("Settings")
    with st.expander("Authentication", expanded=False):
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        st.info("API key is required for AI formulation generation")
    
    with st.expander("AI Model Settings", expanded=False):
        model_choice = st.selectbox(
            "Select AI Model", 
            ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"], 
            index=0
        )
        temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.7, 0.1)
    
    with st.expander("Display Settings", expanded=False):
        show_molecular = st.checkbox("Show Molecular Structures", True)
        show_stability = st.checkbox("Show Stability Analysis", True)
        show_advanced = st.checkbox("Show Advanced Metrics", False)
    
    st.divider()
    
    # Project navigation
    st.subheader("Project Navigation")
    if st.session_state.projects:
        project_options = list(st.session_state.projects.keys())
        project_options.insert(0, "Create New Project")
        selected_project = st.selectbox("Select or Create Project", project_options)
        
        if selected_project != "Create New Project":
            st.session_state.current_project = selected_project
            st.info(f"Working on: {selected_project}")
            if st.button("Export Project", key="export_btn"):
                st.success("Project exported successfully!")
        else:
            st.session_state.current_project = None

# Main content area depends on whether a project is selected or not
if not openai_api_key:
    st.warning("Please enter your OpenAI API key in the sidebar to continue.")
    st.stop()
else:
    client = openai.OpenAI(api_key=openai_api_key)

# Dashboard - shown when no project is selected
if st.session_state.current_project is None:
    st.header("Dashboard")
    
    # Project metrics in attractive cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label="Active Projects", value=len(st.session_state.projects))
        st.markdown('</div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        total_formulations = sum(project["formulations"] for project in st.session_state.projects.values())
        st.metric(label="Total Formulations", value=total_formulations)
        st.markdown('</div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label="Most Used Descriptor", value="Fresh")
        st.markdown('</div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric(label="Most Used Ingredient", value="Citrus Oil")
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
    
    # Project cards
    st.subheader("Your Projects")
    
    # Display projects in a grid
    cols = st.columns(3)
    for i, (name, details) in enumerate(st.session_state.projects.items()):
        with cols[i % 3]:
            st.markdown(f'<div class="project-card">', unsafe_allow_html=True)
            st.subheader(name)
            st.caption(f"Created: {details['created']}")
            st.caption(f"Formulations: {details['formulations']}")
            st.text(details['description'])
            
            # Small radar chart for each project
            profile_df = pd.DataFrame({
                'Attribute': list(details['profile'].keys()),
                'Value': list(details['profile'].values())
            })
            fig = px.line_polar(profile_df, r='Value', theta='Attribute', line_close=True)
            fig.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
            if st.button("Open", key=f"open_{name}"):
                st.session_state.current_project = name
                st.experimental_rerun()
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Create New Project Form
    st.header("Create New Project")
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
            st.experimental_rerun()

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
                st.experimental_rerun()
            
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
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Adjust the sliders to create your sensory profile")
        
        # Target audience and usage settings
        st.subheader("Additional Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            target_audience = st.multiselect(
                "Target Audience", 
                ["Luxury", "Mass Market", "Men", "Women", "Unisex", "Young", "Mature"],
                default=["Unisex"]
            )
            
            usage_context = st.multiselect(
                "Usage Context",
                ["Personal Fragrance", "Home Fragrance", "Beverage", "Food", "Cosmetic"],
                default=["Personal Fragrance"]
            )
        
        with col2:
            st.write("Constraints")
            constraints = st.multiselect(
                "Ingredient Constraints",
                ["Natural Only", "Allergen-Free", "Vegan", "Kosher", "Halal", "Sustainable"],
                default=[]
            )
            
            longevity = st.select_slider(
                "Desired Longevity",
                options=["Very Short", "Short", "Medium", "Long", "Very Long"],
                value="Medium"
            )
            
        # Save button for this module
        if st.button("Save Profile", key="save_profile"):
            st.session_state.projects[current]["target_audience"] = target_audience
            st.session_state.projects[current]["usage_context"] = usage_context
            st.session_state.projects[current]["constraints"] = constraints
            st.session_state.projects[current]["longevity"] = longevity
            st.success("Profile saved successfully! Ready for formulation generation.")
    
    # Module 2: AI Processing and Formulation Generation
    with tabs[1]:
        st.subheader("AI-Powered Formulation Generation")
        
        # Get current profile
        profile = st.session_state.projects[current].get("profile", {})
        description = st.session_state.projects[current].get("description", "")
        
        # Check if we have enough data to generate formulations
        if not profile or not description:
            st.warning("Please complete your fragrance profile in the Profile tab before generating formulations.")
        else:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.write("Generation Settings")
                
                num_formulations = st.slider("Number of Formulations to Generate", 1, 5, 1)
                
                complexity = st.select_slider(
                    "Formulation Complexity",
                    options=["Simple", "Moderate", "Complex", "Expert"],
                    value="Moderate"
                )
                
                # Additional generation parameters
                with st.expander("Advanced Generation Parameters"):
                    focus_ingredients = st.text_input("Focus Ingredients (comma separated)", "")
                    max_ingredients = st.slider("Maximum Number of Ingredients", 5, 30, 15)
                    st.checkbox("Include rare/specialty ingredients", False)
                
            with col2:
                st.info("""
                The AI will analyze your sensory profile and description to generate unique formulations.
                
                Generation may take up to 30 seconds depending on complexity.
                """)
            
            # Generate button with loading animation
            if st.button("Generate Formulations", key="generate_btn"):
                with st.spinner("AI is analyzing and generating formulations..."):
                    # Create a comprehensive prompt for the AI
                    profile_text = ", ".join([f"{k}: {v}/7" for k, v in profile.items()])
                    
                    constraints_text = ""
                    if hasattr(st.session_state.projects[current], "constraints"):
                        constraints_text = f"Constraints: {', '.join(st.session_state.projects[current].get('constraints', []))}"
                    
                    audience_text = ""
                    if hasattr(st.session_state.projects[current], "target_audience"):
                        audience_text = f"Target audience: {', '.join(st.session_state.projects[current].get('target_audience', []))}"
                    
                    prompt = f"""
                    As an AI fragrance formulation expert, create {num_formulations} detailed {complexity.lower()} complexity fragrance formulation(s) based on:
                    
                    DESCRIPTION: {description}
                    
                    SENSORY PROFILE: {profile_text}
                    
                    {constraints_text}
                    {audience_text}
                    
                    For each formulation provide:
                    1. A descriptive name
                    2. A list of ingredients with exact percentages (should sum to 100%)
                    3. A brief description of the sensory experience
                    4. A summary of the main olfactory notes (top, middle, base)
                    5. Predicted longevity and sillage
                    
                    Format each formulation as a JSON object following this structure:
                    {{
                        "name": "Formulation Name",
                        "ingredients": [
                            {{"name": "Ingredient Name", "percentage": number}},
                            ...
                        ],
                        "description": "Sensory description",
                        "notes": {{"top": ["note1", "note2"], "middle": ["note1", "note2"], "base": ["note1", "note2"]}},
                        "longevity": "duration in hours",
                        "sillage": "projection strength"
                    }}
                    
                    Return an array of these JSON objects.
                    """
                    
                    # Make the API call
                    try:
                        completion = client.chat.completions.create(
                            model=model_choice,
                            temperature=temperature,
                            response_format={"type": "json_object"},
                            messages=[
                                {"role": "system", "content": "You are an expert AI assistant specializing in fragrance formulation."},
                                {"role": "user", "content": prompt}
                            ]
                        )
                        
                        # Process the response
                        formulations_text = completion.choices[0].message.content
                        
                        # Parse the JSON response
                        try:
                            import json
                            formulations_data = json.loads(formulations_text)
                            
                            # Store the formulations in session state
                            if 'formulations' not in st.session_state:
                                st.session_state.formulations = {}
                                
                            if current not in st.session_state.formulations:
                                st.session_state.formulations[current] = []
                            
                            # Add the new formulations
                            if "formulations" in formulations_data:
                                st.session_state.formulations[current].extend(formulations_data["formulations"])
                            else:
                                st.session_state.projects[current]["formulations"] += num_formulations
                                st.session_state.formulations[current].extend([formulations_data])
                            
                            st.success(f"Successfully generated {num_formulations} formulation(s)!")
                            
                            # Show a preview of the first formulation
                            with st.expander("Quick Preview", expanded=True):
                                if "formulations" in formulations_data:
                                    formulation = formulations_data["formulations"][0]
                                else:
                                    formulation = formulations_data
                                
                                st.subheader(formulation.get("name", "New Formulation"))
                                st.write(formulation.get("description", ""))
                                
                                # Create a pie chart of ingredients
                                ingredients = formulation.get("ingredients", [])
                                if ingredients:
                                    ingredient_df = pd.DataFrame(ingredients)
                                    fig = px.pie(
                                        ingredient_df, 
                                        values='percentage', 
                                        names='name',
                                        title='Ingredient Composition',
                                        color_discrete_sequence=px.colors.sequential.Blues_r
                                    )
                                    st.plotly_chart(fig, use_container_width=True)
                            
                            st.info("View all formulations in the Analysis tab")
                            
                        except json.JSONDecodeError as e:
                            st.error(f"Error parsing AI response: {e}")
                            st.text(formulations_text)
                    
                    except Exception as e:
                        st.error(f"Error generating formulations: {e}")
            
            # Display existing formulations if any
            if current in st.session_state.get('formulations', {}) and st.session_state.formulations[current]:
                st.divider()
                st.subheader("Existing Formulations")
                
                formulation_names = [f.get("name", f"Formulation {i+1}") 
                                     for i, f in enumerate(st.session_state.formulations[current])]
                
                selected_form = st.selectbox("Select a formulation to view", formulation_names)
                selected_index = formulation_names.index(selected_form)
                
                formulation = st.session_state.formulations[current][selected_index]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader(formulation.get("name", "Unnamed Formulation"))
                    st.write(formulation.get("description", "No description available"))
                    
                    # Notes
                    if "notes" in formulation:
                        st.write("**Olfactory Notes:**")
                        notes = formulation["notes"]
                        if "top" in notes:
                            st.write(f"- Top: {', '.join(notes['top'])}")
                        if "middle" in notes:
                            st.write(f"- Middle: {', '.join(notes['middle'])}")
                        if "base" in notes:
                            st.write(f"- Base: {', '.join(notes['base'])}")
                    
                    # Characteristics
                    st.write(f"**Longevity:** {formulation.get('longevity', 'Unknown')}")
                    st.write(f"**Sillage:** {formulation.get('sillage', 'Unknown')}")
                
                with col2:
                    # Ingredients pie chart
                    ingredients = formulation.get("ingredients", [])
                    if ingredients:
                        ingredient_df = pd.DataFrame(ingredients)
                        fig = px.pie(
                            ingredient_df, 
                            values='percentage', 
                            names='name',
                            title='Ingredient Composition',
                            color_discrete_sequence=px.colors.sequential.Blues_r
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No ingredient information available")
    
    # Module 3: Analysis
    with tabs[2]:
        st.subheader("Formulation Analysis")
        
        # Check if we have formulations to analyze
        if current not in st.session_state.get('formulations', {}) or not st.session_state.formulations[current]:
            st.info("No formulations available for analysis. Please generate formulations first.")
        else:
            # Get the formulations for this project
            formulations = st.session_state.formulations[current]
            
            # Formulation selector
            formulation_names = [f.get("name", f"Formulation {i+1}") for i, f in enumerate(formulations)]
            
            # Allow comparing multiple formulations
            selected_forms = st.multiselect(
                "Select formulations to analyze",
                formulation_names,
                default=[formulation_names[0]] if formulation_names else []
            )
            
            if not selected_forms:
                st.warning("Please select at least one formulation to analyze.")
            else:
                # Get the selected formulations
                selected_indices = [formulation_names.index(name) for name in selected_forms]
                selected_formulations = [formulations[i] for i in selected_indices]
                
                # Tabs for different analysis views
                analysis_tabs = st.tabs(["Composition", "Sensory Profile", "Advanced Analysis"])
                
                # Composition Analysis
                with analysis_tabs[0]:
                    st.subheader("Ingredient Composition Analysis")
                    
                    if len(selected_formulations) == 1:
                        # Single formulation pie chart
                        formulation = selected_formulations[0]
                        ingredients = formulation.get("ingredients", [])
                        
                        if ingredients:
                            # Filter out ingredients below a certain threshold for legibility
                            threshold = 1.0  # Minimum percentage to show in pie chart
                            main_ingredients = [i for i in ingredients if i["percentage"] >= threshold]
                            other_percentage = sum(i["percentage"] for i in ingredients if i["percentage"] < threshold)
                            
                            # Add "Other" category if needed
                            if other_percentage > 0:
                                main_ingredients.append({
                                    "name": "Other Minor Ingredients",
                                    "percentage": other_percentage
                                })
                            
                            ingredient_df = pd.DataFrame(main_ingredients)
                            fig = px.pie(
                                ingredient_df, 
                                values='percentage', 
                                names='name',
                                title=f'Ingredient Composition: {formulation.get("name", "Formulation")}',
                                color_discrete_sequence=px.colors.sequential.Blues_r
                            )
                            fig.update_traces(textposition='inside', textinfo='percent+label')
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # Tabular view of all ingredients
                            st.write("Complete Ingredient List:")
                            ingredient_df_full = pd.DataFrame(ingredients)
                            ingredient_df_full = ingredient_df_full.sort_values(by="percentage", ascending=False)
                            st.dataframe(ingredient_df_full, use_container_width=True)
                        else:
                            st.info("No ingredient information available")
                    
                    else:
                        # Comparative bar chart for multiple formulations
                        st.write("Comparing Top Ingredients Across Formulations")
                        
                        # Get all ingredients across all selected formulations
                        all_ingredients = {}
                        for formulation in selected_formulations:
                            for ingredient in formulation.get("ingredients", []):
                                name = ingredient["name"]
                                if name not in all_ingredients:
                                    all_ingredients[name] = {}
                                all_ingredients[name][formulation.get("name", "Unnamed")] = ingredient["percentage"]
                        
                        # Create a dataframe for plotting
                        ingredient_data = []
                        for ingredient_name, formulation_values in all_ingredients.items():
                            for formulation_name, percentage in formulation_values.items():
                                ingredient_data.append({
                                    "Ingredient": ingredient_name,
                                    "Formulation": formulation_name,
                                    "Percentage": percentage
                                })
                        
                        if ingredient_data:
                            ingredient_df = pd.DataFrame(ingredient_data)
                            
                            # Get top ingredients by total percentage across formulations
                            top_ingredients = ingredient_df.groupby("Ingredient")["Percentage"].sum().nlargest(10).index.tolist()
                            
                            # Filter to only show top ingredients
                            ingredient_df_filtered = ingredient_df[ingredient_df["Ingredient"].isin(top_ingredients
