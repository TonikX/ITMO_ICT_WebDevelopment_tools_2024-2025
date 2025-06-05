\c hockey_db;

-- Роли
INSERT INTO roles (role_name) VALUES ('admin') ON CONFLICT (role_name) DO NOTHING;
INSERT INTO roles (role_name) VALUES ('user') ON CONFLICT (role_name) DO NOTHING;

-- Админ (логин: admin, пароль: admin123)
INSERT INTO users (username, email, password_hash, name, surname, status)
VALUES ('admin', 'admin@hockey.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeA8EQ/1Y5e.QdG6.', 'Admin', 'User', 'active')
ON CONFLICT (username) DO NOTHING;

-- Связка админ-роль (самое важное!)
INSERT INTO users_roles (user_id, role_id)
VALUES (
    (SELECT user_id FROM users WHERE username = 'admin' LIMIT 1),
    (SELECT role_id FROM roles WHERE role_name = 'admin' LIMIT 1)
) ON CONFLICT DO NOTHING;

-- Базовый сезон для парсера
INSERT INTO seasons (year) VALUES ('2024/2025') ON CONFLICT (year) DO NOTHING;