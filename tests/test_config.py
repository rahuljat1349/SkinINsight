"""Configuration tests"""

from app.core.config import Settings


class TestSettingsDefaults:
    def test_app_name(self):
        s = Settings(_env_file=None)
        assert s.app_name == "CutiS"

    def test_app_version(self):
        s = Settings(_env_file=None)
        assert s.app_version == "1.0.0"

    def test_debug_default(self):
        s = Settings(_env_file=None)
        assert s.debug is False

    def test_host_default(self):
        s = Settings(_env_file=None)
        assert s.host == "0.0.0.0"

    def test_port_default(self):
        s = Settings(_env_file=None)
        assert s.port == 8000

    def test_max_image_size(self):
        s = Settings(_env_file=None)
        assert s.max_image_size_bytes == 10 * 1024 * 1024
        assert s.max_image_size_mb == 10

    def test_supported_formats(self):
        s = Settings(_env_file=None)
        assert "jpg" in s.supported_image_formats
        assert "jpeg" in s.supported_image_formats
        assert "png" in s.supported_image_formats
        assert "webp" in s.supported_image_formats

    def test_llm_defaults(self):
        s = Settings(_env_file=None)
        assert s.llm_enabled is True
        assert s.llm_provider == "mistral"
        assert s.llm_timeout_seconds == 30

    def test_pipeline_mode_default(self):
        s = Settings(_env_file=None)
        assert s.send_image_to_llm == "false"

    def test_fallback_default(self):
        s = Settings(_env_file=None)
        assert s.fallback_to_local_models is False

    def test_min_image_resolution(self):
        s = Settings(_env_file=None)
        assert s.min_image_resolution == (256, 256)


class TestSettingsOverride:
    def test_env_override_app_name(self, monkeypatch):
        monkeypatch.setenv("APP_NAME", "TestApp")
        s = Settings(_env_file=None)
        assert s.app_name == "TestApp"

    def test_env_override_debug(self, monkeypatch):
        monkeypatch.setenv("DEBUG", "true")
        s = Settings(_env_file=None)
        assert s.debug is True

    def test_env_override_port(self, monkeypatch):
        monkeypatch.setenv("PORT", "9000")
        s = Settings(_env_file=None)
        assert s.port == 9000

    def test_env_override_max_image_size(self, monkeypatch):
        monkeypatch.setenv("MAX_IMAGE_SIZE_MB", "20")
        s = Settings(_env_file=None)
        assert s.max_image_size_mb == 20

    def test_env_override_llm_provider(self, monkeypatch):
        monkeypatch.setenv("LLM_PROVIDER", "gemini")
        s = Settings(_env_file=None)
        assert s.llm_provider == "gemini"

    def test_env_override_pipeline_mode(self, monkeypatch):
        monkeypatch.setenv("SEND_IMAGE_TO_LLM", "hybrid")
        s = Settings(_env_file=None)
        assert s.send_image_to_llm == "hybrid"

    def test_env_override_fallback(self, monkeypatch):
        monkeypatch.setenv("FALLBACK_TO_LOCAL_MODELS", "true")
        s = Settings(_env_file=None)
        assert s.fallback_to_local_models is True
