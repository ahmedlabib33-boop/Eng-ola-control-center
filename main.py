from __future__ import annotations

import flet as ft

from ola_360.app import ASSETS_DIR, flet_main


# ASGI application for Uvicorn, Render, Railway, Fly.io, and similar hosts.
app = ft.run(
    main=flet_main,
    assets_dir=str(ASSETS_DIR),
    export_asgi_app=True,
)


if __name__ == "__main__":
    # Direct local execution.
    ft.run(
        main=flet_main,
        assets_dir=str(ASSETS_DIR),
    )