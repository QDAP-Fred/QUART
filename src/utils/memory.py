from pyrit.memory import DuckDBMemory
from uuid import uuid4
from pyrit.models import PromptRequestPiece

duckdb_memory = DuckDBMemory()
duckdb_memory.export_all_tables()