import glob
import csv

print("Caut fișiere cu mișcare (Viteză > 0)...\n")
for filepath in glob.glob("src/collector/dataset_obd/*.csv"):
    with open(filepath, 'r') as f:
        reader = csv.DictReader(f)
        speed_col = next((c for c in reader.fieldnames if c and 'SPEED' in c.upper()), None)
        
        if speed_col:
            for row in reader:
                val = row.get(speed_col, '0')
                if val and val.replace('.','',1).isdigit() and float(val) > 0:
                    print(f"✅ {filepath.split('/')[-1]} are date de condus!")
                    break # Trecem la următorul fișier