"""
FILE PURPOSE:
This is the "import hub" for all ORM (Object-Relational Mapping) models.
It imports all database models from the models/ folder and makes them available
to other parts of the application.

WHY THIS FILE EXISTS:
Instead of importing directly from models/lead.py everywhere,
we import from here. This makes it easier to add new models later.

THINK OF IT AS: A "shortcut" or "consolidation point" for all database models.
"""

# Import the Lead model (represents a doctor in the database)
from src.models.lead import Lead

# Export statement: tells Python which names are available when importing this module
# Users can now do: from src.db.models import Lead
__all__ = ["Lead"]
