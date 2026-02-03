import io
import os
import boto3
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from shared.models import CarSale  #

# --- Configuration ---
DB_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@postgres-service:5432/sales")
S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://minio-service:9000")
S3_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET = os.getenv("S3_SECRET_KEY", "minioadmin")
BUCKET_NAME = "sales-data-lake"

# --- Initialization ---
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)
s3_client = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_KEY,
    aws_secret_access_key=S3_SECRET
)

def archive_stale_records(days_threshold=730):
    session = Session()
    cutoff_date = datetime.now() - timedelta(days=days_threshold)
    
    try:
        # 1. Identify "old" records
        query = session.query(CarSale).filter(CarSale.created_at < cutoff_date)
        df = pd.read_sql(query.statement, engine)

        if df.empty:
            print("No stale records found. The Archiver is resting.")
            return

        # 2. Convert to Parquet via in-memory buffer
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, engine='pyarrow', index=False)
        parquet_buffer.seek(0)

        # 3. Upload to MinIO
        file_name = f"archived_sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=parquet_buffer.getvalue()
        )
        print(f"Successfully archived {len(df)} records to {file_name}")

        # 4. Delete from Postgres
        ids_to_delete = df['uuid'].tolist()
        session.execute(
            delete(CarSale).where(CarSale.uuid.in_(ids_to_delete))
        )
        session.commit()
        print(f"Deleted {len(df)} records from Postgres.")

    except Exception as e:
        session.rollback()
        print(f"Error during archiving: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    archive_stale_records()