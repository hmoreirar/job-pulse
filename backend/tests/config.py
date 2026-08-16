import os

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+psycopg://test:test@localhost:5432/test",
)
