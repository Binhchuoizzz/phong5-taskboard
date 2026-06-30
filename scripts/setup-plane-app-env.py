import os
import secrets

PROJECT_ROOT = "/home/binhchuoiz/Projects/Personal/NoteAppC12"
env_local_path = os.path.join(PROJECT_ROOT, "env", ".env.local")
plane_env_path = os.path.join(PROJECT_ROOT, "plane-app", "plane.env")

# 1. Read secrets from env/.env.local
variables = {}
if os.path.exists(env_local_path):
    with open(env_local_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                variables[key.strip()] = val.strip()

pg_pass = variables.get("POSTGRES_PASSWORD", secrets.token_urlsafe(24))
secret_key = variables.get("SECRET_KEY", secrets.token_hex(32))
minio_pass = variables.get("MINIO_ROOT_PASSWORD", secrets.token_urlsafe(24))
rabbit_pass = variables.get("RABBITMQ_DEFAULT_PASS", secrets.token_urlsafe(24))
live_secret = secrets.token_hex(32)

print(f"Loaded credentials. PostgreSQL Pass length: {len(pg_pass)}, MinIO Pass length: {len(minio_pass)}, RabbitMQ Pass length: {len(rabbit_pass)}")

# 2. Modify plane-app/plane.env
if os.path.exists(plane_env_path):
    with open(plane_env_path, "r") as f:
        lines = f.readlines()
    
    new_lines = []
    for line in lines:
        if line.startswith("POSTGRES_PASSWORD="):
            line = f"POSTGRES_PASSWORD={pg_pass}\n"
        elif line.startswith("RABBITMQ_PASSWORD="):
            line = f"RABBITMQ_PASSWORD={rabbit_pass}\n"
        elif line.startswith("AWS_SECRET_ACCESS_KEY="):
            line = f"AWS_SECRET_ACCESS_KEY={minio_pass}\n"
        elif line.startswith("AWS_ACCESS_KEY_ID="):
            line = "AWS_ACCESS_KEY_ID=plane-minio\n"
        elif line.startswith("SECRET_KEY="):
            line = f"SECRET_KEY={secret_key}\n"
        elif line.startswith("LIVE_SERVER_SECRET_KEY="):
            line = f"LIVE_SERVER_SECRET_KEY={live_secret}\n"
        elif line.startswith("DATABASE_URL="):
            line = f"DATABASE_URL=postgresql://plane:{pg_pass}@plane-db:5432/plane\n"
        elif line.startswith("AMQP_URL="):
            line = f"AMQP_URL=amqp://plane:{rabbit_pass}@plane-mq:5672/plane\n"
        elif line.startswith("REDIS_URL="):
            line = "REDIS_URL=redis://plane-redis:6379/\n"
        elif line.startswith("CORS_ALLOWED_ORIGINS="):
            line = "CORS_ALLOWED_ORIGINS=http://localhost\n"
        elif line.startswith("WEB_URL="):
            line = "WEB_URL=http://localhost\n"
        elif line.startswith("APP_DOMAIN="):
            line = "APP_DOMAIN=localhost\n"
        new_lines.append(line)
        
    with open(plane_env_path, "w") as f:
        f.writelines(new_lines)
    print("Updated plane-app/plane.env with secure credentials and inline URLs.")
else:
    print("Error: plane-app/plane.env not found!")
