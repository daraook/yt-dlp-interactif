"""Tests du runner : streaming d'événements via un process FACTICE (sans réseau)."""
from ytdlp_interactif.core.progress import ProgressEvent
from ytdlp_interactif.core.runner import LogLine, RunResult, run


class FakeProc:
    """Imite juste ce que le runner consomme d'un subprocess.Popen."""

    def __init__(self, lines, code):
        self.stdout = iter(lines)
        self._code = code
        self.received_command = None

    def wait(self):
        return self._code


def fake_factory(lines, code):
    def factory(command):
        proc = FakeProc(lines, code)
        proc.received_command = command
        return proc
    return factory


def test_runner_streame_progress_puis_termine_ok():
    lines = [
        "[youtube] Extracting URL",
        "[download] Destination: video.webm",
        "[download]  50.0% of 10.00MiB at 1.00MiB/s ETA 00:05",
        "[download] 100% of 10.00MiB in 00:03",
        "[ExtractAudio] Destination: video.mp3",
    ]
    events = list(run(["yt-dlp", "URL"], popen_factory=fake_factory(lines, 0)))

    # Dernier événement = résultat terminal OK.
    assert isinstance(events[-1], RunResult)
    assert events[-1].ok is True and events[-1].returncode == 0

    dl = [e for e in events if isinstance(e, ProgressEvent) and e.phase == "download"]
    assert [e.percent for e in dl] == [50.0, 100.0]
    assert any(isinstance(e, ProgressEvent) and e.phase == "postproc" for e in events)
    # Les lignes non-progress sont exposées comme LogLine (pour le mode détails).
    assert any(isinstance(e, LogLine) for e in events)


def test_runner_detecte_une_erreur():
    lines = [
        "[youtube] Extracting URL",
        "ERROR: [youtube] Video unavailable",
    ]
    events = list(run(["yt-dlp", "URL"], popen_factory=fake_factory(lines, 1)))
    res = events[-1]
    assert isinstance(res, RunResult)
    assert res.ok is False and res.returncode == 1
    assert any("unavailable" in line for line in res.errors)


def test_runner_ajoute_newline_dans_la_commande_par_defaut():
    """Le runner force --newline pour un parsing ligne à ligne fiable."""
    captured = {}

    def factory(command):
        captured["command"] = command
        return FakeProc([], 0)

    list(run(["yt-dlp", "URL"], popen_factory=factory))
    assert "--newline" in captured["command"]
