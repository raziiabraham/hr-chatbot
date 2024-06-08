import ssl
import pandas as pd
from gensim.models import Word2Vec
import nltk
from nltk.tokenize import word_tokenize

# Disable SSL verification for NLTK downloads
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Ensure nltk dependencies are downloaded
nltk.download('punkt')

# Load dataset
df = pd.read_csv('resume.csv')

# Tokenize resumes
df['Tokenized_Resume'] = df['Resume_str'].apply(lambda x: word_tokenize(x.lower()))

# Print the number of resumes
print(f"Number of resumes: {len(df)}")

# Create and train the Word2Vec model
model = Word2Vec(sentences=df['Tokenized_Resume'].tolist(), vector_size=100, window=5, min_count=1, workers=4)

# Save the model
model.save('resume_word2vec.model')

print("Model trained and saved.")