# monkey_patch_sqlalchemy.py
import sqlalchemy.sql.elements as elements

# Remove temporariamente TypingOnly para Python 3.12
if hasattr(elements, "SQLCoreOperations"):
    SQLCoreOperations = elements.SQLCoreOperations
    bases = tuple(
        b for b in SQLCoreOperations.__bases__ if b.__name__ != "TypingOnly")
    SQLCoreOperations.__bases__ = bases
