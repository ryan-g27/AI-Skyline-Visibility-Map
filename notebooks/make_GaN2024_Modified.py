import csv
from pathlib import Path
from PIL import Image

data_dir = Path(__file__).parent / 'data'
image_dir = Path(__file__).parent / 'Images'
input_file = data_dir / 'raw' / 'GaN2024.csv'
output_file = data_dir / 'processed' / 'GaN2024_Modified.csv'

#[lon_min, lat_min, lon_max, lat_max, width, height, filename]
continents = {
    "North America": [-180, 7, -51, 75, 15480, 8160, 'NorthAmerica2024.png'],
    "South America": [-93, -57, -33, 14, 7200, 8520, 'SouthAmerica2024.png'],
    "Europe":        [-32, 34, 70, 75, 12240, 4920, 'Europe2024.png'],
    "Africa":        [-26, -36, 64, 38, 10800, 8800, 'Africa2024.png'],
    "Asia":          [60, 5, 180, 75, 14400, 8400, 'Asia2024.png'],
    "Australia":     [94, -48, 180, 8, 10320, 6720, 'Australia2024.png']
}

light_pollution_scale = {
    (0, 0, 0): 0,
    (34, 34, 34): 1,
    (66, 66, 66): 2,
    (20, 47, 114): 3,
    (33, 84, 216): 4,
    (15, 87, 20): 5,
    (31, 161, 42): 6,
    (110, 100, 30): 7,
    (184, 166, 37): 8,
    (191, 100, 30): 9,
    (253, 150, 80): 10,
    (251, 90, 73): 11,
    (251, 153, 138): 12,
    (160, 160, 160): 13,
    (242, 242, 242): 14
}


def get_pollution_index(lat, lon):
    for name, bounds in continents.items():
        ln_min, lt_min, ln_max, lt_max, w, h, fname = bounds
        
        if ln_min <= lon <= ln_max and lt_min <= lat <= lt_max:
            img_path = image_dir / fname
            
            with Image.open(img_path) as img:
                img = img.convert('RGB')

                x = int(((lon - ln_min) / (ln_max - ln_min)) * (w - 1))
                y = int(((lt_max - lat) / (lt_max - lt_min)) * (h - 1))
                
                rgb = img.getpixel((x, y))
                if rgb in light_pollution_scale:
                    return light_pollution_scale[rgb]
                else:
                    print(f"Warning: RGB value {rgb} not found in scale. Location: {name} at ({lat}, {lon})")
                    return None
                
    return "Out of Range"

cloud_mapping = {'clear': '0', '1/4 of sky': '0.25', '1/2 of sky': '0.5', 'over 1/2 of sky': '0.75'}

min_mpsa = [22.00, 21.99, 21.93, 21.89, 21.81, 21.69, 21.51, 
               21.25, 20.91, 20.49, 20.02, 19.50, 18.95, 18.38, 17.80]

avg_mpsa = [21.995, 21.96, 21.91, 21.85, 21.75, 21.60, 21.38, 
              21.08, 20.70, 20.255, 19.76, 19.225, 18.665, 18.09, 17.80]

min_lpi = [0.0, 0.01, 0.06, 0.11, 0.19, 0.33, 0.58, 
                          1.0, 1.73, 3.0, 5.2, 9.0, 15.59, 27.0, 46.77]

avg_lpi = [0.005, 0.035, 0.085, 0.15, 0.26, 0.455, 0.79, 1.365, 2.365, 4.1, 7.1, 12.295, 21.295, 36.885, 46.77]

with open(input_file, mode='r', encoding='utf-8') as infile:
    reader = csv.DictReader(infile)
    fieldnames = [f for f in reader.fieldnames if f != 'SQMSerial'] + ['LightPollutionIndex', 'min_mpsa', 'avg_mpsa', 'min_lpi', 'avg_lpi']
    
    with open(output_file, mode='w', encoding='utf-8', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for row in reader:
            if (row['Latitude']==0 and row['Latitude']==0):
                continue
            
            row['CloudCover'] = cloud_mapping.get(row['CloudCover'], row['CloudCover'])
            
            row.pop('SQMSerial', None)

            
            lat = float(row['Latitude'])
            lon = float(row['Longitude'])
            row['LightPollutionIndex'] = get_pollution_index(lat, lon)
            
            # Add pollution scale values based on LightPollutionIndex (1-based index)
            if row['LightPollutionIndex'] is not None and row['LightPollutionIndex'] != "Out of Range":
                pollution_idx = int(row['LightPollutionIndex']) - 1
                row['min_mpsa'] = min_mpsa[pollution_idx]
                row['avg_mpsa'] = avg_mpsa[pollution_idx]
                row['min_lpi'] = min_lpi[pollution_idx]
                row['avg_lpi'] = avg_lpi[pollution_idx]
            else:
                row['min_mpsa'] = None
                row['avg_mpsa'] = None
                row['min_lpi'] = None
                row['avg_lpi'] = None
                
            writer.writerow(row)