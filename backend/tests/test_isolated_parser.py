import pytest
from app.services.isolated_parser import SLOTS, parse_isolated


def test_process_parses_text_and_releases_capacity():
    text = b'Users manage projects and generate reports with the customer portal.'
    assert parse_isolated(text, 'text/plain')['raw_text'] == text.decode()
    assert parse_isolated(text, 'text/plain')['word_count'] > 0


def test_process_rejects_invalid_document():
    with pytest.raises(ValueError):
        parse_isolated(b'not a PDF', 'application/pdf')


def test_process_deadline_reclaims_worker():
    with pytest.raises(ValueError, match='deadline'):
        parse_isolated(b'example text', 'text/plain', timeout=0)
    assert parse_isolated(b'recovery after timeout', 'text/plain')['raw_text']


def test_overload_fails_without_queuing_unbounded_work():
    assert SLOTS.acquire(blocking=False)
    assert SLOTS.acquire(blocking=False)
    try:
        with pytest.raises(RuntimeError, match='busy'):
            parse_isolated(b'example', 'text/plain')
    finally:
        SLOTS.release()
        SLOTS.release()
