from __future__ import annotations

import flet as ft

from ola_360.components.ui import card, chip, text
from ola_360.core.theme import PALETTE
from ola_360.services.ai_service import AIService


PROMPTS = [
    "What requires my attention today?",
    "Which commitments are overdue?",
    "Prepare tomorrow's PMO agenda.",
    "Draft an escalation message.",
    "Summarize unresolved engineering issues.",
]


def ai_view(ai: AIService) -> ft.Control:
    prompt = ft.TextField(label="Ask from stored app data", multiline=True, min_lines=2, border_radius=14)
    answer = ft.Column(spacing=8)

    def ask(e):
        result = ai.answer(prompt.value or "What requires my attention today?", include_private=False)
        answer.controls = [
            card(
                [
                    text(result["answer"], 14),
                    ft.Row([chip(f"Confidence: {result['confidence']}", PALETTE.emerald), chip(result["sources"], PALETTE.blue)], wrap=True),
                    ft.ExpansionTile(title=text("Supporting details and guardrails", 13, ft.FontWeight.BOLD), controls=[text(result["missing"], 12), text(result["fact_vs_inference"], 12)]),
                    ft.TextField(label="Editable draft before sending", value=result["answer"], multiline=True, min_lines=3, border_radius=14),
                ],
                accent=PALETTE.plum,
            )
        ]
        e.page.update()

    return ft.ListView(
        expand=True,
        spacing=12,
        controls=[
            text("AI Executive Chief of Staff", 24, ft.FontWeight.BOLD),
            text("Answers use stored organizational data. Private data is excluded unless My Day is explicitly opened.", 13, color=PALETTE.muted),
            ft.Row([ft.OutlinedButton(item, on_click=lambda e, item=item: setattr(prompt, "value", item) or e.page.update()) for item in PROMPTS[:3]], wrap=True),
            prompt,
            ft.ElevatedButton("Answer with safe fallback", icon=ft.Icons.AUTO_AWESOME, on_click=ask),
            answer,
        ],
    )
