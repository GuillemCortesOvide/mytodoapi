import os

# Default database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/my_todo.db")

# Default test database URL
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///./tests/data/my_test_todo.db")
