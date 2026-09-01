from app.backend import core


def test_nombre_apellido_valido_con_tildes_y_espacios():
    assert core.validate_name("María José") is True


def test_nombre_apellido_invalido_con_numeros():
    assert core.validate_name("Juan123") is False


def test_nombre_apellido_invalido_con_apostrofe():
    assert core.validate_name("O'Connor") is False


def test_nombre_apellido_invalido_alfabeto_no_espanol():
    assert core.validate_name("Müller") is False


def test_nombre_apellido_valido_espacios_internos_multiples():
    assert core.validate_name("Juan   Pérez") is True


def test_nombre_apellido_valido_una_sola_letra():
    assert core.validate_name("A") is True


def test_email_valido_con_tld():
    assert core.validate_email("user@dominio.com") is True


def test_email_valido_sin_tld():
    assert core.validate_email("user@dominio") is True


def test_email_invalido_sin_arroba():
    assert core.validate_email("userdominio") is False


def test_email_invalido_con_espacios():
    assert core.validate_email("user @dominio.com") is False


def test_email_invalido_con_dos_arrobas():
    assert core.validate_email("user@dominio@com") is False


def test_email_invalido_parte_local_vacia():
    assert core.validate_email("@dominio.com") is False


def test_email_invalido_dominio_vacio():
    assert core.validate_email("user@") is False


def test_telefono_valido_numeros_y_guiones():
    assert core.validate_phone("11-4444-5555") is True


def test_telefono_invalido_con_letras():
    assert core.validate_phone("11-abcd") is False


def test_dni_formato_valido_ocho_digitos():
    assert core.validate_dni_format("30111222") is True


def test_dni_formato_valido_siete_digitos():
    assert core.validate_dni_format("3011122") is True


def test_dni_formato_invalido_longitud_corta():
    assert core.validate_dni_format("301112") is False


def test_dni_formato_invalido_con_puntos():
    assert core.validate_dni_format("30.111.222") is False


def test_trim_recorta_espacio_simple():
    assert core.trim_leading_trailing_space(" Juan ") == "Juan"


def test_trim_no_recorta_tab():
    assert core.trim_leading_trailing_space("\tJuan") == "\tJuan"


def test_dni_normaliza_ceros_a_la_izquierda():
    assert core.normalize_dni("0123456") == core.normalize_dni("123456")


def test_estado_inicial_es_activo():
    assert core.initial_status() == "Activo"


def test_try_normalize_dni_normaliza_ceros_a_la_izquierda():
    assert core.try_normalize_dni("0123456") == core.try_normalize_dni("123456")


def test_try_normalize_dni_devuelve_none_ante_letras():
    assert core.try_normalize_dni("abc") is None


def test_try_normalize_dni_devuelve_none_ante_puntos():
    assert core.try_normalize_dni("30.111.222") is None


def test_normalize_search_text_ignora_mayusculas():
    assert core.normalize_search_text("Perez") == core.normalize_search_text("perez")


def test_normalize_search_text_ignora_tildes():
    assert core.normalize_search_text("ÑOÑO") == core.normalize_search_text("ñoño")
    assert core.normalize_search_text("Pérez") == core.normalize_search_text("Perez")


def test_matches_search_por_nombre():
    query = core.normalize_search_text("jua")
    assert core.matches_search(query, dni=30111222, first_name="Juan", last_name="Perez") is True


def test_matches_search_por_apellido():
    query = core.normalize_search_text("pere")
    assert core.matches_search(query, dni=30111222, first_name="Juan", last_name="Perez") is True


def test_matches_search_por_dni_parcial():
    query = core.normalize_search_text("301112")
    assert core.matches_search(query, dni=30111222, first_name="Juan", last_name="Perez") is True


def test_matches_search_sin_coincidencia():
    query = core.normalize_search_text("gomez")
    assert core.matches_search(query, dni=30111222, first_name="Juan", last_name="Perez") is False
