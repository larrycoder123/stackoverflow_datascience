import nltk
import csv
import xml.etree.ElementTree as ET

nltk.download("averaged_perceptron_tagger")
nltk.download("averaged_perceptron_tagger_eng")
nltk.download("stopwords")
nltk.download("wordnet")

import preproc as pp # Import preproc after nltk download - preproc requires installed nltk data

def clean_text(text):        
    rm_stops_text = pp.remove_stops(text)
    rm_features_text = pp.remove_features(rm_stops_text)
    tagged_text = pp.tag_and_remove(rm_features_text)    
    lemm_text = pp.lemmatize(tagged_text)

    if (len(lemm_text.strip()) == 0):
        return None
    
    return lemm_text

def cleanup_posts(input_posts_file, output_posts_file):
    row_count = 0
    export_count = 0

    export_columns = [
        "Id",
        "PostTypeId",
        "Score",
        "Title",
        "Body",
        "Tags",
        "ViewCount",
        "AnswerCount",
        "CommentCount",
        "CreationDate",
        "ClosedDate"
    ]

    with open(input_posts_file, "rb") as input_file, open(output_posts_file, "w", encoding="utf-8", newline='') as output_file:

        writer = csv.DictWriter(output_file, fieldnames=export_columns, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()

        for event, elem in ET.iterparse(input_file, events=("end",)):
            if elem.tag == "row":
                row_count += 1

                post_type_id = elem.get("PostTypeId", "")
                creation_date = elem.get("CreationDate", "")
                creation_date_year = creation_date[:4] # "YYYY-MM-DD..."

                if row_count % 500_000 == 0:
                    print(f"Processing: {row_count:,} / {creation_date} / {export_count:,}")
                                
                if post_type_id == "1" and creation_date_year == "2024":
                    row_data = {}

                    for col in export_columns:
                        row_data[col] = elem.attrib.get(col, "")
                    
                    row_data["Title"] = clean_text(row_data["Title"])
                    row_data["Body"] = clean_text(row_data["Body"])

                    for int_col in ["Id", "PostTypeId", "Score", "ViewCount", "AnswerCount", "CommentCount"]:
                        row_data[int_col] = int(row_data[int_col])

                    if (row_data["Title"] != None and row_data["Body"] != None):
                        writer.writerow(row_data)
                        export_count += 1

            elem.clear()

posts_input_path = "./data/Posts.xml"
posts_output_path = "./data/Posts_Cleaned_2024.csv"

cleanup_posts(posts_input_path, posts_output_path)
