import os
import django
import pandas as pd
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_prj.settings")  # Replace 'your_project_name' with your project name
django.setup()

def load_geojson(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            geojson_data = json.load(file)

        features = geojson_data.get('features', [])
        print(f"Found {len(features)} features in the GeoJSON file.")
        data = pd.DataFrame(features)

        print("GeoJSON data successfully loaded.")

    except Exception as e:
        print(f"Error loading GeoJSON data: {str(e)}")

if __name__ == "__main__":
    geojson_file = 'HangJeongDong_ver20241001.geojson'
    load_geojson(geojson_file)
