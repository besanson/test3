import streamlit as st
import openai
import plotly.express as px
import pandas as pd

# Title and Introduction
st.set_page_config(layout="wide")
st.title("AI-driven Flavour and Fragrance Creation Dashboard")
st.write("An intuitive dashboard for creating, evaluating, and refining unique scents and flavours using advanced AI technology.")

# Sidebar for OpenAI API key and model selection
st.sidebar.header("Settings")
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
model_choice = st.sidebar.selectbox("Select AI Model", ["gpt-4-turbo", "gpt-4", "gpt-3.5-turbo"], index=0)

if not openai_api_key:
    st.warning("Enter your OpenAI API key in the sidebar to continue.")
else:
    client = openai.OpenAI(api_key=openai_api_key)

    # Main Dashboard
    st.header("Dashboard")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Active Projects", value="3")
    with col2:
        st.metric(label="Formulations Generated", value="12")
    with col3:
        st.metric(label="Frequently Used Ingredient", value="Citrus Oil")

    st.subheader("Recent Activity")
    recent_activity = pd.DataFrame({
        "Activity": ["New formulation generated", "Feedback provided", "Project updated"],
        "Project": ["Summer Breeze", "Spicy Delight", "Fresh Morning"],
        "Time": ["2 mins ago", "10 mins ago", "1 hour ago"]
    })
    st.dataframe(recent_activity, use_container_width=True)

    st.divider()

    # Create New Project
    st.header("Create or Select Project")
    project_name = st.text_input("Project Name")
    if st.button("Create New Project"):
        st.success(f"Project '{project_name}' created!")

    # Module 1: Define Target Scent/Flavour Profile
    st.header("Module 1: Define Target Scent/Flavour Profile")
    col1, col2 = st.columns(2)
    with col1:
        prompt = st.text_area("Natural Language Input", placeholder="Describe your scent or flavour...")
    with col2:
        descriptors = ["Fruity", "Floral", "Spicy", "Sweet", "Sour", "Woody", "Creamy", "Nutty", "Fresh", "Herbal"]
        selected_descriptors = st.multiselect("Select descriptors:", descriptors)

    st.subheader("Adjust Sensory Intensity")
    descriptor_values = {}
    descriptor_cols = st.columns(len(selected_descriptors))
    for i, desc in enumerate(selected_descriptors):
        with descriptor_cols[i]:
            descriptor_values[desc] = st.slider(desc, 0, 7, 3)

    # Module 2: AI Processing and Formulation Generation
    if st.button("Generate Formulations"):
        with st.spinner("AI is analyzing and generating formulations..."):
            ai_prompt = f"Generate a detailed fragrance/flavour formulation based on: {prompt}. Descriptors: {descriptor_values}."
            completion = client.chat.completions.create(
                model=model_choice,
                messages=[{"role": "system", "content": "Create a detailed scent/flavour formulation based on given descriptors and intensities."},
                          {"role": "user", "content": ai_prompt}]
            )

            formulation = completion.choices[0].message.content

        # Module 3: Formulation Output and Comparison
        st.header("Module 3: Generated Formulation")
        col1, col2 = st.columns(2)
        with col1:
            st.write(formulation)

        with col2:
            sensory_fig = px.line_polar(r=list(descriptor_values.values()), theta=list(descriptor_values.keys()), line_close=True, title="Predicted Sensory Profile")
            st.plotly_chart(sensory_fig, use_container_width=True)

        # Module 4: Feedback and Refinement
        st.header("Module 4: Feedback and Refinement")
        feedback_rating = st.slider("Overall Satisfaction", 1, 5, 3)
        feedback_text = st.text_area("Qualitative Feedback", placeholder="Provide specific feedback...")

        if st.button("Generate Refined Variation"):
            with st.spinner("Generating refined formulation based on feedback..."):
                refine_prompt = f"Original: {formulation}\nRating: {feedback_rating}/5\nFeedback: {feedback_text}\nGenerate refined formulation."
                refined_completion = client.chat.completions.create(
                    model=model_choice,
                    messages=[{"role": "system", "content": "Refine the scent/flavour formulation based on user feedback."},
                              {"role": "user", "content": refine_prompt}]
                )

                refined_formulation = refined_completion.choices[0].message.content

            st.subheader("Refined Formulation")
            st.write(refined_formulation)

            st.success("Refinement completed successfully!")

    # Module 5: Advanced Analysis and Visualisation
    st.header("Module 5: Advanced Analysis")
    st.write("Coming soon: Detailed molecular structure visualization, odor activity value predictions, and stability analysis.")
