INSERT INTO users (user_id, email, full_name, phone, password_hash, is_active) VALUES
    ('DRIVER-001', 'driver1@example.com', 'Vikram Rao', '+91-9876543210', '$2b$12$mdvw5DZQexlqsprCGqr5euBHLifKx57xBbFolH4R6eGo8WmwwoI/C', TRUE),
    ('DRIVER-002', 'driver2@example.com', 'Anjali Desai', '+91-9876543211', '$2b$12$mdvw5DZQexlqsprCGqr5euBHLifKx57xBbFolH4R6eGo8WmwwoI/C', TRUE)
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO garages (garage_id, name, address, spots_total, spots_available) VALUES
    ('GARAGE-001', 'Downtown Parking Garage', '12 Market Street', 200, 200),
    ('GARAGE-002', 'Airport Parking', '1 Terminal Road', 500, 500)
ON CONFLICT (garage_id) DO NOTHING;
