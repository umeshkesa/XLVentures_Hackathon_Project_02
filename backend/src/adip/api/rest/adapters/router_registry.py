"""Router and adapter registry — auto-registration support."""

from __future__ import annotations

from fastapi import APIRouter

from adip.api.rest.adapters.base import BaseServiceAdapter

_registered_adapters: dict[str, BaseServiceAdapter] = {}
_registered_routers: dict[str, APIRouter] = {}


def register_adapter(domain: str, adapter: BaseServiceAdapter) -> None:
    _registered_adapters[domain] = adapter


def register_router(domain: str, router: APIRouter) -> None:
    _registered_routers[domain] = router


def get_adapter(domain: str) -> BaseServiceAdapter | None:
    return _registered_adapters.get(domain)


def get_router(domain: str) -> APIRouter | None:
    return _registered_routers.get(domain)


def get_all_adapters() -> dict[str, BaseServiceAdapter]:
    return dict(_registered_adapters)


def get_all_routers() -> dict[str, APIRouter]:
    return dict(_registered_routers)


def clear_registry() -> None:
    _registered_adapters.clear()
    _registered_routers.clear()


def get_registered_domains() -> list[str]:
    return list(_registered_adapters.keys())
