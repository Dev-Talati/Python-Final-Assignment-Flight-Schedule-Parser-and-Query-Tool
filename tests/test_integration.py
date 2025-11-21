import os
import json
import subprocess


def test_integration_creates_outputs(tmp_path):
    # create sample csv
    csv = tmp_path / "sample.csv"
    csv.write_text("""#comment\nAB12,JFK,LAX,2025-12-01 09:00,2025-12-01 12:00,199.99\n""")
    qry = tmp_path / "queries.json"
    qry.write_text('[{"origin":"JFK"}]')

    cwd = os.getcwd()
    try:
        # run the script
        res = subprocess.run(["python3", cwd + "/flight_parser.py", "-i", str(csv), "-q", str(qry)], cwd=cwd, capture_output=True, text=True)
        assert res.returncode == 0
        # check db.json exists
        assert os.path.exists(cwd + "/db.json")
        assert os.path.exists(cwd + "/errors.txt")
        # find response file
        files = [f for f in os.listdir(cwd) if f.startswith("response_12345_John_Doe_") and f.endswith(".json")]
        assert len(files) >= 1
        # validate json structure
        with open(cwd + "/db.json") as fh:
            data = json.load(fh)
            assert isinstance(data, list)
    finally:
        # cleanup generated files
        for p in [cwd + "/db.json", cwd + "/errors.txt"]:
            try:
                os.remove(p)
            except Exception:
                pass
        for f in os.listdir(cwd):
            if f.startswith("response_12345_John_Doe_") and f.endswith(".json"):
                try:
                    os.remove(os.path.join(cwd, f))
                except Exception:
                    pass
