from fastapi import FastAPI, HTTPException, Response, status
from typing import List
from shared.database import get_db_connection, wait_for_db
from shared.models import CarSale
import logging

# Initialize FastAPI
app = FastAPI(title="Car Sales API", version="1.0.0")
logger = logging.getLogger(__name__)

@app.on_event("startup")
def startup_event():
    # Ensure DB is ready before the API starts accepting traffic
    if not wait_for_db():
        raise RuntimeError("Could not connect to database on startup")

# --- Endpoints ---

@app.get("/sales", response_model=List[CarSale])
def get_all_sales():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM car_sales ORDER BY created_at DESC")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results

@app.get("/sales/{sale_id}", response_model=CarSale)
def get_sale_by_id(sale_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM car_sales WHERE id = %s", (sale_id,))
    sale = cur.fetchone()
    cur.close()
    conn.close()
    
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

@app.post("/sales", status_code=status.HTTP_201_CREATED)
def add_sale(sale: CarSale):
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        INSERT INTO car_sales (make, model, year, vehicle_type, color, msrp)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, created_at;
    """
    cur.execute(query, (sale.make, sale.model, sale.year, sale.vehicle_type, sale.color, sale.msrp))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return {"id": row['id'], "created_at": row['created_at'], "status": "recorded"}

@app.put("/sales/{sale_id}")
def update_sale(sale_id: str, sale: CarSale):
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        UPDATE car_sales 
        SET make=%s, model=%s, year=%s, vehicle_type=%s, color=%s, msrp=%s
        WHERE id = %s
    """
    cur.execute(query, (sale.make, sale.model, sale.year, sale.vehicle_type, sale.color, sale.msrp, sale_id))
    
    if cur.rowcount == 0:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Sale not found")
        
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Sale updated successfully"}

@app.delete("/sales/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(sale_id: str):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM car_sales WHERE id = %s", (sale_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Sale not found")
        
    cur.execute("DELETE FROM car_sales WHERE id = %s", (sale_id,))
    conn.commit()
    cur.close()
    conn.close()
    return Response(status_code=status.HTTP_204_NO_CONTENT)