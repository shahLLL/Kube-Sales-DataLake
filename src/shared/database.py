import os
import time
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging to see the connection attempts in Kubernetes logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Establishes a connection to Postgres using a mandatory environment variable.
    """
    try:
        # Use .environ[] to ensure we fail fast if the variable is missing
        db_url = os.environ["DATABASE_URL"]
    except KeyError:
        logger.critical("DATABASE_URL environment variable is MISSING. Check K8s Secrets.")
        raise

    return psycopg2.connect(db_url, cursor_factory=RealDictCursor)

def wait_for_db(retries: int = 5, delay: int = 3):
    """
    Attempts to connect to the database multiple times before giving up.
    Prevents the API from crashing while Postgres is still booting up.
    """
    logger.info("Initializing database connection check...")
    
    for attempt in range(1, retries + 1):
        try:
            conn = get_db_connection()
            # Execute a simple query to verify the connection is alive
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
            conn.close()
            logger.info("Database is READY. Proceeding to start application.")
            return True
        except Exception as e:
            logger.warning(
                f"Database connection attempt {attempt}/{retries} failed. "
                f"Retrying in {delay} seconds... (Error: {e})"
            )
            time.sleep(delay)
            
    logger.critical("Could not connect to the database after multiple attempts. Exiting.")
    return False