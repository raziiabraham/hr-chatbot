import streamlit as st
import requests
import predict_similarity  # Import your similarity module
import time
import logging

# Configuration
API_BASE_URL = 'https://x8ki-letl-twmt.n7.xano.io/api:2Yytv5FJ'

# Set up logging
logging.basicConfig(level=logging.INFO)

# Function to update similarity score via the API
def update_similarity_score(interview_id, score):
    try:
        # Fetch the current interview details
        interview_response = requests.get(f"{API_BASE_URL}/job_interview/{interview_id}")
        if interview_response.status_code != 200:
            logging.error(f"Failed to fetch interview ID: {interview_id}, Status Code: {interview_response.status_code}")
            return False

        # Extract the existing data
        interview_data = interview_response.json()

        # Update similarity score
        interview_data["similarity_score"] = score

        # Send the updated record using PATCH
        patch_response = requests.patch(f"{API_BASE_URL}/job_interview/{interview_id}", json=interview_data)
        if patch_response.status_code != 200:
            logging.error(f"Failed to patch interview ID: {interview_id}, Status Code: {patch_response.status_code}, Response: {patch_response.text}")
        return patch_response.status_code == 200

    except Exception as e:
        logging.error(f"Exception occurred while updating interview ID: {interview_id}: {e}")
        return False

    finally:
        # Add a delay to ensure we do not exceed rate limits
        time.sleep(2)

# Function to create a new job via the API
def create_new_job(role_name, role_description):
    payload = {"role_name": role_name, "role_description": role_description}
    response = requests.post(f"{API_BASE_URL}/job_desc", json=payload)
    return response.status_code == 200

# Function to format text for better readability (replace with new line)
def format_text(text):
    return text.replace("\\", "\n\n").strip()

# Streamlit Interface
st.title("HR Job and Interview Management Dashboard")

# Add New Job Section
with st.expander("Add New Job (click to expand)"):
    with st.form("new_job_form"):
        role_name = st.text_input("Job Role Name")
        role_description = st.text_area("Job Role Description")
        submit_button = st.form_submit_button(label="Add New Job")

        if submit_button:
            if role_name and role_description:
                if create_new_job(role_name, role_description):
                    st.success("New job has been created successfully!")
                else:
                    st.error("Failed to create a new job.")
            else:
                st.error("Both role name and description are required.")

# Fetch and display list of jobs
jobs_response = requests.get(f"{API_BASE_URL}/job_desc")
if jobs_response.status_code == 200:
    jobs = jobs_response.json()
    job_options = {job["role_name"]: job["id"] for job in jobs}
    job_name = st.selectbox("Select a Job Role", list(job_options.keys()))
    selected_job_id = job_options.get(job_name, None)
else:
    st.error("Error fetching job list.")
    selected_job_id = None

# Fetch and display job description for the selected job
if selected_job_id:
    job_desc_response = requests.get(f"{API_BASE_URL}/job_desc/{selected_job_id}")
    if job_desc_response.status_code == 200:
        job_desc = job_desc_response.json()
        with st.expander("Job Description (click to expand)"):
            formatted_desc = format_text(job_desc["role_description"])
            st.write(formatted_desc)
    else:
        st.error("Error fetching job description.")

# Fetch and display list of interview summaries for the selected job along with similarity scores
all_interviews_response = requests.get(f"{API_BASE_URL}/job_interview")
if all_interviews_response.status_code == 200:
    all_interviews = all_interviews_response.json()
else:
    st.error("Error fetching interviews")

# Filter interviews related to selected job
if selected_job_id and 'all_interviews' in locals():
    interviews = [interview for interview in all_interviews if interview['job_desc_id'] == selected_job_id]
    
    # Sort the interviews by id in descending order
    interviews.sort(key=lambda x: x['id'], reverse=True)

    if interviews:
        st.subheader("Candidate Interviews")

        # A cache to avoid refetching candidate information
        candidate_cache = {}

        for interview in interviews:
            interview_summary = interview['summary']
            candidate_id = interview['candidate_id']

            # Fetch candidate name with caching
            if candidate_id not in candidate_cache:
                candidate_response = requests.get(f"{API_BASE_URL}/candidate/{candidate_id}")
                if candidate_response.status_code == 200:
                    candidate = candidate_response.json()
                    candidate_cache[candidate_id] = {
                        'name': candidate.get('name', 'Unknown Candidate'),
                        'email': candidate.get('email', 'Unknown Email')
                    }
                else:
                    candidate_cache[candidate_id] = {
                        'name': 'Unknown Candidate',
                        'email': 'Unknown Email'
                    }

            candidate_name = candidate_cache[candidate_id]['name']
            candidate_email = candidate_cache[candidate_id]['email']

            similarity_score = interview.get('similarity_score', None)
            interview_score = interview.get('interview_score', None)

            if similarity_score is None or similarity_score == 0:
                # Calculate similarity score if not available or zero
                similarity_score = predict_similarity.predict_similarity(interview_summary, job_desc["role_description"])

                # Update similarity score in the database
                if update_similarity_score(interview['id'], similarity_score):
                    st.success(f"Similarity score calculated and updated for interview ID: {interview['id']}")
                else:
                    st.error(f"Failed to update similarity score for interview ID: {interview['id']}")
                # Sleep for a bit to ensure DB consistency (optional)
                time.sleep(1)
            else:
                # If similarity score already exists and is valid.
                st.success(f"Existing similarity score is used for interview ID: {interview['id']}")

            # Display candidate information
            formatted_summary = format_text(interview_summary)
            st.markdown(f"**Candidate Name:** {candidate_name}")
            st.markdown(f"**Candidate Email:** {candidate_email}")
            st.markdown(f"**Interview Summary:** {formatted_summary}")
            st.markdown(f"**Similarity Score:** {similarity_score:.4f}")
            st.markdown(f"**Interview Score:** {interview_score}" if interview_score is not None else "**Interview Score:** Not Available")
            st.markdown("---")

            # Add a delay to ensure compliance with API rate limits
            time.sleep(2)
    else:
        st.text("No Interview submission for this Job ads.")
else:
    st.text("No Interview submission for this Job ads.")