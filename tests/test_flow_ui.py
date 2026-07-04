"""Tests d'un flow d'interface de bout en bout (questionary stubé, sans réseau).

Exerce le parcours réel UI -> intent -> runner sur « Extraire l'audio », chemins
succès et échec (avec message d'erreur traduit).
"""
import ytdlp_interactif.ui.questionary_ui as ui
from ytdlp_interactif.core.runner import RunResult

_RAPIDE = "⚡ Rapide (MP3 192 kbps, pochette + tags, dossier auto)"


class _Ret:
    def __init__(self, val):
        self._val = val

    def ask(self):
        return self._val


def _stub_questionary(monkeypatch, *, confirms):
    it = iter(confirms)
    monkeypatch.setattr(ui.questionary, "text", lambda *a, **k: _Ret("http://exemple/v"))
    monkeypatch.setattr(ui.questionary, "select", lambda *a, **k: _Ret(_RAPIDE))
    monkeypatch.setattr(ui.questionary, "confirm", lambda *a, **k: _Ret(next(it)))


def test_flow_audio_succes(monkeypatch, capsys):
    # confirms : voir la commande ? non ; lancer ? oui
    _stub_questionary(monkeypatch, confirms=[False, True])
    monkeypatch.setattr(
        ui, "run_extract_audio",
        lambda plan: iter([RunResult(returncode=0, ok=True, errors=[])]),
    )
    ui._flow_extract_audio()
    out = capsys.readouterr().out
    assert "Terminé" in out


def test_flow_audio_echec_message_clair(monkeypatch, capsys):
    # confirms : voir la commande ? non ; lancer ? oui ; voir détails ? non
    _stub_questionary(monkeypatch, confirms=[False, True, False])
    monkeypatch.setattr(
        ui, "run_extract_audio",
        lambda plan: iter([RunResult(returncode=1, ok=False,
                                     errors=["ERROR: [youtube] x: Video unavailable"])]),
    )
    ui._flow_extract_audio()
    out = capsys.readouterr().out
    assert "pas disponible" in out           # message traduit, pas l'erreur brute
    assert "Video unavailable" not in out    # brut caché (détails non demandés)
