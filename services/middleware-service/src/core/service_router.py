from collections.abc import Mapping


class ServiceRouter:
    """Resolve incoming paths to the correct downstream microservice base URL."""

    def __init__(self, service_map: Mapping[str, str], api_prefix: str):
        prefix = api_prefix or ""
        normalized_prefix = prefix if prefix.startswith("/") else f"/{prefix}"
        self.api_prefix = normalized_prefix.rstrip("/") or "/api/v1"
        self.routes = {name: url.rstrip("/") for name, url in service_map.items() if url}

    def build_target(self, service_name: str, path: str) -> str | None:
        base_url = self.routes.get(service_name)
        if not base_url:
            return None

        normalized_path = path.lstrip("/")
        if normalized_path.startswith("health"):
            return f"{base_url}/{normalized_path}" if normalized_path else f"{base_url}/health"
        if normalized_path:
            return f"{base_url}{self.api_prefix}/{normalized_path}"
        return f"{base_url}{self.api_prefix}"

    def available_services(self) -> list[str]:
        return sorted(self.routes.keys())

    def get_base_url(self, service_name: str) -> str | None:
        return self.routes.get(service_name)
