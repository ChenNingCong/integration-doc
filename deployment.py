import os
import subprocess

# load .env variables from a .env file if it exists
from dotenv import load_dotenv
load_dotenv()
# TODO: configurate 
# ACCESS_TOKEN_SECRET in forum-gateway
# JWT_SECRET and SERVICE_KEY in forum-auth-service
# SERVICE_KEY and DB in forum-user-service
# MONGO_URI and MONGO_PASSWORD for post & reply service
# configuration for email
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=chenningcong393069484@gmail.com
# SMTP_PASSWORD=<16 character password here>
# SMTP_FROM_EMAIL=noreply@yourapp.com
# SMTP_FROM_NAME=Final-project

"""
first step, kill all node processes to avoid port conflicts
| Backend URL | Port | Route | Description |
|---|---|---|---|
| `http://localhost:3000` | 3000 | `/*` | Frontend Page |
| `http://localhost:8080` | 8080 | `/api/health` | Self-referencing Gateway |
| `http://localhost:8001` | 8001 | `/api/auth/*` | Auth Microservice |
| `http://localhost:8002` | 8002 | `/api/users/*` | User Microservice |
| `http://localhost:8003` | 8003 | `/api/posts/*`, `/api/replies/*` | Post & Reply Microservice |
| `http://localhost:8004` | 8004 | `/api/messages/*` | Message Microservice |
| `http://localhost:8005` | 8005 | `/api/history/*` | History Microservice |
| `http://localhost:8006` | 8006 | `/api/files/*` | File Microservice |
| `http://localhost:8007` | 8007 | `/api/internal/email*` | Email Microservice |
"""
def validate_env():
    required_vars = ["ACCESS_TOKEN_SECRET", "MONGO_URI", "MONGO_PASSWORD"]
    missing_vars = [var for var in required_vars if var not in os.environ]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

"""
Try to use different input/output log file for each service to avoid conflicts
"""
def run_server(server_type:str, cmd, cwd=None, check=True):
    print(f"🚀 Starting {server_type} server with command: {' '.join(cmd)}")
    os.makedirs(f"logs/{server_type}", exist_ok=True)
    with open(f"logs/{server_type}/output.log", "w") as out, open(f"logs/{server_type}/error.log", "w") as err:
        # run in the background
        subprocess.Popen(cmd, cwd=cwd, stdout=out, stderr=err, start_new_session=True)



REPOS = [
    "https://github.com/ChenNingCong/forum-gateway",
    "https://github.com/pgwpwei/forum-email-service",
    "https://github.com/pgwpwei/forum-frontend",
    "https://github.com/pgwpwei/forum-post-reply-service",
    "https://github.com/pgwpwei/forum-file-service",
    "https://github.com/pgwpwei/forum-message-service",
    "https://github.com/pgwpwei/forum-history-service",
    "https://github.com/pgwpwei/forum-user-service",
    "https://github.com/pgwpwei/forum-auth-service"
]

def sync():
    for url in REPOS:
        # Extract folder name from URL
        repo_name = url.split('/')[-1]
        repo_path = os.path.join(os.getcwd(), repo_name)
        
        # Check if the directory exists and is a git repo
        if os.path.exists(repo_path) and os.path.isdir(os.path.join(repo_path, ".git")):
            # print(f"🔄 Resetting and updating: {repo_name}")
            try:
                # Reset tracked files to discard local changes
                # subprocess.run(["git", "-C", repo_path, "reset", "--hard", "HEAD"], check=True)
                # Pull latest code
                subprocess.run(["git", "-C", repo_path, "pull"], check=True)
            except subprocess.CalledProcessError:
                print(f"❌ Failed to update {repo_name}")
        else:
            print(f"🚀 Cloning new service: {repo_name}")
            try:
                subprocess.run(["git", "clone", url], check=True)
            except subprocess.CalledProcessError:
                print(f"❌ Failed to clone {repo_name}")


def kill_node_processes():
    for port in [3000, 8080, 8001, 8002, 8003, 8004, 8005, 8006, 8007]:
        try:
            # Find and kill node processes on the specified port
            result = subprocess.run(["lsof", "-t", f"-i:{port}"], capture_output=True, text=True)
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(["kill", "-9", pid])
                    print(f"🛑 Killed process {pid} on port {port}")
        except Exception as e:
            print(f"❌ Error killing processes on port {port}: {e}")


