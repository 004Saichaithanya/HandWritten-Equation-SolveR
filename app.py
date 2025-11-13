import streamlit as st
from File_uploader import upload_image
from LLM import analyze_image
import traceback
import json

# Streamlit page setup
st.set_page_config(page_title="🧮 Handwritten Equation Solver", layout="centered")

st.title("🧠 AI Handwritten Equation Solver")
st.write("Upload an image containing a mathematical equation — the AI will analyze and solve it step by step!")

# File uploader
uploaded_file = st.file_uploader("📤 Choose an image", type=["png", "jpg", "jpeg", "gif"])

if uploaded_file is not None:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    st.write(f"✅ **File Name:** `{uploaded_file.name}`  \n📏 **Size:** {uploaded_file.size / 1024:.2f} KB")

    if st.button("🧩 Solve Equation"):
        with st.spinner("☁️ Uploading image to Cloudinary..."):
            try:
                st.info("Connecting to Cloudinary...")
                image_url = upload_image(uploaded_file)
                st.success("✅ Image uploaded successfully!")
                st.write("🌐 **Image URL:**", image_url)
                print(f"[DEBUG] Image URL: {image_url}")
            except Exception as e:
                st.error(f"❌ Cloudinary upload failed: {e}")
                print("[ERROR] Cloudinary upload failed:")
                traceback.print_exc()
                st.stop()

        with st.spinner("🤖 AI is analyzing the equation..."):
            try:
                print("[DEBUG] Calling analyze_image()...")
                result = analyze_image(image_url)
                print("[DEBUG] Raw LLM response:")
                print(result)

                st.divider()
                st.subheader("🧩 Step-by-Step Solution")

                # If the result is in JSON form with steps/final_answer
                if isinstance(result, dict) and "steps" in result:
                    for i, step in enumerate(result.get("steps", []), start=1):
                        st.markdown(f"**Step {i}:** {step}")
                    st.markdown(f"### ✅ Final Answer: {result.get('final_answer', 'N/A')}")
                else:
                    # fallback display
                    st.write(result)

                st.success("🎯 Problem Solved Successfully!")

            except Exception as e:
                st.error(f"API request failed: {e}")
                print("[ERROR] API request failed:")
                traceback.print_exc()
