import io
import os
import sys
import boto3
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker

# Import shared utilities and models
from shared.database import wait_for_db
from shared.models import CarSaleORM

# --- Configuration ---
# Fetching from environment variables as per project standards
DB_URL = os.environ.get("DATABASE_URL")
S3_ENDPOINT = os.environ.get("S3_ENDPOINT")
S3_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET = os.environ.get("S3_SECRET_KEY")
BUCKET_NAME = os.environ.get("BUCKET_NAME")
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS"))

# --- Initialization ---
engine = create_engine(DB_URL)
Session = sessionmaker(bind=engine)


def archive_stale_records():
    """
    Identifies records older than the threshold, converts them to Parquet,
    uploads to MinIO, and removes them from Postgres.
    """
    session = Session()
    cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
    
    try:
        # 1. Identify "old" records based on created_at schema
        query = session.query(CarSaleORM).filter(CarSaleORM.created_at < cutoff_date)
        df = pd.read_sql(query.statement, engine)

        if df.empty:
            print("No stale records found. The Janitor's work is done for now.")
            return
        else:
            if 'id' in df.columns:
                df['id'] = df['id'].astype(str)

        # 2. Convert to Parquet via in-memory buffer (using PyArrow engine)
        parquet_buffer = io.BytesIO()
        df.to_parquet(parquet_buffer, engine='pyarrow', index=False)
        parquet_buffer.seek(0)

        # 3. Upload to MinIO Data Lake
        s3_client = boto3.client(
            "s3",
            endpoint_url=S3_ENDPOINT,
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET
        )
        
        file_name = f"archived_sales_{datetime.now().strftime('%Y%m%d_%H%M%S')}.parquet"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=file_name,
            Body=parquet_buffer.getvalue()
        )
        print(f"Successfully archived {len(df)} records to {file_name}")

        # 4. Delete archived records from Postgres to free up space
        ids_to_delete = df['id'].tolist()
        session.execute(
            delete(CarSaleORM).where(CarSaleORM.id.in_(ids_to_delete))
        )
        session.commit()
        print(f"Deleted {len(df)} stale records from the primary database.")

    except Exception as e:
        session.rollback()
        print(f"Critical error during archival process: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    # Integration of shared wait_for_db logic
    print("Archiver starting up...")
    if wait_for_db(retries=10, delay=5):
        archive_stale_records()
    else:
        print("Could not reach database. Archiver exiting.")
        sys.exit(1)