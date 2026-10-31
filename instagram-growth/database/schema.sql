-- Optional: the app also creates these tables automatically on first start.
CREATE DATABASE IF NOT EXISTS instagram_growth_db
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE instagram_growth_db;

CREATE TABLE IF NOT EXISTS admins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL UNIQUE,
  password_hash VARCHAR(255) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  instagram_username VARCHAR(30) NOT NULL,
  mobile_number VARCHAR(15) NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_user_identity (instagram_username, mobile_number),
  INDEX ix_users_username (instagram_username)
);

CREATE TABLE IF NOT EXISTS plans (
  id INT AUTO_INCREMENT PRIMARY KEY,
  plan_name VARCHAR(100) NOT NULL,
  follower_quantity INT NOT NULL,
  price DECIMAL(10,2) NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS orders (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  plan_id INT NOT NULL,
  amount DECIMAL(10,2) NOT NULL,
  order_status VARCHAR(20) NOT NULL DEFAULT 'Pending',
  payment_status VARCHAR(10) NOT NULL DEFAULT 'Unpaid',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (plan_id) REFERENCES plans(id),
  INDEX ix_orders_user (user_id),
  INDEX ix_orders_status (order_status)
);

INSERT INTO plans (plan_name, follower_quantity, price)
SELECT * FROM (
  SELECT '500 Followers', 500, 99.00 UNION ALL
  SELECT '1K Followers', 1000, 199.00 UNION ALL
  SELECT '5K Followers', 5000, 499.00 UNION ALL
  SELECT '10K Followers', 10000, 899.00
) AS seed
WHERE NOT EXISTS (SELECT 1 FROM plans);
