import os

# Override compose hostnames with localhost for pytest environments
os.environ["POSTGRES_HOST"] = os.getenv("POSTGRES_HOST", "localhost")
os.environ["REDIS_HOST"] = os.getenv("REDIS_HOST", "localhost")
