from pathlib import Path

from app.idempotency import MemoryStore, SQLiteStore, build_store


def test_memory_store_marks_and_detects_dupes():
    s = MemoryStore()
    assert s.seen("stripe", "evt_1") is False
    s.mark("stripe", "evt_1")
    assert s.seen("stripe", "evt_1") is True
    # otro source con mismo event_id es independiente
    assert s.seen("conekta", "evt_1") is False


def test_sqlite_store_persists(tmp_path: Path):
    db = tmp_path / "idemp.db"
    s1 = SQLiteStore(db)
    s1.mark("stripe", "evt_42")
    # nuevo handle al mismo file: debe ver lo marcado
    s2 = SQLiteStore(db)
    assert s2.seen("stripe", "evt_42") is True
    assert s2.seen("stripe", "evt_43") is False


def test_build_store_factory(tmp_path: Path):
    mem = build_store("memory", tmp_path / "x.db")
    assert isinstance(mem, MemoryStore)
    sqlite = build_store("sqlite", tmp_path / "y.db")
    assert isinstance(sqlite, SQLiteStore)
