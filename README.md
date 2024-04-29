# Data analysis for local plans

Experimenting with applying AI to Local Plans produced by planning authorities in England.

This code analyses Local Plan PDFs and adds data to a vector store

The repo also contains some noodling on ideas.

See https://github.com/jimmytidey/localplans-server for a front end

## Setting up the postgres DB

-- !!!! Installing the vector extension took nearly two hours.  
-- !!!! It would probably be best to run it from Heroku dataclips
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS text_fragments (
id SERIAL PRIMARY KEY,
metadata JSONB,
vector VECTOR(384),
plain_text TEXT,
full_text tsvector,
hash TEXT,
filename TEXT

);

-- Create a text search configuration for English
CREATE TEXT SEARCH CONFIGURATION IF NOT EXISTS english_simple_config ( COPY = simple );

ALTER TEXT SEARCH CONFIGURATION english_simple_config
ALTER MAPPING FOR asciiword, asciihword, hword_asciipart, word, hword, hword_part
WITH english_stem;

-- Alter the text column to use the English full-text search configuration
ALTER TABLE text_fragments
ALTER COLUMN full_text
SET DATA TYPE tsvector
USING to_tsvector('english_simple_config', text);

-- Create an index on the tsvector column for faster full-text searches
CREATE INDEX IF NOT EXISTS text_tsvector_index
ON text_fragments
USING gin(full_text);
