"""Create knowledge_articles table manually since migration didn't actually create it."""
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('152.136.115.121', username='ubuntu', password='Aa782997781.', timeout=20)

sql = """
CREATE TABLE IF NOT EXISTS knowledge_articles (
    id BIGSERIAL PRIMARY KEY,
    category_id BIGINT NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    author_id BIGINT NOT NULL,
    tags JSON NULL,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    status VARCHAR(50) NOT NULL,
    published_at TIMESTAMP NULL,
    summary TEXT NULL,
    cover_image VARCHAR(255) NULL,
    created_at TIMESTAMP NULL,
    updated_at TIMESTAMP NULL
);
CREATE INDEX IF NOT EXISTS idx_ka_category_id ON knowledge_articles (category_id);
CREATE INDEX IF NOT EXISTS idx_ka_author_id ON knowledge_articles (author_id);
CREATE INDEX IF NOT EXISTS idx_ka_status ON knowledge_articles (status);
CREATE INDEX IF NOT EXISTS idx_ka_published_at ON knowledge_articles (published_at);
ALTER TABLE knowledge_articles ADD CONSTRAINT knowledge_articles_category_id_foreign FOREIGN KEY (category_id) REFERENCES knowledge_categories(id) ON DELETE RESTRICT;
ALTER TABLE knowledge_articles ADD CONSTRAINT knowledge_articles_author_id_foreign FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE RESTRICT;
"""

cmd = f"PGPASSWORD=oa_pg_pwd_782997781 psql -h 127.0.0.1 -U oa_user -d security_oa -c \"{sql}\" 2>&1 | head -30"
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
out = stdout.read().decode('utf-8', errors='replace')
print(out)
err = stderr.read().decode('utf-8', errors='replace')
if err: print(f"ERR: {err[:500]}")

client.close()
