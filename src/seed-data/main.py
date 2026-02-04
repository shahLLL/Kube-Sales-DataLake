import os
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

# Using the exact keys from your Kubernetes Secrets/ConfigMaps
DB_URL = os.environ.get("DATABASE_URL")

def seed_data(num_records=200):
    if not DB_URL:
        print("Error: DATABASE_URL environment variable not set.")
        return

    engine = create_engine(DB_URL)
    
    makes = ["Toyota", "Ford", "Honda", "Tesla", "BMW", "Hyundai"]
    v_types = ["sedan", "suv", "coupe", "convertible"]
    colors = ["Red", "Blue", "Black", "Silver", "White"]

    with engine.connect() as conn:
        print(f"Connecting to DB and seeding {num_records} records...")
        
        for i in range(num_records):
            # 50% chance of being "Stale" (Older than 2 years/730 days)
            # 50% chance of being "Fresh" (Within the last 6 months)
            if random.random() > 0.5:
                days_ago = random.randint(740, 1100) # Archive bait
            else:
                days_ago = random.randint(1, 180)    # Should stay in DB

            created_at = datetime.now() - timedelta(days=days_ago)
            
            conn.execute(
                text("""
                    INSERT INTO car_sales (make, model, year, vehicle_type, color, msrp, created_at)
                    VALUES (:make, :model, :year, :v_type, :color, :msrp, :created_at)
                """),
                {
                    "make": random.choice(makes),
                    "model": "Generic Model",
                    "year": random.randint(2015, 2025),
                    "v_type": random.choice(v_types),
                    "color": random.choice(colors),
                    "msrp": random.uniform(22000, 75000),
                    "created_at": created_at
                }
            )
        conn.commit()
    print("✅ Seeding complete! Database is now populated with mixed-age records.")

if __name__ == "__main__":
    seed_data(500)