"""Apply the original pinned readability and compression rules to 72 new summaries."""

import importlib.util
import json
import platform
import sys
from pathlib import Path

import nltk
import textstat

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/full"))
from common import (CORPUS_SHA, GEN_FORMAT_SHA, GEN_PROMPT_SHA,
                    SAMPLE_SHA, frozen, load_selected, sha)  # noqa: E402
from check_generation_feasibility import (CLAUDE_MODEL, build_request)  # noqa: E402
from generate_full import (FORMAT, GEMMA_MODEL, MAX_OUTPUT_TOKENS,
                           OUTPUT as GENERATION, PROMPT, validate_existing)  # noqa: E402

spec = importlib.util.spec_from_file_location("pilot_basic_metrics", ROOT / "scripts/pilot/evaluate_basic_metrics.py")
pilot_metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot_metrics)

OUTPUT = ROOT / "data/extension/evaluation"
PROVIDERS = {"claude": CLAUDE_MODEL, "gemma": GEMMA_MODEL}


def main() -> None:
    if tuple(textstat.__version__) != (0, 7, 13):
        raise SystemExit(f"Expected textstat 0.7.13, got {textstat.__version__}")
    textstat.set_lang("en_US")
    dictionary_hash = pilot_metrics.cmudict_hash()
    _, selected = load_selected()
    prompt = frozen(PROMPT, GEN_PROMPT_SHA).decode("utf-8")
    fmt = json.loads(frozen(FORMAT, GEN_FORMAT_SHA))
    readability_rows, compression_rows = [], []
    for item in selected:
        number = item["sample"]["bill_number"]
        source = item["bill_text"]
        source_stats = pilot_metrics.readability(source)
        for provider, model in PROVIDERS.items():
            path = GENERATION / provider / f"{number}.json"
            body = build_request(provider, model, item, prompt, fmt, MAX_OUTPUT_TOKENS)
            validate_existing(path, item, provider, model, body)
            generation = json.loads(path.read_text(encoding="utf-8"))
            summary = generation["summary"]
            summary_stats = pilot_metrics.readability(summary)
            readability_rows.append({
                "bill_number": number, "cell": item["sample"]["cell"],
                "tertile": item["sample"]["tertile"], "provider": provider, "model": model,
                "source_sha256": item["sample"]["bill_text_sha256"],
                "summary_sha256": sha(summary.encode("utf-8")),
                "source": source_stats, "summary": summary_stats,
                "changes": {name: summary_stats[name] - source_stats[name] for name in
                            ("flesch_kincaid_grade", "flesch_reading_ease", "coleman_liau_index")},
            })
            source_words, summary_words = len(source.split()), len(summary.split())
            compression_rows.append({
                "bill_number": number, "cell": item["sample"]["cell"],
                "tertile": item["sample"]["tertile"], "provider": provider, "model": model,
                "source_whitespace_words": source_words,
                "summary_whitespace_words": summary_words,
                "summary_to_source_ratio": summary_words / source_words,
            })
    metadata = {
        "corpus_sha256": CORPUS_SHA, "sample_sha256": SAMPLE_SHA,
        "python_version": platform.python_version(),
        "textstat_version": ".".join(map(str, textstat.__version__)),
        "nltk_version": nltk.__version__, "cmudict_zip_sha256": dictionary_hash,
        "input_rule": "full cleaned bill_text and exact generated summary, no preprocessing",
        "original_method": "scripts/full/evaluate_basic_metrics.py",
    }
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, rows in (("readability", readability_rows), ("compression", compression_rows)):
        (OUTPUT / f"{name}.json").write_text(
            json.dumps({"metadata": metadata, "records": rows}, indent=2, allow_nan=False) + "\n",
            encoding="utf-8")
    print(f"Wrote pinned readability and compression for {len(readability_rows)} extension summaries")


if __name__ == "__main__":
    main()
