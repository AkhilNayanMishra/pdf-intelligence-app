import json

def format_json(data):
    return json.dumps(data, indent=2)

def save_to_file(file_path, data_str):
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(data_str)
    