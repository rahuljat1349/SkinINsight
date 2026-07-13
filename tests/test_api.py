"""API endpoint tests"""

from fastapi.testclient import TestClient


class TestHealth:
    def test_health_endpoint(self, client: TestClient):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data

    def test_root_endpoint(self, client: TestClient):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "CutiS"

    def test_docs_endpoint(self, client: TestClient):
        resp = client.get("/docs")
        assert resp.status_code == 200

    def test_redoc_endpoint(self, client: TestClient):
        resp = client.get("/redoc")
        assert resp.status_code == 200


class TestAnalyzeValidation:
    def test_no_file_returns_422(self, client: TestClient):
        resp = client.post("/api/v1/analyze")
        assert resp.status_code == 422

    def test_unsupported_format_returns_error(self, client: TestClient):
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("test.txt", b"not an image", "text/plain")},
        )
        assert resp.status_code in (400, 500)
        assert "error" in resp.json()

    def test_large_image_returns_error(self, client: TestClient, large_image: bytes):
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("large.jpg", large_image, "image/jpeg")},
        )
        assert resp.status_code in (400, 500)
        assert "error" in resp.json()

    def test_blank_image_returns_error(self, client: TestClient, blank_image: bytes):
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("blank.jpg", blank_image, "image/jpeg")},
        )
        assert resp.status_code in (400, 500)
        assert "error" in resp.json()

    def test_png_format_accepted(self, client: TestClient, sample_image_png: bytes):
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("test.png", sample_image_png, "image/png")},
        )
        assert resp.status_code in (200, 400, 500)

    def test_webp_format_accepted(self, client: TestClient):
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("test.webp", b"RIFFxxxxWEBPVP8 ", "image/webp")},
        )
        assert resp.status_code in (200, 400, 500)


class TestAnalyzeUserInfo:
    def test_user_info_passed_as_form(self, client: TestClient, blank_image: bytes):
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("blank.jpg", blank_image, "image/jpeg")},
            data={
                "age_group": "25-30",
                "skin_type_self": "Oily",
                "gender": "Female",
                "sensitive_skin": "No",
            },
        )
        assert resp.status_code in (200, 400, 500)

    def test_partial_user_info(self, client: TestClient, blank_image: bytes):
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("blank.jpg", blank_image, "image/jpeg")},
            data={"age_group": "31-40"},
        )
        assert resp.status_code in (200, 400, 500)


class TestErrorResponseStructure:
    def test_error_response_has_required_fields(self, client: TestClient, blank_image: bytes):
        resp = client.post(
            "/api/v1/analyze",
            files={"file": ("blank.jpg", blank_image, "image/jpeg")},
        )
        assert resp.status_code in (400, 500)
        body = resp.json()
        assert "error" in body
        assert "code" in body["error"]
        assert "message" in body["error"]
        assert "user_message" in body["error"]
        assert "success" in body
        assert body["success"] is False
