-- Shared Car Sales Schema
CREATE TABLE IF NOT EXISTS car_sales (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    vehicle_type VARCHAR(20) NOT NULL CHECK (vehicle_type IN ('coupe', 'convertible', 'sedan', 'suv')),
    color VARCHAR(20) NOT NULL,
    msrp NUMERIC(12, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for the Archiver, Helps the archiver find old records quickly
CREATE INDEX IF NOT EXISTS idx_created_at ON car_sales(created_at);