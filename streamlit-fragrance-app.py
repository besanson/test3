import streamlit as st
import openai
import pandas as pd
import time
import json
import os
from PIL import Image
from io import BytesIO
import base64

# Set page configuration
st.set_page_config(
    page_title="Fragrance Creator",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f5f5;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .fragrance-card {
        background-color: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .accent-header {
        color: #2E7D32;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'fragrance_concepts' not in st.session_state:
    st.session_state.fragrance_concepts = []
if 'selected_concept' not in st.session_state:
    st.session_state.selected_concept = None
if 'current_stage' not in st.session_state:
    st.session_state.current_stage = "concept"
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'formula' not in st.session_state:
    st.session_state.formula = {}
if 'final_fragrance' not in st.session_state:
    st.session_state.final_fragrance = None

# Sidebar for navigation and API key input
with st.sidebar:
    st.title("🧪 Fragrance Creator")
    
    api_key = st.text_input("Enter your OpenAI API key", type="password")
    if api_key:
        st.session_state.api_key = api_key
        os.environ["OPENAI_API_KEY"] = api_key
    
    st.markdown("---")
    st.markdown("## Fragrance Creation Workflow")
    
    # Workflow stages
    stages = ["Concept", "Accord Development", "Formula Creation", "Evaluation", "Final Fragrance"]
    
    for i, stage in enumerate(stages):
        if i+1 < stages.index(st.session_state.current_stage.title()) + 1:
            st.success(f"{i+1}. {stage} ✓")
        elif i+1 == stages.index(st.session_state.current_stage.title()) + 1:
            st.info(f"{i+1}. {stage} 🔄")
        else:
            st.markdown(f"{i+1}. {stage}")

# Helper functions
def call_openai_api(prompt, max_tokens=1000):
    if not st.session_state.api_key:
        st.error("Please enter your OpenAI API key in the sidebar.")
        return None
    
    try:
        client = openai.OpenAI(api_key=st.session_state.api_key)
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert perfumer with deep knowledge of fragrance creation, ingredients, and industry trends."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling OpenAI API: {str(e)}")
        return None

def generate_fragrance_pyramid_image(top_notes, middle_notes, base_notes):
    """Generate a text-based fragrance pyramid visualization"""
    st.markdown("### Fragrance Pyramid")
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown("""
        <div style="width: 100%; text-align: center;">
            <div style="background-color: #ffcdd2; padding: 10px; border-radius: 10px 10px 0 0;">
                <h4>Top Notes</h4>
                <p>{}</p>
            </div>
            <div style="background-color: #c8e6c9; padding: 15px; margin-top: 5px;">
                <h4>Middle Notes</h4>
                <p>{}</p>
            </div>
            <div style="background-color: #bbdefb; padding: 20px; border-radius: 0 0 10px 10px; margin-top: 5px;">
                <h4>Base Notes</h4>
                <p>{}</p>
            </div>
        </div>
        """.format(', '.join(top_notes), ', '.join(middle_notes), ', '.join(base_notes)), unsafe_allow_html=True)

# Main app content
st.title("AI-Powered Fragrance Creation Studio")

# Check if API key is provided
if not st.session_state.api_key:
    st.warning("Please enter your OpenAI API key in the sidebar to continue.")
    st.stop()

# Concept Stage
if st.session_state.current_stage == "concept":
    st.header("1. Concept Development")
    
    concept_col1, concept_col2 = st.columns([2, 1])
    
    with concept_col1:
        st.markdown("""
        Start by defining the concept for your fragrance. What story do you want to tell? 
        What emotions should it evoke? Who is the target audience?
        """)
        
        target_audience = st.selectbox(
            "Target Audience",
            ["Luxury", "Mass Market", "Niche", "Youth", "Mature"]
        )
        
        fragrance_family = st.selectbox(
            "Fragrance Family",
            ["Floral", "Oriental", "Woody", "Fresh", "Fougère", "Chypre", "Gourmand", "Citrus", "Aquatic", "Green"]
        )
        
        inspiration = st.text_area("Inspiration or Concept Description", height=100,
                                 placeholder="Describe the inspiration, mood, or story behind your fragrance...")
        
        col1, col2 = st.columns(2)
        
        with col1:
            season = st.multiselect(
                "Season",
                ["Spring", "Summer", "Fall", "Winter"],
                default=["Spring"]
            )
        
        with col2:
            occasion = st.multiselect(
                "Occasion",
                ["Everyday", "Office", "Evening", "Special Occasion", "Outdoor", "Intimate"],
                default=["Everyday"]
            )
    
    with concept_col2:
        st.markdown("### Mood Board")
        mood = st.slider("Mood Scale", 1, 10, 5, 
                         help="1 = Calm/Relaxing, 10 = Energetic/Exciting")
        
        complexity = st.slider("Complexity", 1, 10, 5,
                              help="1 = Simple/Straightforward, 10 = Complex/Sophisticated")
        
        longevity = st.slider("Desired Longevity", 1, 10, 7,
                             help="1 = Light/Ephemeral, 10 = Long-lasting/Intense")
    
    if st.button("Generate Fragrance Concepts"):
        with st.spinner("Creating fragrance concepts..."):
            prompt = f"""
            Generate three distinct fragrance concepts based on the following parameters:
            - Target Audience: {target_audience}
            - Fragrance Family: {fragrance_family}
            - Inspiration: {inspiration}
            - Season: {', '.join(season)}
            - Occasion: {', '.join(occasion)}
            - Mood: {mood}/10
            - Complexity: {complexity}/10
            - Longevity: {longevity}/10
            
            For each concept, provide:
            1. A creative name
            2. A brief description of the fragrance concept (2-3 sentences)
            3. Key notes that would be featured (top, middle, base)
            4. A unique selling point or signature element
            
            Format your response as JSON with this structure:
            [
                {
                    "name": "Name of Concept 1",
                    "description": "Description of concept 1",
                    "notes": {
                        "top": ["Note 1", "Note 2", "Note 3"],
                        "middle": ["Note 1", "Note 2", "Note 3"],
                        "base": ["Note 1", "Note 2", "Note 3"]
                    },
                    "signature": "Unique selling point"
                },
                {...concept 2...},
                {...concept 3...}
            ]
            """
            
            response = call_openai_api(prompt)
            if response:
                try:
                    st.session_state.fragrance_concepts = json.loads(response)
                    st.success("Concepts generated successfully!")
                except json.JSONDecodeError:
                    st.error("Error parsing response. Please try again.")
    
    # Display generated concepts
    if st.session_state.fragrance_concepts:
        st.markdown("### Generated Concepts")
        
        cols = st.columns(len(st.session_state.fragrance_concepts))
        
        for i, concept in enumerate(st.session_state.fragrance_concepts):
            with cols[i]:
                st.markdown(f"""
                <div class="fragrance-card">
                    <h3 class="accent-header">{concept['name']}</h3>
                    <p>{concept['description']}</p>
                    <p><strong>Signature:</strong> {concept['signature']}</p>
                    <details>
                        <summary>View Notes</summary>
                        <p><strong>Top:</strong> {', '.join(concept['notes']['top'])}</p>
                        <p><strong>Middle:</strong> {', '.join(concept['notes']['middle'])}</p>
                        <p><strong>Base:</strong> {', '.join(concept['notes']['base'])}</p>
                    </details>
                    <button onclick="selectConcept{i}()">Select</button>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Select Concept {i+1}", key=f"select_concept_{i}"):
                    st.session_state.selected_concept = concept
                    st.session_state.current_stage = "accord"
                    st.experimental_rerun()

# Accord Development Stage
elif st.session_state.current_stage == "accord":
    st.header("2. Accord Development")
    
    if not st.session_state.selected_concept:
        st.error("No concept selected. Please go back to the concept stage.")
        if st.button("Return to Concept Stage"):
            st.session_state.current_stage = "concept"
            st.experimental_rerun()
    else:
        concept = st.session_state.selected_concept
        
        st.markdown(f"""
        <div class="fragrance-card">
            <h3 class="accent-header">{concept['name']}</h3>
            <p>{concept['description']}</p>
            <p><strong>Signature:</strong> {concept['signature']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        generate_fragrance_pyramid_image(
            concept['notes']['top'],
            concept['notes']['middle'],
            concept['notes']['base']
        )
        
        st.markdown("### Develop Accords")
        st.markdown("""
        Accords are the building blocks of a fragrance - combinations of ingredients that create
        a specific effect or impression. Let's develop the key accords for this fragrance.
        """)
        
        if st.button("Generate Accord Suggestions"):
            with st.spinner("Creating accord suggestions..."):
                prompt = f"""
                Create detailed accords for the fragrance concept "{concept['name']}" with the following notes:
                - Top Notes: {', '.join(concept['notes']['top'])}
                - Middle Notes: {', '.join(concept['notes']['middle'])}
                - Base Notes: {', '.join(concept['notes']['base'])}
                
                The concept is described as: {concept['description']}
                With signature element: {concept['signature']}
                
                For each accord, provide:
                1. A name that captures the essence of the accord
                2. A brief description of the accord's effect
                3. Key ingredients with approximate percentages
                4. How it contributes to the overall fragrance
                
                Create one accord for each of the three layers (top, middle, base), plus one signature accord that represents the unique selling point.
                
                Format your response as JSON with this structure:
                {
                    "top_accord": {
                        "name": "Name of Top Accord",
                        "description": "Description of top accord",
                        "ingredients": [
                            {"name": "Ingredient 1", "percentage": 5},
                            {"name": "Ingredient 2", "percentage": 3},
                            {"name": "Ingredient 3", "percentage": 2}
                        ],
                        "contribution": "How this accord contributes to the overall fragrance"
                    },
                    "middle_accord": {...},
                    "base_accord": {...},
                    "signature_accord": {...}
                }
                """
                
                response = call_openai_api(prompt)
                if response:
                    try:
                        accords = json.loads(response)
                        st.session_state.accords = accords
                        st.success("Accords generated successfully!")
                    except json.JSONDecodeError:
                        st.error("Error parsing response. Please try again.")
        
        # Display generated accords
        if 'accords' in st.session_state:
            st.markdown("### Developed Accords")
            
            tabs = st.tabs(["Top Accord", "Middle Accord", "Base Accord", "Signature Accord"])
            
            with tabs[0]:
                accord = st.session_state.accords["top_accord"]
                st.markdown(f"""
                <div class="fragrance-card">
                    <h3 class="accent-header">{accord['name']}</h3>
                    <p>{accord['description']}</p>
                    <p><strong>Contribution:</strong> {accord['contribution']}</p>
                    <h4>Ingredients:</h4>
                    <ul>
                    {"".join([f"<li>{ing['name']} - {ing['percentage']}%</li>" for ing in accord['ingredients']])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)
            
            with tabs[1]:
                accord = st.session_state.accords["middle_accord"]
                st.markdown(f"""
                <div class="fragrance-card">
                    <h3 class="accent-header">{accord['name']}</h3>
                    <p>{accord['description']}</p>
                    <p><strong>Contribution:</strong> {accord['contribution']}</p>
                    