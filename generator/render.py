"""Render handwritten-format documents as noisy images (skew, smudges, low contrast).
The clean text layer stays in the case JSON as ground truth. Font: Caveat (SIL OFL 1.1)."""
import json, pathlib, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
FONT = pathlib.Path(__file__).resolve().parent / "fonts" / "caveat-latin-400-normal.woff"


def render(doc, seed, out_path):
    rng = random.Random(f"{seed}:{doc['doc_id']}")
    font = ImageFont.truetype(str(FONT), 30)
    lines = doc["text"].replace("₵", "c").split("\n")
    w = 160 + max(int(font.getlength(l)) for l in lines)
    h = 60 + 42 * len(lines)
    img = Image.new("L", (w, h), 236)
    d = ImageDraw.Draw(img)
    y = 30
    for l in lines:
        x = 30 + rng.randint(-4, 6)
        parts = l.split("[illegible]")
        for k, part in enumerate(parts):
            d.text((x, y + rng.randint(-2, 2)), part, font=font, fill=rng.randint(60, 110))
            x += int(font.getlength(part))
            if k < len(parts) - 1:
                d.ellipse((x, y + 4, x + 90, y + 34), fill=rng.randint(120, 150))  # smudge
                x += 95
        y += 42
    for _ in range(int(w * h / 900)):  # speckle noise
        px, py = rng.randrange(w), rng.randrange(h)
        d.point((px, py), fill=rng.randint(150, 200))
    img = img.rotate(rng.uniform(-1.5, 1.5), expand=True, fillcolor=236).filter(ImageFilter.GaussianBlur(0.6))
    img.save(out_path, optimize=True)


def main():
    out = ROOT / "cases" / "images"; out.mkdir(parents=True, exist_ok=True)
    n = 0
    for sub in ("fixed", "eval"):
        for f in sorted((ROOT / "cases" / sub).glob("*.json")):
            case = json.loads(f.read_text(encoding="utf-8"))
            for doc in case["documents"]:
                if doc["format"] == "handwritten":
                    render(doc, case["meta"]["seed"], out / f"{case['meta']['case_id']}_{doc['doc_id']}.png"); n += 1
    print(f"rendered {n} handwritten-style images")


if __name__ == "__main__":
    main()
