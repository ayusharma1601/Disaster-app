import csv
from datetime import datetime
from typing import Dict, List, Tuple

# Bounding box for Assam, India (FR-011)
ASSAM_BOUNDS = {
    "min_lat": 24.0,
    "max_lat": 28.2,
    "min_lon": 89.7,
    "max_lon": 96.1
}

def validate_coordinates(lat: float, lon: float) -> bool:
    return (ASSAM_BOUNDS["min_lat"] <= lat <= ASSAM_BOUNDS["max_lat"]) and \
           (ASSAM_BOUNDS["min_lon"] <= lon <= ASSAM_BOUNDS["max_lon"])

def validate_and_parse_csv(filepath: str) -> Dict:
    valid_rows = []
    rejected_rows = []
    
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            try:
                # State verification (SRS Test T-002)
                state = row.get("state", "").strip()
                if state.lower() != "assam":
                    rejected_rows.append({
                        "row": idx,
                        "data": row,
                        "reason": f"Geographic mismatch: State '{state}' is not Assam (Pilot area requirement)"
                    })
                    continue

                lat = float(row["latitude"])
                lon = float(row["longitude"])
                if not validate_coordinates(lat, lon):
                    rejected_rows.append({
                        "row": idx,
                        "data": row,
                        "reason": f"Coordinates ({lat}, {lon}) are outside Assam bounding limits"
                    })
                    continue

                val_str = row.get("value", "").strip()
                val = float(val_str) if val_str != "" else None  # FR-015: Keep missing as None

                parsed_row = {
                    "station_name": row.get("station_name", "Unknown Station").strip(),
                    "station_type": row.get("station_type", "Rainfall").strip(),
                    "latitude": lat,
                    "longitude": lon,
                    "district": row.get("district", "Kamrup Metropolitan").strip(),
                    "variable": row.get("variable", "rainfall_24h").strip(),
                    "value": val,
                    "unit": row.get("unit", "mm").strip(),
                    "observed_at": datetime.strptime(row["observed_at"].strip(), "%Y-%m-%d %H:%M:%S"),
                    "is_simulated": row.get("is_simulated", "true").lower() == "true",
                    "quality_flag": "VALID" if val is not None else "MISSING"
                }
                valid_rows.append(parsed_row)

            except Exception as e:
                rejected_rows.append({
                    "row": idx,
                    "data": row,
                    "reason": f"Parsing error: {str(e)}"
                })

    return {
        "total_rows": len(valid_rows) + len(rejected_rows),
        "valid_count": len(valid_rows),
        "rejected_count": len(rejected_rows),
        "valid_rows": valid_rows,
        "rejected_rows": rejected_rows
    }
