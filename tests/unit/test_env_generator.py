import unittest
import os
import sys
import tempfile
import shutil

# Resolve and insert project root into python paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.setup_plane_app_env import load_env_local, generate_plane_env

class TestEnvGenerator(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to act as file environment
        self.test_dir = tempfile.mkdtemp()
        self.env_local_path = os.path.join(self.test_dir, ".env.local")
        self.plane_env_path = os.path.join(self.test_dir, "plane.env")
        
        # Write a dummy template plane.env
        self.template_content = (
            "POSTGRES_PASSWORD=default_postgres_pass\n"
            "REDIS_PASSWORD=\n"
            "REDIS_URL=redis://plane-redis:6379/\n"
            "CORS_ALLOWED_ORIGINS=http://localhost\n"
            "WEB_URL=http://localhost\n"
            "APP_DOMAIN=localhost\n"
            "SECRET_KEY=default_secret\n"
        )
        with open(self.plane_env_path, "w", encoding="utf-8") as f:
            f.write(self.template_content)

    def tearDown(self):
        # Remove temporary directory
        shutil.rmtree(self.test_dir)

    def test_load_env_local_empty_or_missing(self):
        # Test loading missing file
        vars_dict = load_env_local("non_existent_file.env")
        self.assertEqual(vars_dict, {})

    def test_load_env_local_parsing(self):
        # Write custom env.local
        env_content = (
            "# This is a comment\n"
            "POSTGRES_PASSWORD=custom_pg_password123\n"
            "\n"
            "  REDIS_PASSWORD = custom_redis_pass_xyz  \n"
            "WEB_URL=http://100.121.120.59\n"
        )
        with open(self.env_local_path, "w", encoding="utf-8") as f:
            f.write(env_content)
            
        vars_dict = load_env_local(self.env_local_path)
        self.assertEqual(vars_dict.get("POSTGRES_PASSWORD"), "custom_pg_password123")
        self.assertEqual(vars_dict.get("REDIS_PASSWORD"), "custom_redis_pass_xyz")
        self.assertEqual(vars_dict.get("WEB_URL"), "http://100.121.120.59")
        self.assertIsNone(vars_dict.get("NON_EXISTENT"))

    def test_generate_plane_env(self):
        # Write custom env.local
        env_content = (
            "POSTGRES_PASSWORD=pg_secure_pwd\n"
            "REDIS_PASSWORD=redis_secure_pwd\n"
            "REDIS_URL=redis://:redis_secure_pwd@plane-redis:6379/\n"
            "WEB_URL=http://100.121.120.59\n"
            "CORS_ALLOWED_ORIGINS=http://100.121.120.59,http://localhost\n"
        )
        with open(self.env_local_path, "w", encoding="utf-8") as f:
            f.write(env_content)
            
        success = generate_plane_env(self.env_local_path, self.plane_env_path)
        self.assertTrue(success)
        
        # Read back generated file and verify replacements
        with open(self.plane_env_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        content_dict = {}
        for line in lines:
            line = line.strip()
            if line and "=" in line:
                k, v = line.split("=", 1)
                content_dict[k] = v
                
        self.assertEqual(content_dict.get("POSTGRES_PASSWORD"), "pg_secure_pwd")
        self.assertEqual(content_dict.get("REDIS_PASSWORD"), "redis_secure_pwd")
        self.assertEqual(content_dict.get("REDIS_URL"), "redis://:redis_secure_pwd@plane-redis:6379/")
        self.assertEqual(content_dict.get("WEB_URL"), "http://100.121.120.59")
        self.assertEqual(content_dict.get("CORS_ALLOWED_ORIGINS"), "http://100.121.120.59,http://localhost")
        self.assertEqual(content_dict.get("APP_DOMAIN"), "100.121.120.59")
        self.assertNotEqual(content_dict.get("SECRET_KEY"), "default_secret") # Should be dynamically generated

if __name__ == "__main__":
    unittest.main()
