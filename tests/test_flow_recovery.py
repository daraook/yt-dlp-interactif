"""Tests des parcours de récupération sur échec (questionary stubé, sans réseau).

- Défi anti-robot YouTube -> relance automatique proposée avec le solveur officiel.
- Lot partiellement réussi -> compte rendu clair + reprise sûre proposée.
"""
from types import SimpleNamespace

import ytdlp_interactif.ui.questionary_ui as ui
from ytdlp_interactif.core.runner import RunResult

_RAPIDE = "⚡ Rapide (MP3 192 kbps, pochette + tags, dossier auto)"


class _Ret:
    def __init__(self, val):
        self._val = val

    def ask(self):
        return self._val


class _Runner:
    """Runner injectable : enregistre chaque commande, renvoie un résultat par appel."""

    def __init__(self, results):
        self._results = list(results)
        self.commands = []

    def __call__(self, plan):
        self.commands.append(list(plan.command))
        return iter([self._results[len(self.commands) - 1]])


def _stub(monkeypatch, confirms):
    it = iter(confirms)
    monkeypatch.setattr(ui.questionary, "text", lambda *a, **k: _Ret("http://exemple/v"))
    monkeypatch.setattr(ui.questionary, "select", lambda *a, **k: _Ret(_RAPIDE))
    monkeypatch.setattr(ui.questionary, "confirm", lambda *a, **k: _Ret(next(it)))


def test_bot_check_propose_et_relance_avec_ejs(monkeypatch, capsys):
    """Bot-check -> on propose la relance ; acceptée, elle ajoute --remote-components."""
    monkeypatch.setattr(ui.shutil, "which", lambda name: "/usr/bin/deno")
    runner = _Runner([
        RunResult(returncode=1, ok=False,
                  errors=["ERROR: [youtube] x: Sign in to confirm you're not a bot"]),
        RunResult(returncode=0, ok=True, errors=[]),
    ])
    monkeypatch.setattr(ui, "run_extract_audio", runner)
    # voir la commande ? non ; lancer ? oui ; réessayer avec le solveur ? oui
    _stub(monkeypatch, confirms=[False, True, True])

    ui._flow_extract_audio()
    out = capsys.readouterr().out

    assert "anti-robot" in out
    assert "Terminé" in out
    assert len(runner.commands) == 2
    assert "--remote-components" not in runner.commands[0]
    assert "--remote-components" in runner.commands[1]
    assert "ejs:github" in runner.commands[1]


def test_bot_check_sans_deno_signale_l_installation(monkeypatch, capsys):
    """Sans Deno, on prévient qu'il faut l'installer (solution sûre explicitée)."""
    monkeypatch.setattr(ui.shutil, "which", lambda name: None)
    runner = _Runner([
        RunResult(returncode=1, ok=False,
                  errors=["ERROR: Sign in to confirm you're not a bot"]),
    ])
    monkeypatch.setattr(ui, "run_extract_audio", runner)
    # voir la commande ? non ; lancer ? oui ; réessayer ? non ; voir détails ? non
    _stub(monkeypatch, confirms=[False, True, False, False])

    ui._flow_extract_audio()
    out = capsys.readouterr().out
    assert "Deno" in out and "deno.land" in out


def test_execute_succes_partiel_de_lot(tmp_path, monkeypatch, capsys):
    """Des fichiers existent malgré des échecs -> compte rendu partiel + reprise sûre."""
    (tmp_path / "ok1.mp3").write_text("x")
    plan = SimpleNamespace(
        command=["yt-dlp", "--download-archive", str(tmp_path / "a.txt"),
                 "-o", "t", "URL"],
        output_dir=tmp_path,
    )
    monkeypatch.setattr(ui.questionary, "confirm", lambda *a, **k: _Ret(False))

    def run_fn(_plan):
        return iter([RunResult(returncode=1, ok=False,
                               errors=["ERROR: item 3: Giving up after 10 retries"])])

    ui._execute(plan, run_fn)
    out = capsys.readouterr().out
    assert "échecs" in out
    assert "1 fichier" in out
    assert "Giving up" in out
    assert "anti-doublon" in out


def test_execute_echec_net_rassure_et_renvoie_vers_yt_dlp(tmp_path, monkeypatch, capsys):
    """Erreur inconnue, aucun fichier -> on rassure et on renvoie vers yt-dlp officiel."""
    plan = SimpleNamespace(command=["yt-dlp", "-o", "t", "URL"], output_dir=tmp_path)
    monkeypatch.setattr(ui.questionary, "confirm", lambda *a, **k: _Ret(False))

    def run_fn(_plan):
        return iter([RunResult(returncode=1, ok=False,
                               errors=["ERROR: quelque chose d'inédit 9x2"])])

    ui._execute(plan, run_fn)
    out = capsys.readouterr().out
    assert "interface" in out.lower()
    assert "yt-dlp" in out
