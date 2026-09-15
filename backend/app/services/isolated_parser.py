"""Bounded document parsing in disposable processes, never API worker threads."""
import multiprocessing
import threading

SLOTS = threading.BoundedSemaphore(2)
MAX_TEXT_CHARS = 1_000_000


def _parse_child(connection, content, mime_type):
    try:
        from app.services.document_parser import DocumentParser

        result = DocumentParser.parse(content, mime_type)
        if len(result['raw_text']) > MAX_TEXT_CHARS:
            raise ValueError('Extracted text exceeds limit')
        connection.send((True, result))
    except Exception:
        connection.send((False, None))
    finally:
        connection.close()


def parse_isolated(content: bytes, mime_type: str, timeout: float = 30.0) -> dict:
    if not SLOTS.acquire(blocking=False):
        raise RuntimeError('Document processing is busy')
    context = multiprocessing.get_context('spawn')
    parent, child = context.Pipe(duplex=False)
    process = context.Process(target=_parse_child, args=(child, content, mime_type), daemon=True)
    try:
        process.start()
        child.close()
        if not parent.poll(timeout):
            raise ValueError('Document parsing exceeded deadline')
        ok, result = parent.recv()
        if not ok:
            raise ValueError('Document could not be parsed')
        return result
    except EOFError:
        raise ValueError('Document parser stopped unexpectedly') from None
    finally:
        try:
            if process.pid is not None:
                if process.is_alive():
                    process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    process.kill()
                    process.join(timeout=5)
                process.close()
        finally:
            parent.close()
            child.close()
            SLOTS.release()
