"""Convergent checks for APP 309 — multimodal image-gen survey lab.

Offline via FakeImageClient. Ollama path exercised with httpx MockTransport.
"""

from __future__ import annotations

import base64
import os
import sys
from pathlib import Path

import httpx
import pytest

ROOT = Path(__file__).resolve().parents[1]
LAB = os.environ.get("GURUKUL_LAB", "starter")
sys.path.insert(0, str(ROOT / LAB))

from image_gen import (  # noqa: E402
    FakeImageClient,
    ImageArtifact,
    OllamaImageClient,
    StubOpenAIImageClient,
    build_generate_request,
    diffusion_work_units,
    normalize_prompt,
    seed_from_prompt,
    solid_png,
)


def test_normalize_prompt_collapses_whitespace():
    assert normalize_prompt("  red   cube  ") == "red cube"


def test_normalize_prompt_rejects_empty():
    with pytest.raises(ValueError):
        normalize_prompt("   ")
    with pytest.raises(ValueError):
        normalize_prompt("")


def test_normalize_prompt_max_chars():
    with pytest.raises(ValueError):
        normalize_prompt("xxxxxxxxxx", max_chars=5)


def test_diffusion_work_units():
    assert diffusion_work_units(64, 64, 20) == ((64 * 64) * 20)
    with pytest.raises(ValueError):
        diffusion_work_units(0, 10, 8)
    with pytest.raises(ValueError):
        diffusion_work_units(10, 0, 8)
    with pytest.raises(ValueError):
        diffusion_work_units(10, 8, 0)


def test_seed_from_prompt_is_deterministic():
    a = seed_from_prompt("ops dashboard screenshot")
    b = seed_from_prompt("ops dashboard screenshot")
    assert a == b
    assert 0 <= a <= 2147483647
    assert seed_from_prompt("ops dashboard screenshot", salt=1) != a


def test_build_generate_request_defaults_seed():
    req = build_generate_request("  blue circle  ", width=32, height=16, steps=5)
    assert req["prompt"] == "blue circle"
    assert req["width"] == 32
    assert req["height"] == 16
    assert req["steps"] == 5
    assert req["seed"] == seed_from_prompt("blue circle")


def test_build_generate_request_respects_explicit_seed():
    req = build_generate_request("x", seed=42)
    assert req["seed"] == 42


def test_solid_png_has_signature():
    raw = solid_png(2, 2, (255, 0, 0))
    assert raw.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(raw) > 40


def test_fake_image_client_deterministic():
    client = FakeImageClient()
    a = client.generate("incident heatmap", width=8, height=8, steps=10)
    b = client.generate("incident heatmap", width=8, height=8, steps=10)
    assert isinstance(a, ImageArtifact)
    assert a.data == b.data
    assert a.seed == b.seed
    assert a.provider == "fake"
    assert a.mime_type == "image/png"
    assert a.prompt == "incident heatmap"
    assert a.width == 8 and a.height == 8 and a.steps == 10
    assert a.data.startswith(b"\x89PNG\r\n\x1a\n")


def test_fake_image_client_seed_changes_bytes():
    client = FakeImageClient()
    a = client.generate("same prompt", seed=1, width=4, height=4)
    b = client.generate("same prompt", seed=2, width=4, height=4)
    assert a.data != b.data


def test_stub_openai_image_client_provider_label():
    stub = StubOpenAIImageClient()
    art = stub.generate("paid stub path", width=4, height=4, seed=7)
    assert art.provider == "openai-stub"
    assert art.data.startswith(b"\x89PNG\r\n\x1a\n")
    fake = FakeImageClient().generate("paid stub path", width=4, height=4, seed=7)
    assert art.data == fake.data


def test_ollama_image_client_with_mock_transport():
    png = solid_png(4, 4, (10, 20, 30))
    b64 = base64.b64encode(png).decode("ascii")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/generate"
        return httpx.Response(200, json={"image": b64})

    http = httpx.Client(transport=httpx.MockTransport(handler), base_url="http://ollama.test")
    client = OllamaImageClient(client=http, base_url="http://ollama.test", model="llava")
    art = client.generate("mock ollama image", width=4, height=4, steps=3, seed=99)
    assert art.provider == "ollama"
    assert art.data == png
    assert art.seed == 99
    assert art.steps == 3
    http.close()


def test_ollama_image_client_accepts_response_field():
    png = solid_png(2, 2, (1, 2, 3))
    b64 = base64.b64encode(png).decode("ascii")

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"response": b64})

    http = httpx.Client(transport=httpx.MockTransport(handler))
    client = OllamaImageClient(client=http, base_url="http://ollama.test")
    art = client.generate("via response field", width=2, height=2, seed=1)
    assert art.data == png
