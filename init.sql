ALTER USER postgres WITH PASSWORD 'postgres';

DROP TABLE IF EXISTS Book;

CREATE TABLE Book(
    id SERIAL PRIMARY KEY,
    name TEXT,
    author TEXT,
    year INT,
    path TEXT NOT NULL,
    UNIQUE(name, author, year),
    UNIQUE(path)
);
