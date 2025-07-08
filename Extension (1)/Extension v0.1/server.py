from flask import Flask, request, jsonify
import joblib
from flask_cors import CORS
from sklearn.preprocessing import LabelEncoder
import urllib.parse
import math
from collections import Counter  
import re
import numpy as np
import pandas as pd

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load RandomForestClassifier and its selected features
rf_classifier, selected_features = joblib.load(r'C:\Users\arell\Documents\1_ALF\newnew\improved.pkl')

# TLD LabelEncoder should be fit on the entire dataset
tld_encoder = LabelEncoder()

# Function to predict whether a URL is benign or malicious
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    url = data.get('url')

    # Extract features from the URL
    features = extract_features(url)

    # Check the length of the features
    print(f"Extracted features length: {len(features)}")  # Ensure it's 20 (or whatever number of features you need)

    # Create a DataFrame with the correct feature names
    features_df = pd.DataFrame([features], columns=selected_features)
    print(f"Features DataFrame:\n{features_df}")  # Debugging print

    # Get predicted probabilities for both classes
    prob = rf_classifier.predict_proba(features_df)

    # Set a custom threshold for classification
    threshold = 0.7  # You can adjust this value

    # prob[0][1] is the probability of the URL being malicious (class 1)
    if prob[0][1] > threshold:
        result = {'status': 'malicious', 'probability': prob[0][1]}
    else:
        result = {'status': 'benign', 'probability': prob[0][1]}

    return jsonify(result)

# Feature extraction from URL
def extract_features(url):
    # Ensure the URL has a scheme (http:// or https://)
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    features = {}

    # Parsing URL components
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path
    query = parsed_url.query
    tld = domain.split('.')[-1] if '.' in domain else ''
    
    # Helper functions
    def char_count(text, chars):
        return sum(1 for c in text if c in chars)
    
    def entropy(text):
        if len(text) == 0:
            return 0
        probabilities = [n_x / len(text) for x, n_x in Counter(text).items()]
        return -sum(p * math.log2(p) for p in probabilities if p > 0)

    def character_continuity_rate(text):
        if len(text) == 0:
            return 0
        max_continuous = 0
        current_count = 1
        for i in range(1, len(text)):
            if text[i] == text[i - 1]:
                current_count += 1
            else:
                max_continuous = max(max_continuous, current_count)
                current_count = 1
        max_continuous = max(max_continuous, current_count)
        return max_continuous / len(text)

    # Feature calculations with checks for missing values
    domain_tokens = domain.split('.') if domain else []
    path_tokens = path.split('/') if path else []
    query_tokens = query.split('&') if query else []
    
    domain_letter_count = sum(len(token) for token in domain_tokens) if domain_tokens else 0
    path_letter_count = sum(len(token) for token in path_tokens) if path_tokens else 0
    domain_digit_count = char_count(domain, '0123456789') if domain else 0

    # Handle missing or zero-length components by setting default values
    features['domain_token_count'] = len(domain_tokens) if domain_tokens else 0
    features['path_token_count'] = len(path_tokens) if path_tokens else 0
    features['avgdomaintokenlen'] = domain_letter_count / len(domain_tokens) if domain_tokens else 0
    features['longdomaintokenlen'] = max(len(token) for token in domain_tokens) if domain_tokens else 0
    features['ldl_domain'] = len(domain) if domain else 0
    features['ldl_path'] = len(path) if path else 0
    features['subDirLen'] = len('/'.join(path_tokens[:-1])) if path_tokens else 0
    features['pathurlRatio'] = len(path) / len(url) if url else 0
    features['argDomanRatio'] = len(query) / len(domain) if domain else 0
    features['domainUrlRatio'] = len(domain) / len(url) if url else 0
    features['NumberofDotsinURL'] = url.count('.') if url else 0
    features['CharacterContinuityRate'] = character_continuity_rate(url) if url else 0
    features['host_DigitCount'] = domain_digit_count
    features['host_letter_count'] = domain_letter_count
    features['Directory_LetterCount'] = path_letter_count
    features['Domain_LongestWordLength'] = max(len(token) for token in domain_tokens) if domain_tokens else 0
    features['sub-Directory_LongestWordLength'] = max(len(token) for token in path_tokens[:-1]) if len(path_tokens) > 1 else 0

    # Adding additional features (with default values for missing parts)
    features['URLQueries_variable'] = len(query_tokens) if query_tokens else 0
    features['delimeter_Domain'] = domain.count('.') if domain else 0
    features['delimeter_Count'] = url.count('/') + url.count('?') + url.count('&') if url else 0
    features['SymbolCount_URL'] = char_count(url, "!@#$%^&*()_+{}:\"<>?[];',./\\|`~") if url else 0
    
    # Print extracted features for debugging
    print(f"Extracted features for URL '{url}':")
    print(features)

    # Return the 20 features, ensuring all are filled even if some were missing
    return [features.get(key, 0) for key in selected_features]


if __name__ == '__main__':
    app.run(debug=True)
