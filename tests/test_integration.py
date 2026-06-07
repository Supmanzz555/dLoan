import time
from fastapi.testclient import TestClient
from api.routes import app
from data.applicants import ALL_APPLICANTS, EXPECTED_OUTCOMES

client = TestClient(app)

DELAY_BETWEEN_TESTS = 15
MAX_POLLS = 40


def test_all_applicants():
    results = []
    for app_data in ALL_APPLICANTS:
        time.sleep(DELAY_BETWEEN_TESTS)

        resp = client.post("/screen", json=app_data)
        assert resp.status_code == 200, f"{app_data['applicant_id']}: {resp.status_code}"
        job_id = resp.json()["job_id"]

        for _ in range(MAX_POLLS):
            status_resp = client.get(f"/screen/{job_id}/status")
            assert status_resp.status_code == 200
            data = status_resp.json()
            if data["status"] == "done":
                result = data["result"]
                break
            elif data["status"] == "error":
                raise AssertionError(f"{app_data['applicant_id']} failed: {data['error']}")
            time.sleep(3)
        else:
            raise AssertionError(f"{app_data['applicant_id']}: job did not complete")

        expected = EXPECTED_OUTCOMES[app_data["applicant_id"]]
        ok = result["recommendation"] == expected
        results.append((app_data["applicant_id"], expected, result["recommendation"], ok))

        if ok:
            print(f"{app_data['applicant_id']}: {result['recommendation']:30s} ✅")
        else:
            print(f"{app_data['applicant_id']}: expected={expected:30s} got={result['recommendation']:30s} ⚠️")

    passed = sum(1 for r in results if r[3])
    total = len(results)
    print(f"\n{passed}/{total} match expected baseline")

    for app_id, exp, got, ok in results:
        if not ok:
            print(f"  MISMATCH: {app_id} expected '{exp}' got '{got}'")

    assert passed >= total * 0.8, f"Accuracy too low: {passed}/{total} ({passed/total*100:.0f}%)"
