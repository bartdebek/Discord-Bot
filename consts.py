QUESTION_MODAL = """[
    {{
        "type": 9,
        "title": "Quiz question",
        "custom_id": "quiz_modal",
        "components": [
            {{
                "type": 1,
                "components": [
                    {{
                        "type": 4,
                        "custom_id": "question",
                        "style": 2,
                        "label": "Question",
                        "value": "{question}",
                        "required": false,
                        "disabled": true
                    }},
                    {{
                        "type": 4,
                        "custom_id": "answer",
                        "style": 1,
                        "label": "Your answer (1-4)",
                        "min_length": 1,
                        "max_length": 1,
                        "placeholder": "Enter 1, 2, 3 or 4"
                    }}
                ]
            }}
        ]
    }}
]"""

# JSON template for a message with buttons and an embedded media/image.
# This is the format you originally used before switching to modals.  The
# placeholder fields ({question}, {answer0}…{answer3}) are filled in by
# ``QuizView``; everything else is treated as literal JSON and therefore
# braces are doubled to escape them for ``str.format``.
QUESTION_BUTTONS = """[
    {{
        "type": 17,
        "accent_color": null,
        "spoiler": false,
        "components": [
            {{
                "type": 9,
                "accessory": {{
                    "type": 11,
                    "media": {{
                        "url": "https://powerspeech.pl/wp-content/uploads/2020/03/R_KOTARSKI-6-1.png.webp"
                    }},
                    "description": null,
                    "spoiler": false
                }},
                "components": [
                    {{
                        "type": 10,
                        "content": "{question}"
                    }}
                ]
            }},
            {{
                "type": 1,
                "components": [
                    {{
                        "type": 2,
                        "style": 1,
                        "label": "{answer0}",
                        "emoji": null,
                        "disabled": false,
                        "custom_id": "0"
                    }},
                    {{
                        "type": 2,
                        "style": 1,
                        "label": "{answer1}",
                        "emoji": null,
                        "disabled": false,
                        "custom_id": "1"
                    }},
                    {{
                        "type": 2,
                        "style": 1,
                        "label": "{answer2}",
                        "emoji": null,
                        "disabled": false,
                        "custom_id": "2"
                    }},
                    {{
                        "type": 2,
                        "style": 1,
                        "label": "{answer3}",
                        "emoji": null,
                        "disabled": false,
                        "custom_id": "3"
                    }}
                ]
            }}
        ]
    }}
]"""