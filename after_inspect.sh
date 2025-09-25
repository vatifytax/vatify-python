python -m venv .venv && source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install dist/*.whl
python - <<'PY'
import sys, importlib.util
print("python:", sys.executable)
spec = importlib.util.find_spec("vatify")
print("find_spec('vatify'):", spec)
if spec:
    import vatify; print("vatify from:", vatify.__file__)
PY