"""
3. Gateway setup
   1.  Run `git clone https://github.com/ChenNingCong/forum-gateway` to download the gateway codes (Joe is not here today so I will use my own version of gateway).
   2.  Create a `.env` file in the root directory with the following line (this is for JWT token). Any token works.:
   `ACCESS_TOKEN_SECRET=8efaf6d52fa6d6674e6f9f27d72e0a76285a7be1b93772d7e90f5639c28449c58686f37203f45a629ca4b22d3af7751848ed34cab37297d6f159ee99b835c9de`
   3.  Run `npm install` and `npm start server.js`.
   4.  (Test): go to `http://localhost:8080/api/health` and you should see a "OK" message.
   5.  (Test): If you launch both the frontend and the gateway, go to `http://localhost:3000` you should see the login page.
"""
def setup_gateway():
    gateway_path = os.path.join(os.getcwd(), "forum-gateway")
    env_file_path = os.path.join(gateway_path, ".env")
    # First, remove existing .env file if it exists
    if os.path.exists(env_file_path):
        os.remove(env_file_path)
    # Create .env file with ACCESS_TOKEN_SECRET
    with open(env_file_path, 'w') as env_file:
        env_file.write(f"ACCESS_TOKEN_SECRET={os.getenv('ACCESS_TOKEN_SECRET')}\n")
    
    print("⚙️  Setting up gateway...")
    try:
        # Install dependencies
        subprocess.run(["npm", "install"], cwd=gateway_path, check=True)
        # Start the server
        run_server("forum-gateway", ["npm", "start", "server.js"], cwd=gateway_path, check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to set up the gateway.")
    # check health endpoint
    try:
        result = subprocess.run(["curl", "http://localhost:8080/api/health"], capture_output=True, text=True)
        if "OK" in result.stdout:
            print("✅ Gateway is healthy.")
        else:
            print("❌ Gateway health check failed.")
    except subprocess.CalledProcessError:
        print("❌ Failed to perform gateway health check.")

"""
2. Frontend setup
   1. Inside the `project` folder, run `git clone https://github.com/pgwpwei/forum-frontend` to download the frontend code.
   2. Run `npm install` and `npm run dev -- --port 3000` to launch the development server on port `3000`.
   3. (Test): go to `http://localhost:3000` and you should see a "Loading authentication" page.
"""
def setup_frontend():
    # cd to forum-frontend temporarily
    frontend_path = os.path.join(os.getcwd(), "forum-frontend")
    print("⚙️  Setting up frontend...")
    try:
        # Install dependencies
        subprocess.run(["npm", "install"], cwd=frontend_path, check=True)
        # Start the development server on port 3000
        run_server("forum-frontend", ["npm", "run", "dev", "--", "--port", "3000"], cwd=frontend_path, check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to set up the frontend.")

"""4. Post & Reply Service setup
## Setup Instructions

### Install Dependencies
```bash
npm install
```

### Running the Test Server
Use the in-memory database implementation:
```bash
npm run dev test.config.yaml
```

### Running the Production Server

1. Create a credentials file at `secrets/secret.env`:
```
   MONGO_URI=mongodb+srv://chenningcong393069484_db_user:<PASSWORD>@cluster0.4pa51vd.mongodb.net/?appName=Cluster0
   MONGO_PASSWORD=your_password_here
```
   Note: Keep the `<PASSWORD>` placeholder in `MONGO_URI` — it will be automatically replaced with `MONGO_PASSWORD` during initialization.

2. Start the server:
```bash
   npm run dev real.config.yaml
```

### Configuration

Customize settings in your config file:
```yaml
express:
  port: 3000

db:
  type: "atlas"  # Options: "atlas" or "memory"
  atlas:
    database: ${ MONGO_URI } # Do not modify this
    password: ${ MONGO_PASSWORD } # Do not modify this

user:
  type: "test"  # Options: "real" or "test"

postRead:
  type: "test"  # Options: "real" or "test"
```
"""

def setup_post_reply_service():
    # Setup database credentials
    service_path = os.path.join(os.getcwd(), "forum-post-reply-service")
    secrets_path = os.path.join(service_path, "secrets")
    os.makedirs(secrets_path, exist_ok=True)
    secret_file_path = os.path.join(secrets_path, "secret.env")
    with open(secret_file_path, 'w') as secret_file:
        secret_file.write(f"MONGO_URI={os.getenv('MONGO_URI')}\n")
        secret_file.write(f"MONGO_PASSWORD={os.getenv('MONGO_PASSWORD')}\n")
        print("⚙️  Setting up Post & Reply Service's database secrets...")
    # then update config and start server
    with open(os.path.join(service_path, "production.config.yaml"), 'w') as config_file:
        # Write the configuration yaml file
        import yaml
        config = {
            'express': {
                'port': 8003
            },
            'db': {
                'type': 'atlas',
                'atlas': {
                    'database': '${ MONGO_URI }',
                    'password': '${ MONGO_PASSWORD }'
                }
            },
            # Use test implementations for services
            'user': {
                'type': 'test'
            },
            'postRead': {
                'type': 'test'
            }
        }
        yaml.dump(config, config_file)  
    try:
        # Install dependencies
        subprocess.run(["npm", "install"], cwd=service_path, check=True)
        # Start the server with production config
        run_server("forum-post-reply-service", ["npm", "run", "dev", "production.config.yaml"], cwd=service_path, check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to set up the Post & Reply Service.")


"""
Auth Service setup
### 1. Install Dependencies
```bash
npm install
```

### 2. Setup Environment
```bash
copy .env.example .env
# Edit .env with your settings
```

### 3. Run Service
```bash
npm start
```
"""
def setup_auth_service():
    service_path = os.path.join(os.getcwd(), "forum-auth-service")
    print("⚙️  Setting up Auth Service...")
    # Copy the .env.example to .env
    example_env_path = os.path.join(service_path, ".env.example")
    target_env_path = os.path.join(service_path, ".env")
    assert os.path.exists(example_env_path)
    import shutil
    shutil.copy(example_env_path, target_env_path)
    try:
        # Install dependencies
        subprocess.run(["npm", "install"], cwd=service_path, check=True)
        # Start the server
        run_server("forum-auth-service", ["npm", "run", "dev"], cwd=service_path, check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to set up the Auth Service.")


def setup_user_service():
    service_path = os.path.join(os.getcwd(), "forum-user-service")
    print("⚙️  Setting up User Service...")
    # Copy the .env.example to .env
    example_env_path = os.path.join(service_path, ".env.example")
    target_env_path = os.path.join(service_path, ".env")
    assert os.path.exists(example_env_path)
    import shutil
    shutil.copy(example_env_path, target_env_path)
    try:
        # must activate virtual environment first

        venv_path = os.path.join(service_path, "venv")
        if not os.path.exists(venv_path):
            subprocess.run(["python3", "-m", "venv", "venv"], cwd=service_path, check=True)
        assert os.path.exists(venv_path)
        # Install dependencies
        subprocess.run([os.path.join(venv_path, "bin", "pip"), "install", "-e", "."], cwd=service_path, check=True)
        # Start the server
        os.environ["FLASK_DEBUG"] = "1"
        os.environ["TESTING"] = "True"
        run_server("forum-user-service", [os.path.join(venv_path, "bin", "python"), "run.py"], cwd=service_path, check=True)    
    except subprocess.CalledProcessError:
        print("❌ Failed to set up the User Service.")      


def setup_file_service():
    pass

def setup_message_service():
    pass  # Implementation would be similar to setup_post_reply_service()

"""
## Quick Start (Windows)

### 1. Install Dependencies
```bash
npm install
```

### 2. Setup Gmail
1. Enable 2-Factor Authentication on Google account
2. Generate App Password: https://myaccount.google.com/apppasswords
3. Copy the 16-character password

### 3. Setup Environment
```bash
copy .env.example .env
# Edit .env with your settings
```

Required `.env` variables:
```
PORT=3003
SERVICE_KEY=your_service_key
SMTP_EMAIL=your-gmail@gmail.com
SMTP_PASSWORD=your-app-password-here
```

### 4. Run Service
```bash
npm start
```
Service runs at `http://localhost:3003`

**Development** (with auto-reload):
```bash
npm run dev
```
"""
def setup_email_service():
    service_path = os.path.join(os.getcwd(), "forum-email-service")
    print("⚙️  Setting up Email Service...")
    # Copy the .env.example to .env
    example_env_path = os.path.join(service_path, ".env.example")
    target_env_path = os.path.join(service_path, ".env")
    assert os.path.exists(example_env_path)
    import shutil
    shutil.copy(example_env_path, target_env_path)
    try:
        # Install dependencies
        subprocess.run(["npm", "install"], cwd=service_path, check=True)
        # Start the server
        run_server("forum-email-service", ["npm", "start"], cwd=service_path, check=True)
    except subprocess.CalledProcessError:
        print("❌ Failed to set up the Email Service.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Deploy Forum Application Services")
    parser.add_argument('--no-sync', action='store_true', help="Skip syncing repositories")
    parser.add_argument('--sync-only', action='store_true', help="Only sync repositories and exit   ")
    parser.add_argument('--no-log-cleanup', action='store_true', help="Skip cleanup log files")
    args = parser.parse_args()
    validate_env()
    kill_node_processes()
    if not args.no_log_cleanup:
        # Clean up log files
        if os.path.exists("logs"):
            import shutil
            shutil.rmtree("logs")
            print("🧹 Cleaned up old log files.")
    if not args.no_sync:
        sync()
    if not args.sync_only:
        setup_gateway()
        setup_frontend()
        setup_post_reply_service()
        setup_auth_service()
        setup_user_service()
        setup_file_service()
        setup_message_service()
        print("\n✅ All services processed.")