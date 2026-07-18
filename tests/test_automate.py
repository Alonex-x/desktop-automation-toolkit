import json
import os
import sys
import tarfile
import pytest
import automate


@pytest.fixture
def rules_path(tmp_path, monkeypatch):
    fake_path = tmp_path / "automate_rules.json"
    monkeypatch.setattr(automate, "get_rules_path", lambda: str(fake_path))
    return fake_path

def write_rules(path, rules):
    path.write_text(json.dumps({"rules": rules}), encoding="utf-8")

class TestLoadRules:
    def test_load_rules_validas(self, rules_path):
        reglas = [{"name": "borrar_torrents", "condition": {"type": "extension", "value": ".torrent"}, "action": "delete"}]
        write_rules(rules_path, reglas)
        resultado = automate.load_rules()
        assert resultado == reglas

    def test_load_rules_json_invalido(self, rules_path):
        rules_path.write_text("{ esto no es JSON válido ", encoding="utf-8")
        resultado = automate.load_rules()
        assert resultado == []

    def test_load_rules_archivo_no_existe(self, rules_path):
        assert not rules_path.exists()
        resultado = automate.load_rules()
        assert resultado == []

    def test_load_rules_clave_rules_no_es_lista(self, rules_path):
        rules_path.write_text(json.dumps({"rules": "no soy una lista"}), encoding="utf-8")
        resultado = automate.load_rules()
        assert resultado == []

class TestMatchRule:
    def test_match_rule_extension_string_simple(self):
        reglas = [{"name": "regla_pdf", "condition": {"type": "extension", "value": ".pdf"}, "action": "ignore"}]
        resultado = automate.match_rule("informe.pdf", reglas)
        assert resultado == reglas[0]

    def test_match_rule_extension_lista(self):
        reglas = [{"name": "regla_imagenes", "condition": {"type": "extension", "value": [".jpg", ".png", ".gif"]}, "action": "move", "destination": "imagenes"}]
        resultado_png = automate.match_rule("foto.png", reglas)
        resultado_jpg = automate.match_rule("foto.jpg", reglas)
        assert resultado_png == reglas[0]
        assert resultado_jpg == reglas[0]

    def test_match_rule_sin_coincidencia(self):
        reglas = [{"name": "regla_pdf", "condition": {"type": "extension", "value": ".pdf"}, "action": "ignore"}]
        resultado = automate.match_rule("documento.docx", reglas)
        assert resultado is None

    def test_match_rule_lista_vacia(self):
        resultado = automate.match_rule("cualquier_archivo.txt", [])
        assert resultado is None

    def test_match_rule_es_case_insensitive(self):
        reglas = [{"name": "regla_pdf", "condition": {"type": "extension", "value": ".PDF"}, "action": "ignore"}]
        resultado = automate.match_rule("informe.pdf", reglas)
        assert resultado == reglas[0]

class TestApplyRuleActionDelete:
    def test_delete_dry_run_no_elimina_archivo(self, tmp_path, capsys):
        archivo = tmp_path / "temporal.tmp"
        archivo.write_text("contenido")
        regla = {"name": "borrar_temp", "action": "delete"}
        consumido = automate.apply_rule_action(regla, str(archivo), str(tmp_path), dry_run=True)
        assert consumido is True
        assert archivo.exists()
        salida = capsys.readouterr().out
        assert "DRY RUN" in salida

    def test_delete_real_elimina_archivo(self, tmp_path):
        archivo = tmp_path / "temporal.tmp"
        archivo.write_text("contenido")
        regla = {"name": "borrar_temp", "action": "delete"}
        consumido = automate.apply_rule_action(regla, str(archivo), str(tmp_path), dry_run=False)
        assert consumido is True
        assert not archivo.exists()

class TestApplyRuleActionMove:
    def test_move_dry_run_no_mueve_archivo(self, tmp_path, capsys):
        archivo = tmp_path / "imagen.png"
        archivo.write_text("contenido")
        regla = {"name": "mover_imagenes", "action": "move", "destination": "imagenes"}
        consumido = automate.apply_rule_action(regla, str(archivo), str(tmp_path), dry_run=True)
        assert consumido is True
        assert archivo.exists()
        assert not (tmp_path / "imagenes").exists()
        salida = capsys.readouterr().out
        assert "DRY RUN" in salida

    def test_move_real_mueve_archivo_a_destino(self, tmp_path):
        archivo = tmp_path / "imagen.png"
        archivo.write_text("contenido")
        regla = {"name": "mover_imagenes", "action": "move", "destination": "imagenes"}
        consumido = automate.apply_rule_action(regla, str(archivo), str(tmp_path), dry_run=False)
        destino_esperado = tmp_path / "imagenes" / "imagen.png"
        assert consumido is True
        assert not archivo.exists()
        assert destino_esperado.exists()

    def test_move_sin_destination_no_lanza_excepcion(self, tmp_path):
        archivo = tmp_path / "imagen.png"
        archivo.write_text("contenido")
        regla = {"name": "mover_sin_destino", "action": "move"}
        consumido = automate.apply_rule_action(regla, str(archivo), str(tmp_path), dry_run=False)
        assert consumido is True
        assert archivo.exists()

