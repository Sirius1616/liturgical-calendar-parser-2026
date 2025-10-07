# src/schema.py

SCHEMAS = {
    "daily_bible_citations_2026.csv": {
        "fields": {
            "Date": "date",
            "BibleCitationShort": "string",
            "SourceLine": "string"
        },
        "required": ["Date", "BibleCitationShort"]
    },

    "major_feasts_2026.csv": {
        "fields": {
            "FeastDate": "string",  # "Jan 4"
            "FeastName": "string",
            "Category": ["Solemnities of the Lord", "Marian Feasts", "Major Saints"]
        },
        "required": ["FeastDate", "FeastName", "Category"]
    },

   
    "weekly_index_2026.csv": {
        "fields": {
            "WeekNumber": "int",
            "StartDate": "date",
            "EndDate": "date",
        },
        "required": ["WeekNumber", "StartDate", "EndDate"]
    },

