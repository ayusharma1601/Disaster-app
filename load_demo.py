import csv
from sqlalchemy.orm import Session
import models
from database import engine, SessionLocal

def load_demo_data():
    models.Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Clear existing to prevent duplicates during demo runs
    db.query(models.RainfallRecord).delete()
    
    records_to_insert = []
    with open("demo_data.csv", "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rainfall = float(row["rainfall_mm"]) if row["rainfall_mm"] else None
            record = models.RainfallRecord(
                state=row["state"],
                district=row["district"],
                latitude=float(row["latitude"]),
                longitude=float(row["longitude"]),
                rainfall_mm=rainfall,
                is_simulated_data=True  # As per instructions, clearly tag simulated data
            )
            records_to_insert.append(record)
    
    db.bulk_save_objects(records_to_insert)
    db.commit()
    print(f"Inserted {len(records_to_insert)} demo records.")

if __name__ == "__main__":
    load_demo_data()
