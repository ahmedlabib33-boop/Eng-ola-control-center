from __future__ import annotations

import inspect

import flet as ft

from ola_360.app import ASSETS_DIR, flet_main


def _running_inside_streamlit() -> bool:
    return any("streamlit" in frame.filename.replace("\\", "/").lower() for frame in inspect.stack())


def _render_streamlit_compatibility_page() -> None:
    import streamlit as st

    st.set_page_config(page_title="OLA 360", page_icon="🏛️", layout="wide")
    st.title("OLA 360 | Executive PMO Chief of Staff")
    st.caption("Executive clarity. Every morning.")
    st.warning(
        "This repository is a Flet application. Streamlit Community Cloud can run this "
        "compatibility page, but the full mobile command-center UI should be deployed as "
        "an ASGI app using the included Procfile or run locally with RUN_APP.bat."
    )
    st.markdown(
        """
        ### Full app entrypoints

        - Local Windows: `RUN_APP.bat`
        - ASGI deployment: `uvicorn main:app --host 0.0.0.0 --port $PORT`
        - Main module: `main.py`

        ### Included capabilities

        - Executive Morning Brief
        - Early-Warning and Intervention Radar
        - Meeting extraction, decisions, commitments, and follow-up drafts
        - AI Chief of Staff safe fallback
        - My Day private module
        - Mobile Premium pages: Intervention Cockpit, Template Center, Timeline, End-of-Day Review
        """
    )


# ASGI application for Uvicorn, Render, Railway, Fly.io, and similar hosts.
app = None if _running_inside_streamlit() else ft.run(main=flet_main, assets_dir=str(ASSETS_DIR), export_asgi_app=True)


if __name__ == "__main__":
    if _running_inside_streamlit():
        _render_streamlit_compatibility_page()
    else:
        # Direct local execution.
        ft.run(
            main=flet_main,
            assets_dir=str(ASSETS_DIR),
        )
