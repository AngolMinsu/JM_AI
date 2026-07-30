CREATE TABLE ecu_nodes (
    node_id INTEGER PRIMARY KEY AUTOINCREMENT,
    node_name TEXT NOT NULL,
    mcu_model TEXT NOT NULL,
    can_baudrate INTEGER,
    fw_version TEXT,
    status TEXT DEFAULT 'ACTIVE',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);