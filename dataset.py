import pandas as pd
from sqlalchemy import create_engine
import xml.etree.ElementTree as ET
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
import joblib

def parse_xml_to_dataframe(file_path):
    # Load and parse the XML file
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Define an empty list to store the extracted data
    data = []

    for review in root.findall('.//Review'):
        review_id = review.attrib['rid']
        for sentence in review.findall('.//sentence'):
            sentence_id = sentence.attrib['id']
            text = sentence.find('text').text
            for opinion in sentence.findall('.//Opinion'):
                # Extracting attributes from each Opinion
                record = {
                    'Review ID': review_id,
                    'Sentence ID': sentence_id,
                    'Text': text,
                    'Target': opinion.attrib['target'],
                    'Category': opinion.attrib['category'],
                    'Polarity': opinion.attrib['polarity'],
                    'From': opinion.attrib['from'],
                    'To': opinion.attrib['to']
                }
                data.append(record)

    # Convert the list into a DataFrame
    df = pd.DataFrame(data)

    return df


def clean_string(input_string):
    # Check if the input is None
    if input_string is None:
        return "Null"

    # Split the string by '#'
    parts = input_string.split('#')

    # Remove quotation marks from each part
    transformed_parts = [part.replace('"', '') for part in parts]

    # Replace underscores with spaces and capitalize the first letter of each word
    transformed_parts = [part.replace('_', ' ').capitalize() for part in transformed_parts]
    
    # Join the parts back into a single string with spaces
    output_string = ' '.join(transformed_parts)
    
    return output_string


def get_data():
    absa16 = parse_xml_to_dataframe('dataset/ABSA16_Restaurants_Train_SB1_v2.xml')
    test_data_gold = parse_xml_to_dataframe('dataset/Test Data - Gold Annotations - Subtask 1 - Restaurant Reviews - English.xml')
    trial_data = parse_xml_to_dataframe('dataset/Trial Data - Subtask 1 - Restaurant Reviews - English.xml')

    merged_df = pd.concat([absa16, test_data_gold, trial_data], ignore_index=True)

    merged_df = merged_df[['Target', 'Category', 'Polarity']]
    merged_df['Target'] = merged_df['Target'].apply(clean_string)
    merged_df['Category'] = merged_df['Category'].apply(clean_string)
    merged_df = merged_df.dropna()

    return merged_df


engine = create_engine('sqlite:///metrics.sqlite')
def store_metrics(merged_df):
    target_counts = merged_df['Target'].value_counts()
    category_counts = merged_df['Category'].value_counts()
    polarity_counts = merged_df['Polarity'].value_counts()
    # Store to sqlite database
    target_counts.to_sql('target_counts', con=engine, if_exists='replace')
    category_counts.to_sql('category_counts', con=engine, if_exists='replace')
    polarity_counts.to_sql('polarity_counts', con=engine, if_exists='replace')


model_path = 'model.pkl'
def build_model(merged_df):

    # Assuming 'target' and 'category' are of type string
    categorical_transformer = OneHotEncoder(handle_unknown='ignore')

    preprocessor = ColumnTransformer(
        transformers=[
            ('target', categorical_transformer, ['Target']),
            ('category', categorical_transformer, ['Category'])
        ])

    X = merged_df.drop(['Polarity'], axis=1)
    y = merged_df['Polarity']

    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', RandomForestClassifier(n_estimators=100, random_state=42))
    ])
    model.fit(X, y)

    # Store the model
    joblib.dump(model, model_path)
