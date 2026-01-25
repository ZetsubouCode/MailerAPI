import os

import uvicorn


def _bool_env(key: str, default: bool = False) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on"}


def main() -> None:
    host = os.getenv("MAILER_API_HOST", "127.0.0.1")
    port = int(os.getenv("MAILER_API_PORT", "5556"))
    reload = _bool_env("MAILER_API_RELOAD", True)
    uvicorn.run("app.main:app", host=host, port=port, reload=reload, log_level="info")


if __name__ == "__main__":
    main()
