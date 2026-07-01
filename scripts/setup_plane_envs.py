import os
import secrets

# Resolve PROJECT_ROOT dynamically relative to this script's location
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLANE_DIR = os.path.join(PROJECT_ROOT, "plane")

# 1. Read secrets from env/.env.local
env_local_path = os.path.join(PROJECT_ROOT, "env", ".env.local")
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

print(f"Loaded credentials. PostgreSQL Pass length: {len(pg_pass)}, MinIO Pass length: {len(minio_pass)}, RabbitMQ Pass length: {len(rabbit_pass)}")

# 2. Copy and configure root .env
root_example = os.path.join(PLANE_DIR, ".env.example")
root_env = os.path.join(PLANE_DIR, ".env")

with open(root_example, "r") as f:
    root_lines = f.readlines()

new_root_lines = []
for line in root_lines:
    if line.startswith("POSTGRES_PASSWORD="):
        line = f'POSTGRES_PASSWORD="{pg_pass}"\n'
    elif line.startswith("RABBITMQ_PASSWORD="):
        line = f'RABBITMQ_PASSWORD="{rabbit_pass}"\n'
    elif line.startswith("AWS_SECRET_ACCESS_KEY="):
        line = f'AWS_SECRET_ACCESS_KEY="{minio_pass}"\n'
    elif line.startswith("AWS_ACCESS_KEY_ID="):
        line = 'AWS_ACCESS_KEY_ID="plane-minio"\n'
    elif line.startswith("MINIO_ROOT_PASSWORD="):
        line = f'MINIO_ROOT_PASSWORD="{minio_pass}"\n'
    elif line.startswith("MINIO_ROOT_USER="):
        line = 'MINIO_ROOT_USER="plane-minio"\n'
    elif line.startswith("LISTEN_HTTP_PORT="):
        line = 'LISTEN_HTTP_PORT=80\n'
    elif line.startswith("LISTEN_HTTPS_PORT="):
        line = 'LISTEN_HTTPS_PORT=443\n'
    new_root_lines.append(line)

with open(root_env, "w") as f:
    f.writelines(new_root_lines)
print("Created root .env file")

# 3. Copy and configure apps/api/.env
api_example = os.path.join(PLANE_DIR, "apps", "api", ".env.example")
api_env = os.path.join(PLANE_DIR, "apps", "api", ".env")

with open(api_example, "r") as f:
    api_lines = f.readlines()

new_api_lines = []
secret_key_present = False
for line in api_lines:
    if line.startswith("POSTGRES_PASSWORD="):
        line = f'POSTGRES_PASSWORD="{pg_pass}"\n'
    elif line.startswith("RABBITMQ_PASSWORD="):
        line = f'RABBITMQ_PASSWORD="{rabbit_pass}"\n'
    elif line.startswith("AWS_SECRET_ACCESS_KEY="):
        line = f'AWS_SECRET_ACCESS_KEY="{minio_pass}"\n'
    elif line.startswith("AWS_ACCESS_KEY_ID="):
        line = 'AWS_ACCESS_KEY_ID="plane-minio"\n'
    elif line.startswith("SECRET_KEY="):
        line = f'SECRET_KEY="{secret_key}"\n'
        secret_key_present = True
    elif line.startswith("USE_MINIO="):
        line = 'USE_MINIO=1\n'
    elif line.startswith("WEB_URL="):
        line = 'WEB_URL="http://localhost:8000"\n'
    new_api_lines.append(line)

if not secret_key_present:
    new_api_lines.append(f'\nSECRET_KEY="{secret_key}"\n')

# Ensure DATABASE_URL and REDIS_URL are correct and resolve inline
# Line 12 in apps/api/.env.example: DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
# Let's write them explicitly to be safe
final_api_lines = []
for line in new_api_lines:
    if line.startswith("DATABASE_URL="):
        line = f'DATABASE_URL=postgresql://plane:{pg_pass}@plane-db:5432/plane\n'
    elif line.startswith("REDIS_URL="):
        line = 'REDIS_URL="redis://plane-redis:6379/"\n'
    final_api_lines.append(line)

with open(api_env, "w") as f:
    f.writelines(final_api_lines)
print("Created apps/api/.env file")

# 4. Copy other apps examples to .env
apps = ["web", "space", "admin", "live"]
for app in apps:
    app_example = os.path.join(PLANE_DIR, "apps", app, ".env.example")
    app_env = os.path.join(PLANE_DIR, "apps", app, ".env")
    if os.path.exists(app_example):
        with open(app_example, "r") as sf:
            content = sf.read()
        with open(app_env, "w") as df:
            df.write(content)
        print(f"Created apps/{app}/.env file")

print("All environment files copied and configured successfully!")
