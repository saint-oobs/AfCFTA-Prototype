"""Optional live provider: Google Gemini API (free tier), called with the standard library only.

Runs LOCALLY via the CLI (python -m adapter.run --live ...). The API key is read from the environment
variable GEMINI_API_KEY and is never written to disk, the repo or the website.
Free-tier inputs may be used by Google to improve its products: send SYNTHETIC data only.
"""
import base64, hashlib, json, os, pathlib, urllib.request

PROMPTS = pathlib.Path(__file__).resolve().parent / "prompts"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
DEFAULT_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")


def _call(model, parts):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("Set GEMINI_API_KEY in your shell (never commit it).")
    body = {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"temperature": 0, "responseMimeType": "application/json"}}
    req = urllib.request.Request(ENDPOINT.format(model=model, key=key), data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read())
    text = resp["candidates"][0]["content"]["parts"][0]["text"]
    return text, resp.get("modelVersion", model)


def extract(documents, images_dir, case_id, operation_codes, model=DEFAULT_MODEL):
    template = (PROMPTS / "extract_v1.txt").read_text(encoding="utf-8")
    doc_txt, parts = [], []
    for d in documents:
        img = pathlib.Path(images_dir) / f"{case_id}_{d['doc_id']}.png"
        if d["format"] == "handwritten" and img.exists():
            doc_txt.append(f"[{d['doc_id']}] ({d['type']}) – see attached image {img.name}")
            parts.append({"inline_data": {"mime_type": "image/png", "data": base64.b64encode(img.read_bytes()).decode()}})
        else:
            doc_txt.append(f"[{d['doc_id']}] ({d['type']})\n{d['text']}")
    prompt = template.replace("{operation_codes}", ", ".join(operation_codes)).replace("{documents}", "\n\n".join(doc_txt))
    text, version = _call(model, [{"text": prompt}] + parts)
    return json.loads(text), {"model": model, "model_version": version,
                              "prompt_hash": hashlib.sha256(template.encode()).hexdigest()[:16],
                              "input_hash": hashlib.sha256(prompt.encode()).hexdigest()[:16]}


def explain(result, rule_ids, model=DEFAULT_MODEL):
    template = (PROMPTS / "explain_v1.txt").read_text(encoding="utf-8")
    slim = {k: result[k] for k in ("outcome", "components", "findings")}
    prompt = template.replace("{rule_ids}", ", ".join(rule_ids)).replace("{result}", json.dumps(slim)[:12000])
    text, version = _call(model, [{"text": prompt}])
    try:
        text = json.loads(text) if text.strip().startswith(("{", '"')) else text
        if isinstance(text, dict):
            text = text.get("explanation") or json.dumps(text)
    except json.JSONDecodeError:
        pass
    return text, {"model": model, "model_version": version, "prompt_hash": hashlib.sha256(template.encode()).hexdigest()[:16]}
