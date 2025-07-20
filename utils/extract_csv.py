import csv

def extract_text_from_csv(file_path):
    try:
        with open(file_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = ["\t".join(row) for row in reader]
        return "\n".join(rows)
    except Exception as e:
        return f"[CSV extract failed: {str(e)}]"
