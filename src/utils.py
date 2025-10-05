#!/usr/bin/env python



def clean_text(text: str) -> str:
    """Basic cleanup: trim, normalize spaces, capitalize."""
    return " ".join(text.strip().split()).title()
