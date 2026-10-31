import importlib.util
import os
import sys
from pathlib import Path

# Add instagram-growth directory to Python sys.path so modules and packages can be imported
growth_dir = Path(__file__).resolve().parent / "instagram-growth"
if str(growth_dir) not in sys.path:
    sys.path.insert(0, str(growth_dir))

# Switch working directory to instagram-growth so relative paths and templates work
try:
    os.chdir(growth_dir)
except OSError:
    pass

# Load instagram-growth/app.py dynamically to avoid circular import with root app.py
_spec = importlib.util.spec_from_file_location("growth_app", growth_dir / "app.py")
_growth_module = importlib.util.module_from_spec(_spec)
sys.modules["growth_app"] = _growth_module
_spec.loader.exec_module(_growth_module)

app = _growth_module.app
create_app = _growth_module.create_app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))
