"""
make_short.py — הופך תסריט טקסט לסרטון 9:16 עם קריינות בעברית וכתוביות.

שימוש:
    python make_short.py ..\\content\\scripts\\01-red-stocks.txt backgrounds\\screen.mp4 out\\01.mp4
    python make_short.py --all ..\\content\\scripts backgrounds\\screen.mp4 out

רקע: הקלטת מסך של הגיליון (נתוני דמה בלבד!) או כל וידאו אנכי/אופקי.
דרישות: Python 3.10+, ffmpeg ב-PATH, pip install edge-tts
"""
import asyncio, os, subprocess, sys, pathlib, tempfile
import edge_tts

VOICE = os.environ.get("TTS_VOICE", "he-IL-AvriNeural")   # או he-IL-HilaNeural
RATE = os.environ.get("TTS_RATE", "+8%")


def spoken_text(path: pathlib.Path) -> str:
    """שורות שמתחילות ב-# הן הערות במאי ולא מוקראות."""
    lines = [l.strip() for l in path.read_text(encoding="utf-8").splitlines()]
    return " ".join(l for l in lines if l and not l.startswith("#"))


async def tts(text: str, mp3: str, srt: str) -> None:
    com = edge_tts.Communicate(text, VOICE, rate=RATE)
    subs = edge_tts.SubMaker()
    with open(mp3, "wb") as f:
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
                subs.feed(chunk)
    with open(srt, "w", encoding="utf-8") as f:
        f.write(subs.get_srt())


def render(bg: str, mp3: str, srt: str, out: str) -> None:
    # ffmpeg subtitles filter needs forward slashes and an escaped drive colon on Windows
    srt_ff = srt.replace("\\", "/").replace(":", "\\:")
    vf = ("scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
          f"subtitles='{srt_ff}':force_style='FontName=Arial,Fontsize=15,Bold=1,"
          "PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Alignment=2,MarginV=60'")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", bg, "-i", mp3,
                    "-vf", vf, "-shortest", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", out], check=True)


def make(script: pathlib.Path, bg: str, out: pathlib.Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        mp3, srt = os.path.join(tmp, "voice.mp3"), os.path.join(tmp, "subs.srt")
        asyncio.run(tts(spoken_text(script), mp3, srt))
        render(bg, mp3, srt, str(out))
    print("✓", out)


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] == "--all":
        src, bg, outdir = pathlib.Path(sys.argv[2]), sys.argv[3], pathlib.Path(sys.argv[4])
        for s in sorted(src.glob("*.txt")):
            make(s, bg, outdir / (s.stem + ".mp4"))
    elif len(sys.argv) == 4:
        make(pathlib.Path(sys.argv[1]), sys.argv[2], pathlib.Path(sys.argv[3]))
    else:
        print(__doc__)
        sys.exit(1)
