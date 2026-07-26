from __future__ import annotations

import ctypes
import os
from ctypes import wintypes
from pathlib import Path


class CredentialStoreError(RuntimeError):
    pass


class _DataBlob(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]


def _blob_from_bytes(value: bytes) -> tuple[_DataBlob, ctypes.Array[ctypes.c_char]]:
    buffer = ctypes.create_string_buffer(value)
    blob = _DataBlob(len(value), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_byte)))
    return blob, buffer


class WindowsCredentialStore:
    """Current-user DPAPI storage; ciphertext is useless to other Windows users/machines."""

    _ENTROPY = b"osun-lights:home-assistant:v1"
    _UI_FORBIDDEN = 0x01

    def __init__(self, path: Path) -> None:
        self.path = path

    def save(self, token: str) -> None:
        if os.name != "nt":
            raise CredentialStoreError("Windows DPAPI is available only on Windows")
        if not token.strip():
            raise CredentialStoreError("Cannot store an empty credential")
        encrypted = self._protect(token.strip().encode("utf-8"))
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = self.path.with_suffix(".tmp")
        temporary.write_bytes(encrypted)
        os.replace(temporary, self.path)

    def load(self) -> str | None:
        if not self.path.exists():
            return None
        if os.name != "nt":
            raise CredentialStoreError("Windows DPAPI is available only on Windows")
        try:
            return self._unprotect(self.path.read_bytes()).decode("utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise CredentialStoreError("The protected Home Assistant credential could not be read") from exc

    def delete(self) -> None:
        if self.path.exists():
            self.path.unlink()

    @classmethod
    def _protect(cls, plaintext: bytes) -> bytes:
        crypt32 = ctypes.windll.crypt32
        kernel32 = ctypes.windll.kernel32
        crypt32.CryptProtectData.argtypes = [
            ctypes.POINTER(_DataBlob),
            wintypes.LPCWSTR,
            ctypes.POINTER(_DataBlob),
            ctypes.c_void_p,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(_DataBlob),
        ]
        crypt32.CryptProtectData.restype = wintypes.BOOL
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p
        source, source_buffer = _blob_from_bytes(plaintext)
        entropy, entropy_buffer = _blob_from_bytes(cls._ENTROPY)
        output = _DataBlob()
        result = crypt32.CryptProtectData(
            ctypes.byref(source),
            "Osun Home Assistant token",
            ctypes.byref(entropy),
            None,
            None,
            cls._UI_FORBIDDEN,
            ctypes.byref(output),
        )
        del source_buffer, entropy_buffer
        if not result:
            raise CredentialStoreError("Windows could not protect the Home Assistant credential")
        try:
            return ctypes.string_at(output.pbData, output.cbData)
        finally:
            kernel32.LocalFree(ctypes.cast(output.pbData, ctypes.c_void_p))

    @classmethod
    def _unprotect(cls, ciphertext: bytes) -> bytes:
        crypt32 = ctypes.windll.crypt32
        kernel32 = ctypes.windll.kernel32
        crypt32.CryptUnprotectData.argtypes = [
            ctypes.POINTER(_DataBlob),
            ctypes.POINTER(wintypes.LPWSTR),
            ctypes.POINTER(_DataBlob),
            ctypes.c_void_p,
            ctypes.c_void_p,
            wintypes.DWORD,
            ctypes.POINTER(_DataBlob),
        ]
        crypt32.CryptUnprotectData.restype = wintypes.BOOL
        kernel32.LocalFree.argtypes = [ctypes.c_void_p]
        kernel32.LocalFree.restype = ctypes.c_void_p
        source, source_buffer = _blob_from_bytes(ciphertext)
        entropy, entropy_buffer = _blob_from_bytes(cls._ENTROPY)
        output = _DataBlob()
        result = crypt32.CryptUnprotectData(
            ctypes.byref(source),
            None,
            ctypes.byref(entropy),
            None,
            None,
            cls._UI_FORBIDDEN,
            ctypes.byref(output),
        )
        del source_buffer, entropy_buffer
        if not result:
            raise CredentialStoreError("Windows could not decrypt the Home Assistant credential")
        try:
            return ctypes.string_at(output.pbData, output.cbData)
        finally:
            kernel32.LocalFree(ctypes.cast(output.pbData, ctypes.c_void_p))
