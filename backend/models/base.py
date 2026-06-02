"""
Base Model
==========

Re-exports the SQLAlchemy declarative ``Base`` from the database
configuration module.  Models should import ``Base`` from here rather
than reaching into ``config.database`` directly, keeping the dependency
graph clean.
"""

from __future__ import annotations

from config.database import Base

__all__ = ["Base"]
