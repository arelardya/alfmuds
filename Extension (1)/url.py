import re
import urllib.parse
import math
from collections import Counter
from itertools import groupby  
import pandas as pd

# Load CSV
df = pd.read_csv(r'C:\Users\arell\Documents\1_ALF\data\source.csv')

# Feature Extraction Function
def extract_url_features(url):
    features = {}
    
    # Parsing URL components
    parsed_url = urllib.parse.urlparse(url)
    domain = parsed_url.netloc
    path = parsed_url.path
    query = parsed_url.query
    filename = path.split('/')[-1] if '/' in path else ''
    file_ext = filename.split('.')[-1] if '.' in filename else ''
    tld = domain.split('.')[-1] if '.' in domain else ''

    # Helper Functions
    def tokenize(text, delimiters='/.-_'):
        regex_pattern = f"[{re.escape(delimiters)}]"
        return re.split(regex_pattern, text)
    
    def char_count(text, chars):
        return sum(1 for c in text if c in chars)
    
    def entropy(text):
        probabilities = [n_x / len(text) for x, n_x in Counter(text).items()]
        return -sum([p * math.log2(p) for p in probabilities])
    
    # Feature Extraction
    features['Querylength'] = len(query)
    
    # Token counts and lengths
    domain_tokens = tokenize(domain)
    path_tokens = tokenize(path)
    query_tokens = tokenize(query, delimiters='=&')

    features['domain_token_count'] = len(domain_tokens)
    features['path_token_count'] = len(path_tokens)
    features['avgdomaintokenlen'] = sum(len(t) for t in domain_tokens) / len(domain_tokens) if domain_tokens else 0
    features['longdomaintokenlen'] = max(len(t) for t in domain_tokens) if domain_tokens else 0
    features['avgpathtokenlen'] = sum(len(t) for t in path_tokens) / len(path_tokens) if path_tokens else 0
    features['tld'] = tld
    
    # Character Composition
    features['charcompvowels'] = char_count(url, 'aeiou')
    features['charcompace'] = url.count(' ')
    
    # Lengths (ldl_ and dld_)
    features['ldl_url'] = len(url)
    features['ldl_domain'] = len(domain)
    features['ldl_path'] = len(path)
    features['ldl_filename'] = len(filename)
    features['ldl_getArg'] = len(query)
    
    # Path and Directory
    features['subDirLen'] = len('/'.join(path.split('/')[:-1]))
    features['this.fileExtLen'] = len(file_ext)
    features['ArgLen'] = len(query)

    # Ratios
    features['pathurlRatio'] = len(path) / len(url) if url else 0
    features['ArgUrlRatio'] = len(query) / len(url) if url else 0
    features['argDomanRatio'] = len(query) / len(domain) if domain else 0
    features['domainUrlRatio'] = len(domain) / len(url) if url else 0
    features['pathDomainRatio'] = len(path) / len(domain) if domain else 0
    features['argPathRatio'] = len(query) / len(path) if path else 0
    
    # Executable and Port Detection
    features['executable'] = 1 if file_ext in ['exe', 'bin', 'sh'] else 0
    features['isPortEighty'] = 1 if parsed_url.port == 80 or parsed_url.port is None else 0
    
    # Digit, Letter, and Symbol Counts
    digits = '0123456789'
    letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    special_chars = "!@#$%^&*()_+{}:\"<>?[];',./\\|`~"
    
    features['NumberofDotsinURL'] = url.count('.')
    features['ISIpAddressInDomainName'] = 1 if re.match(r'^\d+\.\d+\.\d+\.\d+$', domain) else 0
    features['CharacterContinuityRate'] = max(len(list(g)) for k, g in groupby(url)) / len(url) if url else 0
    features['LongestVariableValue'] = max(len(t) for t in query_tokens) if query_tokens else 0
    
    # Digit counts
    features['URL_DigitCount'] = char_count(url, digits)
    features['host_DigitCount'] = char_count(domain, digits)
    features['Directory_DigitCount'] = char_count(path, digits)
    features['File_name_DigitCount'] = char_count(filename, digits)
    features['Extension_DigitCount'] = char_count(file_ext, digits)
    features['Query_DigitCount'] = char_count(query, digits)

    # Letter counts
    features['URL_Letter_Count'] = char_count(url, letters)
    features['host_letter_count'] = char_count(domain, letters)
    features['Directory_LetterCount'] = char_count(path, letters)
    features['Filename_LetterCount'] = char_count(filename, letters)
    features['Extension_LetterCount'] = char_count(file_ext, letters)
    features['Query_LetterCount'] = char_count(query, letters)

    # Longest token lengths
    features['LongestPathTokenLength'] = max(len(token) for token in path_tokens) if path_tokens else 0
    features['Domain_LongestWordLength'] = max(len(token) for token in domain_tokens) if domain_tokens else 0
    features['Path_LongestWordLength'] = max(len(token) for token in path_tokens) if path_tokens else 0
    features['sub-Directory_LongestWordLength'] = max(len(token) for token in tokenize('/'.join(path.split('/')[:-1]))) if path_tokens else 0
    features['Arguments_LongestWordLength'] = max(len(token) for token in query_tokens) if query_tokens else 0
    
    # Sensitive words and variables
    features['URL_sensitiveWord'] = 1 if any(word in url.lower() for word in ['secure', 'login', 'password']) else 0
    features['URLQueries_variable'] = len(query_tokens)
    
    # Delimiters and symbols
    features['spcharUrl'] = char_count(url, special_chars)
    features['delimeter_Domain'] = domain.count('.')
    features['delimeter_path'] = path.count('/')
    features['delimeter_Count'] = url.count('/') + url.count('?') + url.count('&')
    
    # Number Rates
    features['NumberRate_URL'] = features['URL_DigitCount'] / len(url) if url else 0
    features['NumberRate_Domain'] = features['host_DigitCount'] / len(domain) if domain else 0
    features['NumberRate_DirectoryName'] = features['Directory_DigitCount'] / len(path) if path else 0
    features['NumberRate_FileName'] = features['File_name_DigitCount'] / len(filename) if filename else 0
    features['NumberRate_Extension'] = features['Extension_DigitCount'] / len(file_ext) if file_ext else 0
    features['NumberRate_AfterPath'] = features['Query_DigitCount'] / len(query) if query else 0
    
    # Symbol Counts
    features['SymbolCount_URL'] = char_count(url, special_chars)
    features['SymbolCount_Domain'] = char_count(domain, special_chars)
    features['SymbolCount_Directoryname'] = char_count(path, special_chars)
    features['SymbolCount_FileName'] = char_count(filename, special_chars)
    features['SymbolCount_Extension'] = char_count(file_ext, special_chars)
    features['SymbolCount_Afterpath'] = char_count(query, special_chars)
    
    # Entropy
    features['Entropy_URL'] = entropy(url)
    features['Entropy_Domain'] = entropy(domain)
    features['Entropy_Filename'] = entropy(filename)
    features['Entropy_Extension'] = entropy(file_ext)
    features['Entropy_Afterpath'] = entropy(query)

    return features

# Feature Extraction
features_list = []
for index, row in df.iterrows():
    url = row['url']
    url_type = row['type']
    
    features = extract_url_features(url)
    features['url_type'] = url_type  # Add url_type as a feature
    
    features_list.append(features)

# Convert to DataFrame
features_df = pd.DataFrame(features_list)

# Save to CSV
features_df.to_csv('malicious_2021.csv', index=False)

print("Extracted CSV has been saved as 'malicious_2021.csv'")
