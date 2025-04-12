CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    uid VARCHAR(255) UNIQUE NOT NULL,        -- UID do utilizador (Firebase, por exemplo)
    role ENUM('admin', 'user') NOT NULL,
    imei VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);