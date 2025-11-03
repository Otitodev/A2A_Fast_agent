#!/usr/bin/env python3
"""
Deployment helper script for Telex AI Agent
Supports local development, Docker, and cloud deployment preparation
"""
import os
import sys
import subprocess
import json
from pathlib import Path

class DeploymentHelper:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / ".env"
        self.env_example = self.project_root / ".env.example"
    
    def check_requirements(self):
        """Check if all requirements are met for deployment."""
        print("🔍 Checking deployment requirements...")
        
        issues = []
        
        # Check if .env file exists
        if not self.env_file.exists():
            if self.env_example.exists():
                print("⚠️  .env file not found. Creating from .env.example...")
                self.env_example.rename(self.env_file)
                issues.append("Please edit .env file and add your MISTRAL_API_KEY")
            else:
                issues.append(".env file is missing")
        
        # Check if MISTRAL_API_KEY is set
        if self.env_file.exists():
            with open(self.env_file) as f:
                env_content = f.read()
                if "MISTRAL_API_KEY=your_mistral_api_key_here" in env_content:
                    issues.append("Please set your actual MISTRAL_API_KEY in .env file")
                elif "MISTRAL_API_KEY=" not in env_content:
                    issues.append("MISTRAL_API_KEY is not set in .env file")
        
        # Check if required files exist
        required_files = [
            "requirements.txt",
            "Dockerfile", 
            "app/main.py",
            "leapcell.yaml"
        ]
        
        for file in required_files:
            if not (self.project_root / file).exists():
                issues.append(f"Required file missing: {file}")
        
        if issues:
            print("❌ Issues found:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print("✅ All requirements met!")
            return True
    
    def test_local(self):
        """Test the application locally."""
        print("🧪 Testing application locally...")
        
        if not self.check_requirements():
            return False
        
        try:
            # Start the server in background
            print("Starting server...")
            process = subprocess.Popen([
                sys.executable, "start_server.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait a moment for server to start
            import time
            time.sleep(3)
            
            # Test health endpoint
            result = subprocess.run([
                "curl", "-f", "http://localhost:8000/health"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Local server is running and healthy!")
                
                # Run compliance tests
                print("Running A2A compliance tests...")
                test_result = subprocess.run([
                    sys.executable, "test_a2a_compliance.py", "http://localhost:8000"
                ], capture_output=True, text=True, timeout=60)
                
                if test_result.returncode == 0:
                    print("✅ All compliance tests passed!")
                else:
                    print("⚠️  Some compliance tests failed:")
                    print(test_result.stdout)
                
                return True
            else:
                print("❌ Local server health check failed")
                return False
                
        except Exception as e:
            print(f"❌ Error testing locally: {e}")
            return False
        finally:
            # Clean up
            try:
                process.terminate()
            except:
                pass
    
    def build_docker(self):
        """Build Docker image."""
        print("🐳 Building Docker image...")
        
        if not self.check_requirements():
            return False
        
        try:
            result = subprocess.run([
                "docker", "build", "-t", "telex-ai-agent", "."
            ], check=True)
            
            print("✅ Docker image built successfully!")
            
            # Test Docker image
            print("Testing Docker image...")
            result = subprocess.run([
                "docker", "run", "--rm", "-d", 
                "--name", "telex-test",
                "-p", "8001:8000",
                "--env-file", ".env",
                "telex-ai-agent"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                import time
                time.sleep(5)  # Wait for container to start
                
                # Test health
                health_result = subprocess.run([
                    "curl", "-f", "http://localhost:8001/health"
                ], capture_output=True, text=True, timeout=10)
                
                # Clean up
                subprocess.run(["docker", "stop", "telex-test"], capture_output=True)
                
                if health_result.returncode == 0:
                    print("✅ Docker image is working correctly!")
                    return True
                else:
                    print("❌ Docker image health check failed")
                    return False
            else:
                print("❌ Failed to run Docker container")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Docker build failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Error building Docker image: {e}")
            return False
    
    def prepare_leapcell(self):
        """Prepare for Leapcell deployment."""
        print("🚀 Preparing for Leapcell deployment...")
        
        if not self.check_requirements():
            return False
        
        # Check if leapcell.yaml exists and is valid
        leapcell_config = self.project_root / "leapcell.yaml"
        if not leapcell_config.exists():
            print("❌ leapcell.yaml not found")
            return False
        
        print("✅ Leapcell configuration found")
        
        # Create deployment checklist
        checklist = [
            "✅ leapcell.yaml configuration file",
            "✅ Dockerfile optimized for cloud deployment", 
            "✅ Health check endpoint at /health",
            "✅ Environment variables configured",
            "✅ Requirements.txt with all dependencies",
            "⚠️  Set MISTRAL_API_KEY in Leapcell dashboard",
            "⚠️  Test deployment after going live"
        ]
        
        print("\n📋 Leapcell Deployment Checklist:")
        for item in checklist:
            print(f"   {item}")
        
        print("\n🔗 Next Steps:")
        print("   1. Push your code to GitHub")
        print("   2. Connect GitHub repo to Leapcell")
        print("   3. Set environment variables in Leapcell dashboard:")
        print("      - MISTRAL_API_KEY=your_actual_api_key")
        print("      - MISTRAL_MODEL=mistral-small-latest")
        print("   4. Deploy and test the endpoints")
        
        return True
    
    def show_endpoints(self):
        """Show available endpoints."""
        print("\n📡 Available Endpoints:")
        endpoints = [
            ("GET  /", "Root endpoint with service info"),
            ("GET  /health", "Health check endpoint"),
            ("GET  /test-llm", "Test LLM connection"),
            ("POST /webhook", "Telex.im webhook endpoint"),
            ("POST /a2a", "A2A protocol JSON-RPC endpoint"),
            ("POST /a2a/ping", "A2A ping endpoint"),
            ("POST /a2a/chat", "A2A chat endpoint")
        ]
        
        for method_path, description in endpoints:
            print(f"   {method_path:<20} - {description}")
        
        print("\n🤖 A2A Methods:")
        methods = [
            "ping", "echo", "capabilities", "status",
            "ai.chat", "ai.complete", "ai.review_code", "ai.explain_code",
            "task.create", "task.status", "task.cancel"
        ]
        
        for method in methods:
            print(f"   - {method}")

def main():
    """Main deployment helper."""
    helper = DeploymentHelper()
    
    if len(sys.argv) < 2:
        print("🚀 Telex AI Agent Deployment Helper")
        print("\nUsage:")
        print("   python deploy.py check      - Check deployment requirements")
        print("   python deploy.py test       - Test application locally")
        print("   python deploy.py docker     - Build and test Docker image")
        print("   python deploy.py leapcell   - Prepare for Leapcell deployment")
        print("   python deploy.py endpoints  - Show available endpoints")
        return
    
    command = sys.argv[1].lower()
    
    if command == "check":
        helper.check_requirements()
    elif command == "test":
        helper.test_local()
    elif command == "docker":
        helper.build_docker()
    elif command == "leapcell":
        helper.prepare_leapcell()
    elif command == "endpoints":
        helper.show_endpoints()
    else:
        print(f"❌ Unknown command: {command}")
        print("Use 'python deploy.py' to see available commands")

if __name__ == "__main__":
    main()