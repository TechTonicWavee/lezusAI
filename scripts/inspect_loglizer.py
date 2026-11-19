import sys
import inspect
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGLIZER_PATH = ROOT / "log-anomaly"

sys.path.insert(0, str(LOGLIZER_PATH))

print("=" * 55)
print("DRISHTI AI - LOGLIZER INTEGRATION TEST")
print("=" * 55)

try:
    from loglizer.models import IsolationForest

    print("\n[OK] Loglizer IsolationForest imported")

    print("\nConstructor:")
    print(inspect.signature(IsolationForest))

    print("\nAvailable methods:")
    for name in dir(IsolationForest):
        if not name.startswith("_"):
            method = getattr(IsolationForest, name)
            if callable(method):
                try:
                    print(name, inspect.signature(method))
                except (TypeError, ValueError):
                    print(name)

except Exception as error:
    print("\n[FAILED] Could not import Loglizer")
    print(type(error).__name__, ":", error)

print("\n" + "=" * 55)
