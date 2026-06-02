from app.config import normalize_database_url


def test_normalize_render_postgres_url_uses_psycopg_driver():
    url = "postgres://user:pass@example.render.com/mana_hyderabad"

    assert normalize_database_url(url) == "postgresql+psycopg://user:pass@example.render.com/mana_hyderabad"


def test_normalize_plain_postgresql_url_uses_psycopg_driver():
    url = "postgresql://user:pass@example.render.com/mana_hyderabad"

    assert normalize_database_url(url) == "postgresql+psycopg://user:pass@example.render.com/mana_hyderabad"


def test_normalize_explicit_sqlalchemy_driver_url_is_unchanged():
    url = "postgresql+psycopg://user:pass@example.render.com/mana_hyderabad"

    assert normalize_database_url(url) == url
