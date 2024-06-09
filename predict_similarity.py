import numpy as np
from gensim.models import Word2Vec
import nltk
from nltk.tokenize import word_tokenize
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter

# Load the trained model
model = Word2Vec.load('resume_word2vec.model')

# Ensure nltk dependencies are downloaded
nltk.download('punkt')

# Function to get the weighted Word2Vec embedding for a text_string
def get_weighted_text_string_embedding(model, text_string):
    tokens = word_tokenize(text_string.lower())
    token_freq = Counter(tokens)  # Get frequency of each token
    word_vectors = [(model.wv[token] * token_freq[token]) for token in tokens if token in model.wv]
    weights = [token_freq[token] for token in tokens if token in model.wv]
    
    if not word_vectors:
        return np.zeros(model.vector_size)
    
    weighted_embedding = np.average(word_vectors, axis=0, weights=weights)
    return weighted_embedding

# Function to compute weighted cosine similarity
def predict_similarity(interview_summary_str, job_description):
    # Get weighted embeddings for job description and interview summary string
    job_description_embedding = get_weighted_text_string_embedding(model, job_description)
    new_resume_embedding = get_weighted_text_string_embedding(model, interview_summary_str)
    
    similarity = cosine_similarity([job_description_embedding], [new_resume_embedding])[0][0]
    return similarity

"""
# Example of predicting similarity
job_description = "About Asseti\
Asseti is a cloud-based Intelligent Asset Management platform that provides critical condition insights to real estate portfolio owners. With Asseti, owners reduce uncertainty around capital expenditure and are able to predict future spend and condition in their portfolios. Asseti is used extensively in Australia, and is gaining strong traction in our go-to-market in the United States, with significant growth in private and government customers alike.\
Introduction\
We are seeking a well-rounded Data Scientist to join our rapidly-growing team. This role requires a strong background in Python, with a particular focus on Python’s ML toolkit, and good grounding in Pandas and GeoPandas. The ideal candidate will be proficient in building and maintaining models that are robust and scalable. Experience working with Imaging and Geospatial data is highly desirable. Good business acumen and communication skills are essential, as the role will be working closely with our teams in Product, Marketing and Dev.\
Key Responsibilities\
Maintain and enhance our existing ML models and code base in Python.\
Work with Product/Marketing/Dev leads to gather requirements, develop, and implement new ML models as needed by the business.\
Perform Analytics on our existing data assets, and report on findings to inform the design of new models and overall product performance.\
Report on opportunities to continually improve our models and code base, for both accuracy and computational efficiency.\
Required Skills and Qualifications:\
Bachelor\'s degree in Computer Science, Astrophysics, Medical Imaging, or a related discipline in computational/imaging/geospatial Science.\
3+ years experience of Data Science related work (preferably in Python), either in industry or in academia.\
Deep understanding of ML techniques and methodologies, particularly Convolutional Neural Networks and similar.\
Strong experience with data analytics and visualisation.\
Comfortable with linear algebra and maths in general.\
Demonstrated ability to build and test ML models, and explain results using a variety of complementary metrics.\
Excellent problem-solving skills, attention to detail, and commitment to code quality.\
Effective communication skills and the ability to work collaboratively in a team environment.\
Preferred Skills:\
Experience with Image transformation and GeoSpatial coordinate systems.\
Experience with photogrammetry and computational geometry in a geospatial context. \
Experience with AI and machine learning technologies in a geospatial context."
interview_summary_str = "I have been a product manager for the last 7 years with focus on artificial intelligence and machine learning. And now I'm studying Master of AI in Business, in Sydney, Australia."

similarity_score = predict_similarity(interview_summary_str, job_description)
print(f"Similarity Score: {similarity_score}")
"""