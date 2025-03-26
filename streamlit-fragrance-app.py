import streamlit as st
import openai
import pandas as pd
import plotly.express as px

# Set up OpenAI API Key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Title and Introduction
st.title("AI-driven Flavour and Fragrance Creator")
st.write("Easily craft unique scents and flavours using intuitive descriptions and AI-powered formulation suggestions.")

# Step 1: User defines target
st.header("Define Your Target")
input_method = st.radio("Choose input method:", ["Natural Language Prompt", "Descriptor Selection"])

if input_method == "Natural Language Prompt":
    prompt = st.text_area("Describe your desired flavour or fragrance:", placeholder="e.g., a fresh, zesty citrus aroma with a hint of sweetness")
else:
    descriptors = ["Fruity", "Floral", "Spicy", "Sweet", "Sour", "Woody", "Creamy", "Nutty", "Fresh", "Herbal"]
    selected_descriptors = st.multiselect("Select descriptors:", descriptors)
    prompt = "A scent/flavour with attributes: " + ", ".join(selected_descriptors)

# Optional Parameters
st.subheader("Optional: Set specific intensity parameters")
sweetness = st.slider("Sweetness Intensity", 0, 7, 3)
citrus = st.slider("Citrus Intensity", 0, 7, 3)
woody = st.slider("Woody Intensity", 0, 7, 3)

if st.button("Generate Formulations"):
    with st.spinner("Generating potential formulations..."):
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI expert flavourist and perfumer, creating formulations based on user descriptions."},
                {"role": "user", "content": f"Generate a fragrance/flavour formulation for: {prompt}. Include ingredients and their proportions. Sweetness: {sweetness}/7, Citrus: {citrus}/7, Woody: {woody}/7."}
            ]
        )

        formulation = completion.choices[0].message.content

    # Display generated formulation
    st.header("AI-Generated Formulation")
    st.write(formulation)

    # Simulate Sensory Profile Visualization
    attributes = {"Sweetness": sweetness, "Citrus": citrus, "Woody": woody}
    fig = px.line_polar(r=attributes.values(), theta=attributes.keys(), line_close=True, title="Predicted Sensory Profile")
    st.plotly_chart(fig)

    # User Feedback
    st.header("Evaluate and Refine")
    rating = st.slider("Rate this formulation", 1, 5, 3)
    feedback = st.text_input("Provide additional feedback", placeholder="e.g., too floral, not enough citrus")

    if st.button("Generate Refined Variation"):
        with st.spinner("Refining formulation based on feedback..."):
            refined_completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Refine the formulation based on user feedback."},
                    {"role": "user", "content": f"Original formulation: {formulation}. User rating: {rating}/5. Feedback: {feedback}. Generate a refined version."}
                ]
            )

            refined_formulation = refined_completion.choices[0].message.content

        st.subheader("Refined Formulation")
        st.write(refined_formulation)

        # Indicate iterative refinement
        st.success("Refinement completed! You can further adjust parameters or provide additional feedback.")
