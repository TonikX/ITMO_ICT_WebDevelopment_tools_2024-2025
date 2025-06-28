-- Создание таблицы для хранения результатов парсинга
CREATE TABLE IF NOT EXISTS pages (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT,
    execution_time DECIMAL(10, 4),
    method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_pages_url ON pages(url);
CREATE INDEX IF NOT EXISTS idx_pages_created_at ON pages(created_at);
CREATE INDEX IF NOT EXISTS idx_pages_method ON pages(method);

-- Вставка тестовых данных
INSERT INTO pages (url, title, execution_time, method) VALUES
('https://my.itmo.ru', 'ИТМО - Санкт-Петербургский национальный исследовательский университет информационных технологий, механики и оптики', 0.5, 'async'),
('https://www.github.com', 'GitHub: Let''s build from here', 0.3, 'async'),
('https://www.stackoverflow.com', 'Stack Overflow - Where Developers Learn, Share, & Build Careers', 0.4, 'async')
ON CONFLICT DO NOTHING; 