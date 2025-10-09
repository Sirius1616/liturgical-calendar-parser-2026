import os
from src import schema

def test_schema_fields_defined():
    assert hasattr(schema, "DAY_DATA_FIELDS")
    assert isinstance(schema.DAY_DATA_FIELDS, list)
    assert "date" in schema.DAY_DATA_FIELDS
