#!/usr/bin/env python3
"""
Script to run the AI Medical Prescription Verification System
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages from pyproject.toml"""
    requirements = [
        "streamlit>=1.49.1",
        "pandas>=2.3.2", 
        "plotly>=6.3.0",
        "openai>=1.107.1",
        "requests>=2.32.5"
    ]
    
    print("Installing required packages...")
    for package in requirements:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ Installed {package}")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")

def run_streamlit_app():
    """Run the Streamlit application"""
    print("\n🚀 Starting AI Medical Prescription Verification System...")
    print("📱 The app will open in your browser at http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the application\n")
    
    try:
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up one level to the project root
        project_root = os.path.dirname(script_dir)
        
        # Check if app.py exists
        app_path = os.path.join(project_root, "app.py")
        if not os.path.exists(app_path):
            print(f"❌ app.py not found at {app_path}")
            return
        
        # Change to project root directory
        os.chdir(project_root)
        
        # Run streamlit
        subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
    except Exception as e:
        print(f"❌ Error running application: {e}")

if __name__ == "__main__":
    print("🏥 AI Medical Prescription Verification System")
    print("=" * 50)
    
    # Install requirements first
    install_requirements()
    
    # Run the app
    run_streamlit_app()
