from app.services.analytics_service import sanitize_csv_cell


def test_leaves_ordinary_text_untouched() -> None:
    assert sanitize_csv_cell("Excess tuition fee charged") == "Excess tuition fee charged"


def test_neutralizes_formula_prefixes() -> None:
    assert sanitize_csv_cell("=cmd|'/c calc'!A1") == "'=cmd|'/c calc'!A1"
    assert sanitize_csv_cell("+1+1") == "'+1+1"
    assert sanitize_csv_cell("-2+3") == "'-2+3"
    assert sanitize_csv_cell("@SUM(A1:A2)") == "'@SUM(A1:A2)"


def test_empty_string_is_safe() -> None:
    assert sanitize_csv_cell("") == ""