class TestApplyRuleActionIgnore:
    def test_ignore_dry_run(self, tmp_path, capsys):
        archivo = tmp_path / "notas.txt"
        archivo.write_text("contenido")
        regla = {"name": "ignorar_notas", "action": "ignore"}
        consumido = automate.apply_rule_action(regla, str(archivo), str(tmp_path), dry_run=True)
        assert consumido is True
        assert archivo.exists()
        salida = capsys.readouterr().out
        assert "DRY RUN" in salida

    def test_ignore_real_no_elimina_ni_mueve(self, tmp_path):
        archivo = tmp_path / "notas.txt"
        archivo.write_text("contenido")
        regla = {"name": "ignorar_notas", "action": "ignore"}
        consumido = automate.apply_rule_action(regla, str(archivo), str(tmp_path), dry_run=False)
        assert consumido is True
        assert archivo.exists()

    def test_accion_desconocida_no_consume_el_archivo(self, tmp_path):
        archivo = tmp_path / "notas.txt"
        archivo.write_text("contenido")
        regla = {"name": "accion_rara", "action": "teletransportar"}
        consumido = automate.apply_rule_action(regla, str(archivo), str(tmp_path), dry_run=False)
        assert consumido is False
        assert archivo.exists()

class TestOrganizeByExtension:
    def test_organize_comportamiento_por_defecto(self, rules_path, tmp_path):
        (tmp_path / "documento.pdf").write_text("contenido")
        (tmp_path / "foto.jpg").write_text("contenido")
        automate.organize_by_extension(str(tmp_path), dry_run=False)
        assert (tmp_path / "pdf" / "documento.pdf").exists()
        assert (tmp_path / "jpg" / "foto.jpg").exists()

    def test_organize_reglas_personalizadas_tienen_prioridad(self, rules_path, tmp_path):
        reglas = [
            {
                "name": "torrents_a_papelera",
                "condition": {"type": "extension", "value": ".torrent"},
                "action": "move",
                "destination": "papelera",
            }
        ]
        write_rules(rules_path, reglas)
        (tmp_path / "pelicula.torrent").write_text("contenido")
        (tmp_path / "documento.pdf").write_text("contenido")
        automate.organize_by_extension(str(tmp_path), dry_run=False)
        assert (tmp_path / "papelera" / "pelicula.torrent").exists()
        assert not (tmp_path / "torrent").exists()
        assert (tmp_path / "pdf" / "documento.pdf").exists()

    def test_organize_regla_delete_elimina_archivo_en_lugar_de_organizarlo(self, rules_path, tmp_path):
        reglas = [{"name": "borrar_torrents", "condition": {"type": "extension", "value": ".torrent"}, "action": "delete"}]
        write_rules(rules_path, reglas)
        archivo = tmp_path / "pelicula.torrent"
        archivo.write_text("contenido")
        automate.organize_by_extension(str(tmp_path), dry_run=False)
        assert not archivo.exists()
        assert not (tmp_path / "torrent").exists()

    def test_organize_ignora_subdirectorios(self, rules_path, tmp_path):
        subdir = tmp_path / "ya_organizado"
        subdir.mkdir()
        automate.organize_by_extension(str(tmp_path), dry_run=False)
        assert subdir.exists()

class TestBackupDirectory:
    def test_backup_comprimido_crea_tar_gz(self, tmp_path):
        origen = tmp_path / "proyecto"
        origen.mkdir()
        (origen / "archivo.txt").write_text("datos importantes")
        destino = tmp_path / "backups"
        destino.mkdir()
        automate.backup_directory(str(origen), str(destino), compress=True)
        archivos_backup = list(destino.glob("backup_*.tar.gz"))
        assert len(archivos_backup) == 1
        with tarfile.open(archivos_backup[0], "r:gz") as tar:
            nombres = tar.getnames()
            assert any("archivo.txt" in nombre for nombre in nombres)

    def test_backup_sin_comprimir_copia_directorio(self, tmp_path):
        origen = tmp_path / "proyecto"
        origen.mkdir()
        (origen / "archivo.txt").write_text("datos importantes")
        destino = tmp_path / "backups"
        destino.mkdir()
        automate.backup_directory(str(origen), str(destino), compress=False)
        copia = destino / "proyecto" / "archivo.txt"
        assert copia.exists()
        assert copia.read_text() == "datos importantes"
