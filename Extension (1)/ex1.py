#Machine Learning
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

#EXtension
import joblib
import os

# Load the dataset
df = pd.read_csv(r'C:\Users\arell\Documents\1_ALF\data\malicious_2021.csv', low_memory=False)

# Select features and target columns
features = ['Querylength', 'domain_token_count', 'path_token_count',
            'avgdomaintokenlen', 'longdomaintokenlen', 'avgpathtokenlen', 'tld',
            'charcompvowels', 'charcompace', 'ldl_url', 'ldl_domain', 'ldl_path',
            'ldl_filename', 'ldl_getArg', 'dld_domain', 'dld_path',
            'dld_filename', 'dld_getArg', 'urlLen', 'domainlength', 'pathLength',
            'subDirLen', 'fileNameLen', 'this.fileExtLen', 'ArgLen', 'pathurlRatio',
            'ArgUrlRatio', 'argDomanRatio', 'domainUrlRatio', 'pathDomainRatio',
            'argPathRatio', 'executable', 'isPortEighty', 'NumberofDotsinURL',
            'ISIpAddressInDomainName', 'CharacterContinuityRate',
            'LongestVariableValue', 'URL_DigitCount', 'host_DigitCount',
            'Directory_DigitCount', 'File_name_DigitCount', 'Extension_DigitCount',
            'Query_DigitCount', 'URL_Letter_Count', 'host_letter_count',
            'Directory_LetterCount', 'Filename_LetterCount',
            'Extension_LetterCount', 'Query_LetterCount', 'LongestPathTokenLength',
            'Domain_LongestWordLength', 'Path_LongestWordLength',
            'sub-Directory_LongestWordLength', 'Arguments_LongestWordLength',
            'URL_sensitiveWord', 'URLQueries_variable', 'spcharUrl',
            'delimeter_Domain', 'delimeter_path', 'delimeter_Count',
            'NumberRate_URL', 'NumberRate_Domain', 'NumberRate_DirectoryName',
            'NumberRate_FileName', 'NumberRate_Extension', 'NumberRate_AfterPath',
            'SymbolCount_URL', 'SymbolCount_Domain', 'SymbolCount_Directoryname',
            'SymbolCount_FileName', 'SymbolCount_Extension',
            'SymbolCount_Afterpath', 'Entropy_URL', 'Entropy_Domain', 'Entropy_Filename', 'Entropy_Extension',
            'Entropy_Afterpath', 'url_type']

# Clean the dataset by removing NaNs and infinities in numeric columns only
df_cleaned = df.copy()

# Convert 'tld' and 'url_type' to string since they're categorical
df_cleaned['tld'] = df_cleaned['tld'].astype(str)
df_cleaned['url_type'] = df_cleaned['url_type'].astype(str)

# Select only numeric features for checking infinite values
numeric_features = [f for f in features if f not in ['tld', 'url_type']]

# Apply np.isfinite only to numeric features and filter rows
df_cleaned = df_cleaned[np.isfinite(df_cleaned[numeric_features]).all(axis=1)]

# Label encoding for TLD and url_type (since they're categorical)
label_encoder_tld = LabelEncoder()
label_encoder_url_type = LabelEncoder()

df_cleaned['tld_encoded'] = label_encoder_tld.fit_transform(df_cleaned['tld'])
df_cleaned['url_type_encoded'] = label_encoder_url_type.fit_transform(df_cleaned['url_type'])

# Combine all features (numeric + 'tld_encoded') for the model
X = df_cleaned[numeric_features + ['tld_encoded']]

# Binary classification: Benign vs Malicious
df_cleaned['binary_label'] = df_cleaned['url_type'].apply(lambda x: 0 if x == 'benign' else 1)

# Train-Test Split for Binary Classification (Benign vs Malicious)
X_train_bin, X_test_bin, y_train_bin, y_test_bin = train_test_split(
    X, df_cleaned['binary_label'], test_size=0.3, random_state=42, stratify=df_cleaned['binary_label']
)

# Initialize the XGBoost classifier for binary classification
c_binary = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)

# Fit the model on the training data for binary classification
c_binary.fit(X_train_bin, y_train_bin)


# Multiclass Classification for types of malicious URLs
# Only consider the non-benign entries
malicious_df = df_cleaned[df_cleaned['binary_label'] == 1].copy()

# Use the 'url_type_encoded' column for the target
X_multi = malicious_df[numeric_features + ['tld_encoded']]
y_multi = malicious_df['url_type_encoded']

# Train-Test Split for Multiclass Classification
X_train_multi, X_test_multi, y_train_multi, y_test_multi = train_test_split(
    X_multi, y_multi, test_size=0.3, random_state=42, stratify=y_multi
)

# Adjust the multiclass labels so that they start from 0
y_train_multi = y_train_multi - 1
y_test_multi = y_test_multi - 1

# Initialize the XGBoost classifier for multiclass classification
c_multi = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)

# Fit the model on the training data for multiclass classification
c_multi.fit(X_train_multi, y_train_multi)

# Specify the folder path where you want to save the model
folder_path = '../extension/ml'
os.makedirs(folder_path, exist_ok=True)  # This will create the folder if it doesn't exist

# Save the trained model to a file
joblib.dump(c_binary, os.path.join(folder_path,'binary model.pkl'))
joblib.dump(c_multi, os.path.join(folder_path,'multiclass model.pkl'))

