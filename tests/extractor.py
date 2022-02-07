import os, json

def list_attributes(file):
    pass

def extract_from_tweets(file, attribute):
    if validate(file):
        with open(os.path.abspath(file), encoding='utf8') as f:
            data = json.load(f) 
            for tweet in data:  
                try:
                    print(f"{tweet['id']}, {attribute}: {tweet[attribute]}")  
                except Exception as e:
                    raise e

def validate(file):
    if file.lower().endswith('.json') & os.path.isfile(file):
        return True
    elif os.path.exists(file):
        print("Could not validate filetype. Please submit a .json file.") 
    else:
        print("File does not seem to exist. Please check that the path is correct.")  
    return False


extract_from_tweets('test_data.json', 'timestamp')