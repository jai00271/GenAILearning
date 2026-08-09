"""APP 309 — Multimodal image-gen lab (solution).

Survey hands-on: thin ImageClient contract + FakeImageClient for offline pytest.
Optional Ollama HTTP path (injectable httpx client) and a [PAID] OpenAI-shaped stub.
"""

from __future__ import annotations

import base64
import hashlib
import struct
import zlib
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

import httpx

DEFAULT_OLLAMA_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_OLLAMA_MODEL = "llava"


@dataclass(frozen=True)
class ImageArtifact:
    """Provider-agnostic image generation result."""

    prompt: str
    width: int
    height: int
    mime_type: str
    data: bytes
    seed: int
    provider: str
    steps: int


def normalize_prompt(prompt: str, max_chars: int = 400) -> str:
    """Strip, collapse whitespace, enforce non-empty and max length."""
    if prompt is None:
        raise ValueError("prompt must be a non-empty string")
    cleaned = " ".join(str(prompt).split())
    if not cleaned:
        raise ValueError("prompt must be a non-empty string")
    if len(cleaned) > max_chars:
        raise ValueError(f"prompt exceeds max_chars={max_chars}")
    return cleaned


def diffusion_work_units(width: int, height: int, steps: int) -> int:
    """Teaching heuristic for relative diffusion cost: pixels × steps."""
    if width < 1 or height < 1:
        raise ValueError("width and height must be >= 1")
    if steps < 1:
        raise ValueError("steps must be >= 1")
    return width * height * steps


def seed_from_prompt(prompt: str, salt: int = 0) -> int:
    """Deterministic 31-bit seed from prompt (+ optional salt)."""
    digest = hashlib.sha256(f"{salt}:{prompt}".encode("utf-8")).digest()
    return int.from_bytes(digest[:4], "big") & 2147483647


def build_generate_request(
    prompt: str,
    width: int = 64,
    height: int = 64,
    steps: int = 20,
    seed: int | None = None,
) -> dict[str, Any]:
    """Canonical request dict shared by clients (teaching shape)."""
    normalized = normalize_prompt(prompt)
    if width < 1 or height < 1:
        raise ValueError("width and height must be >= 1")
    if steps < 1:
        raise ValueError("steps must be >= 1")
    resolved_seed = seed_from_prompt(normalized) if seed is None else int(seed)
    return {
        "prompt": normalized,
        "width": width,
        "height": height,
        "steps": steps,
        "seed": resolved_seed,
    }


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    crc = zlib.crc32(tag + data) & 4294967295
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)


def solid_png(width: int, height: int, rgb: tuple[int, int, int]) -> bytes:
    """Minimal RGB PNG (8-bit) — no third-party image libs."""
    if width < 1 or height < 1:
        raise ValueError("width and height must be >= 1")
    r, g, b = rgb
    row = b"\x00" + bytes([r, g, b]) * width
    raw = row * height
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(raw, 9))
        + _png_chunk(b"IEND", b"")
    )


def _rgb_from_seed(seed: int) -> tuple[int, int, int]:
    return ((seed >> 16) & 255, (seed >> 8) & 255, seed & 255)


@runtime_checkable
class ImageClient(Protocol):
    """Thin multimodal image-generation interface."""

    def generate(
        self,
        prompt: str,
        width: int = 64,
        height: int = 64,
        steps: int = 20,
        seed: int | None = None,
    ) -> ImageArtifact:
        """Return an ImageArtifact for the given text prompt."""
        ...


class FakeImageClient:
    """Deterministic offline client for pytest — no network, no GPU, no keys."""

    provider_name = "fake"

    def generate(
        self,
        prompt: str,
        width: int = 64,
        height: int = 64,
        steps: int = 20,
        seed: int | None = None,
    ) -> ImageArtifact:
        req = build_generate_request(
            prompt, width=width, height=height, steps=steps, seed=seed
        )
        rgb = _rgb_from_seed(req["seed"])
        data = solid_png(req["width"], req["height"], rgb)
        return ImageArtifact(
            prompt=req["prompt"],
            width=req["width"],
            height=req["height"],
            mime_type="image/png",
            data=data,
            seed=req["seed"],
            provider=self.provider_name,
            steps=req["steps"],
        )


class OllamaImageClient:
    """Optional local path — httpx against Ollama-style `/api/generate`.

    Live servers / image-capable models vary; pytest must inject MockTransport.
    Expected JSON (teaching contract): ``{"image": "<base64 png>"}`` or
    ``{"response": "<base64 png>"}``.
    """

    provider_name = "ollama"

    def __init__(
        self,
        base_url: str = DEFAULT_OLLAMA_BASE_URL,
        model: str = DEFAULT_OLLAMA_MODEL,
        timeout: float = 120.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._client = client
        self._owns_client = client is None

    def close(self) -> None:
        if self._client is not None and self._owns_client:
            self._client.close()
            self._client = None

    def __enter__(self) -> OllamaImageClient:
        if self._client is None:
            self._client = httpx.Client(timeout=self.timeout)
            self._owns_client = True
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def generate(
        self,
        prompt: str,
        width: int = 64,
        height: int = 64,
        steps: int = 20,
        seed: int | None = None,
    ) -> ImageArtifact:
        if self._client is None:
            self._client = httpx.Client(timeout=self.timeout)
            self._owns_client = True
        req = build_generate_request(
            prompt, width=width, height=height, steps=steps, seed=seed
        )
        payload = {
            "model": self.model,
            "prompt": req["prompt"],
            "stream": False,
            "options": {"seed": req["seed"], "num_predict": req["steps"]},
            "width": req["width"],
            "height": req["height"],
        }
        resp = self._client.post(f"{self.base_url}/api/generate", json=payload)
        resp.raise_for_status()
        body = resp.json()
        b64 = body.get("image")
        if b64 is None:
            b64 = body.get("response")
        if not b64 or not isinstance(b64, str):
            raise RuntimeError(
                "Ollama image response missing image/response base64 field"
            )
        data = base64.b64decode(b64)
        return ImageArtifact(
            prompt=req["prompt"],
            width=req["width"],
            height=req["height"],
            mime_type="image/png",
            data=data,
            seed=req["seed"],
            provider=self.provider_name,
            steps=req["steps"],
        )


class StubOpenAIImageClient:
    """[PAID — approx cost] Interface-shaped stub — no OPENAI_API_KEY.

    Returns FakeImageClient bytes with provider ``openai-stub`` so CI never
    needs cloud credentials. Check current OpenAI Images pricing as of August 2026
    before using a real client.
    """

    provider_name = "openai-stub"

    def __init__(self) -> None:
        self._fake = FakeImageClient()

    def generate(
        self,
        prompt: str,
        width: int = 64,
        height: int = 64,
        steps: int = 20,
        seed: int | None = None,
    ) -> ImageArtifact:
        art = self._fake.generate(
            prompt, width=width, height=height, steps=steps, seed=seed
        )
        return ImageArtifact(
            prompt=art.prompt,
            width=art.width,
            height=art.height,
            mime_type=art.mime_type,
            data=art.data,
            seed=art.seed,
            provider=self.provider_name,
            steps=art.steps,
        )
