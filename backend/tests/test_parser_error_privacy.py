from functools import partial
from unittest.mock import Mock

import pytest
from app.services import document_parser as module


@pytest.mark.parametrize("format_name", ["pdf", "docx", "txt"])
def test_parser_library_errors_do_not_expose_document_or_path(monkeypatch, format_name):
    private_detail = "private-client-document C:/private/customer.txt"
    logger = Mock()
    monkeypatch.setattr(module, "logger", logger)

    def fail(*args, **kwargs):
        raise RuntimeError(private_detail)

    if format_name == "pdf":
        monkeypatch.setattr("pdfplumber.open", fail)
        parse = partial(module.DocumentParser.parse, b"%PDF-malformed", "application/pdf")
    elif format_name == "docx":
        monkeypatch.setattr("docx.Document", fail)
        parse = partial(module.DocumentParser._parse_docx, b"malformed")
    else:
        monkeypatch.setattr(module.DocumentParser, "_parse_txt", fail)
        parse = partial(module.DocumentParser.parse, b"a document", "text/plain")

    with pytest.raises(ValueError) as error:
        parse()
    assert private_detail not in str(error.value)
    assert private_detail not in str(logger.mock_calls)
    assert logger.error.call_args.kwargs["error_type"] == "RuntimeError"
