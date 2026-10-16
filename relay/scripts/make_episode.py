#!/usr/bin/env python3
"""Turn a Relay Brief into an episode.

  python3 make_episode.py brief.txt --out ~/site --theme "Your Monday book"

Checks the script against the brief rules, then voices it with ElevenLabs and
writes episodes/YYYY-MM-DD.mp3 plus an entry in episodes.json.

Credentials come from the environment and are never written to disk:
  ELEVENLABS_API_KEY   required for audio
  RELAY_VOICE_ID       required for audio
  RELAY_MODEL_ID       optional, defaults to eleven_turbo_v2_5

With no key it prints the script and the check results and stops cleanly, so
you can run the whole skill on dummy data without any setup.
"""
import argparse, datetime, io, json, os, re, shutil, subprocess, sys, urllib.request, urllib.error

ABBREV = r"\b(ARR|VP|CRM|SLA|QBR|CTO|CIO|CFO|SVP|API|NRR|ACV|Q[1-4])\b"

def check(text):
    """The brief rules, as a list of (ok, message)."""
    words = len(text.split())
    return [
        (200 <= words <= 225, "word count %d (target 200-225)" % words),
        (not re.search(r"\d", text), "digits: %s" % (re.findall(r"\d+", text)[:4] or "none")),
        (not re.search(r"[—–]", text), "em or en dashes: %d" % len(re.findall(r"[—–]", text))),
        (not re.search(ABBREV, text), "abbreviations: %s" % (re.findall(ABBREV, text)[:4] or "none")),
        ("•" not in text and not re.search(r"(?m)^\s*[-*]\s", text), "bullet points present" ),
    ]

def duration(path, text):
    """Real seconds if ffprobe is around, otherwise an estimate from the script."""
    if shutil.which("ffprobe"):
        try:
            out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                  "-of", "default=nw=1:nk=1", path],
                                 capture_output=True, text=True, timeout=20)
            if out.returncode == 0 and out.stdout.strip():
                return round(float(out.stdout.strip())), "measured"
        except Exception:
            pass
    return round(len(text.split()) / 150 * 60), "estimated"

def speak(text, voice, model, key):
    body = json.dumps({
        "text": text, "model_id": model,
        "voice_settings": {"stability": 0.45, "similarity_boost": 0.80,
                           "style": 0.15, "use_speaker_boost": True},
    }).encode()
    req = urllib.request.Request(
        "https://api.elevenlabs.io/v1/text-to-speech/%s" % voice, data=body,
        headers={"xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()

def main():
    p = argparse.ArgumentParser()
    p.add_argument("script", help="text file holding the brief, or - for stdin")
    p.add_argument("--out", default=".", help="site root that holds episodes/ and episodes.json")
    p.add_argument("--theme", default="Your Relay Brief")
    p.add_argument("--preview", default="")
    p.add_argument("--date", default=None, help="YYYY-MM-DD, defaults to today")
    a = p.parse_args()

    text = (sys.stdin.read() if a.script == "-" else io.open(a.script, encoding="utf-8").read()).strip()
    print("Brief checks")
    failed = 0
    for ok, msg in check(text):
        print("  %s %s" % ("PASS" if ok else "WARN", msg))
        failed += 0 if ok else 1
    if failed:
        print("  %d rule(s) to fix. Voicing anyway." % failed)

    key, voice = os.environ.get("ELEVENLABS_API_KEY"), os.environ.get("RELAY_VOICE_ID")
    if not key or not voice:
        missing = " and ".join(n for n, v in (("ELEVENLABS_API_KEY", key), ("RELAY_VOICE_ID", voice)) if not v)
        print("\nNo audio: %s not set. Here is the script to read or paste:\n" % missing)
        print(text)
        return 0

    day = a.date or datetime.date.today().isoformat()
    root = os.path.expanduser(a.out)
    os.makedirs(os.path.join(root, "episodes"), exist_ok=True)
    mp3 = os.path.join(root, "episodes", "%s.mp3" % day)
    try:
        audio = speak(text, voice, os.environ.get("RELAY_MODEL_ID", "eleven_turbo_v2_5"), key)
    except urllib.error.HTTPError as e:
        print("\nElevenLabs returned %s. Nothing written." % e.code)
        print((e.read()[:300] or b"").decode("utf-8", "replace"))
        return 1
    except Exception as e:
        print("\nCould not reach ElevenLabs: %s. Nothing written." % e)
        return 1
    io.open(mp3, "wb").write(audio)
    secs, how = duration(mp3, text)
    print("\nWrote %s (%d seconds, %s)" % (mp3, secs, how))

    jpath = os.path.join(root, "episodes.json")
    try:
        eps = json.load(io.open(jpath, encoding="utf-8"))
    except Exception:
        eps = []
    d = datetime.date.fromisoformat(day)
    pretty = "%s %d, %d" % (d.strftime("%b"), d.day, d.year)
    entry = {"date": pretty, "short": "%s %d" % (d.strftime("%b"), d.day), "theme": a.theme,
             "preview": a.preview or " ".join(text.split("\n\n")[1:3])[:240],
             "issue": [["Relay", text]], "file": "episodes/%s.mp3" % day, "dur": secs, "peaks": []}
    eps = [e for e in eps if e.get("file") != entry["file"]]
    eps.insert(0, entry)
    io.open(jpath, "w", encoding="utf-8").write(json.dumps(eps, indent=2, ensure_ascii=False))
    print("Added to %s as the newest episode." % jpath)
    return 0

if __name__ == "__main__":
    sys.exit(main())
