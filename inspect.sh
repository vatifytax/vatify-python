# Inspect the wheel
python - <<'PY'
import glob, zipfile, os
wheel = sorted(glob.glob("dist/*.whl"))[-1]
print("Wheel:", wheel)
with zipfile.ZipFile(wheel) as z:
    names = [n for n in z.namelist() if n.startswith("vatify/")]
    print("Wheel has package files:", bool(names))
    print("\n".join(names[:20]))
PY

# Inspect the sdist (tar.gz)
tar -tzf dist/*.tar.gz | sed -n '1,120p'

