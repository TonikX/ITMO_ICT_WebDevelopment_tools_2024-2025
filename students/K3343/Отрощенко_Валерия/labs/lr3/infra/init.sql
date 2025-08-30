CREATE TABLE IF NOT EXISTS hackathon (
  id SERIAL PRIMARY KEY,
  title TEXT,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);