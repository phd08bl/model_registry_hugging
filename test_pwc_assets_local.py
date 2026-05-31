"""
test_pwc_assets_local.py

Tests local/offline loading of:
- Hugging Face models
- SentenceTransformer model
- BERTScore local model
- NLTK data
- SummaC asset
- spaCy model
- Optional FlashRank cache

Run after downloading/transferring ./model_registry:

    python test_pwc_assets_local.py
"""

from pathlib import Path
import os
import subprocess
import sys
import traceback


# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------

BASE_DIR = Path("./model_registry").resolve()
HF_DIR = BASE_DIR / "huggingface"
NLTK_DIR = BASE_DIR / "nltk_data"
SUMMAC_DIR = BASE_DIR / "summac"
SPACY_DIR = BASE_DIR / "spacy_models"
FLASHRANK_DIR = BASE_DIR / "flashrank"

# Force offline behaviour.
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["NLTK_DATA"] = str(NLTK_DIR)

TEST_RESULTS = []


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def assert_exists(path: Path, description: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing {description}: {path}")
    print(f"Found {description}: {path}")


def record_result(name: str, status: str, error: str | None = None) -> None:
    TEST_RESULTS.append({
        "name": name,
        "status": status,
        "error": error,
    })


def run_test(name: str, func) -> None:
    print_section(name)

    try:
        func()
        print(f"\nPASS: {name}")
        record_result(name, "PASS")
    except Exception as exc:
        print(f"\nFAIL: {name}")
        print(f"Error: {exc}")
        print("\nTraceback:")
        traceback.print_exc()
        record_result(name, "FAIL", str(exc))


def print_summary() -> None:
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for result in TEST_RESULTS:
        status = result["status"]
        name = result["name"]

        if status == "PASS":
            print(f"[PASS] {name}")
        else:
            print(f"[FAIL] {name}")
            print(f"       {result['error']}")

    failures = [r for r in TEST_RESULTS if r["status"] == "FAIL"]

    print("\n" + "-" * 80)

    if failures:
        print(f"{len(failures)} test(s) failed.")
    else:
        print("All tests passed.")


def list_files(path: Path) -> None:
    if not path.exists():
        print(f"Path does not exist: {path}")
        return

    print(f"Files in {path}:")
    for item in sorted(path.iterdir()):
        print(f" - {item.name}")


# ---------------------------------------------------------------------
# 1. Test Transformers models
# ---------------------------------------------------------------------

def load_tokenizer(local_name: str, path: Path):
    from transformers import AutoTokenizer

    # ALBERT commonly requires SentencePiece.
    # use_fast=False avoids fast-tokenizer conversion issues when tokenizer.json
    # is absent or incomplete.
    if local_name == "albert-xlarge-vitaminc":
        spiece_path = path / "spiece.model"

        if not spiece_path.exists():
            list_files(path)
            raise FileNotFoundError(
                "ALBERT tokenizer requires spiece.model, but it was not found. "
                f"Expected file: {spiece_path}. "
                "Install sentencepiece and repair/re-download this model folder."
            )

        print("ALBERT detected. Loading tokenizer with use_fast=False.")
        return AutoTokenizer.from_pretrained(
            str(path),
            local_files_only=True,
            use_fast=False,
        )

    return AutoTokenizer.from_pretrained(
        str(path),
        local_files_only=True,
    )


def test_transformers_model(local_name: str, model_type: str = "base") -> None:
    from transformers import AutoModel, AutoModelForSequenceClassification
    import torch

    path = HF_DIR / local_name
    assert_exists(path, f"HF model folder for {local_name}")

    list_files(path)

    print(f"\nLoading tokenizer from: {path}")
    tokenizer = load_tokenizer(local_name, path)

    if model_type == "sequence_classification":
        print(f"Loading sequence classification model from: {path}")
        model = AutoModelForSequenceClassification.from_pretrained(
            str(path),
            local_files_only=True,
        )
    else:
        print(f"Loading base model from: {path}")
        model = AutoModel.from_pretrained(
            str(path),
            local_files_only=True,
        )

    text = "This is a local offline model loading test."
    inputs = tokenizer(text, return_tensors="pt", truncation=True)

    with torch.no_grad():
        outputs = model(**inputs)

    print(f"\n{local_name} loaded successfully.")
    print(f"Output object type: {type(outputs)}")

    if hasattr(model.config, "id2label"):
        print(f"id2label: {model.config.id2label}")


def test_bert_base_uncased() -> None:
    test_transformers_model(
        local_name="bert-base-uncased",
        model_type="base",
    )


def test_toxic_bert() -> None:
    test_transformers_model(
        local_name="toxic-bert",
        model_type="sequence_classification",
    )


def test_albert_xlarge_vitaminc() -> None:
    test_transformers_model(
        local_name="albert-xlarge-vitaminc",
        model_type="sequence_classification",
    )


def test_deberta_xlarge_mnli() -> None:
    test_transformers_model(
        local_name="deberta-xlarge-mnli",
        model_type="sequence_classification",
    )


# ---------------------------------------------------------------------
# 2. Test SentenceTransformer model
# ---------------------------------------------------------------------

def test_sentence_transformer() -> None:
    from sentence_transformers import SentenceTransformer

    path = HF_DIR / "all-MiniLM-L6-v2"
    assert_exists(path, "SentenceTransformer folder")

    list_files(path)

    model = SentenceTransformer(str(path))

    embeddings = model.encode([
        "This is a local embedding test.",
        "This is another local sentence.",
    ])

    print("SentenceTransformer loaded successfully.")
    print(f"Embedding shape: {embeddings.shape}")


# ---------------------------------------------------------------------
# 3. Test BERTScore local model usage
# ---------------------------------------------------------------------

def test_bert_score() -> None:
    try:
        from bert_score import score
    except ImportError:
        print("bert_score is not installed. Skipping BERTScore test.")
        return

    model_path = HF_DIR / "bert-base-uncased"
    assert_exists(model_path, "BERTScore local model folder")

    candidates = ["The company reported strong growth."]
    references = ["The company reported strong revenue growth."]

    precision, recall, f1 = score(
        candidates,
        references,
        model_type=str(model_path),
        lang="en",
        verbose=False,
    )

    print("BERTScore loaded local model successfully.")
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F1: {f1}")


# ---------------------------------------------------------------------
# 4. Test NLTK data
# ---------------------------------------------------------------------

def test_nltk_data() -> None:
    import nltk

    nltk.data.path.append(str(NLTK_DIR))

    assert_exists(NLTK_DIR, "NLTK data folder")

    text = "This is sentence one. This is sentence two."
    sentences = nltk.sent_tokenize(text)

    print("NLTK sentence tokenisation successful.")
    print(sentences)


# ---------------------------------------------------------------------
# 5. Test SummaC asset file
# ---------------------------------------------------------------------

def test_summac_asset() -> None:
    asset_path = SUMMAC_DIR / "summac_conv_vitc_sent_perc_e.bin"
    assert_exists(asset_path, "SummaC convolution asset")

    print("SummaC asset exists.")

    try:
        import summac  # noqa: F401
        print("summac package import successful.")
    except ImportError:
        print("summac package is not installed. Asset file exists, but SummaC import skipped.")


# ---------------------------------------------------------------------
# 6. Test spaCy local model
# ---------------------------------------------------------------------

def install_spacy_wheel_if_needed() -> None:
    try:
        import en_core_web_sm  # noqa: F401
        print("en_core_web_sm already installed.")
        return
    except ImportError:
        pass

    wheels = list(SPACY_DIR.glob("en_core_web_sm-*.whl"))

    if not wheels:
        print(f"No en_core_web_sm wheel found in: {SPACY_DIR}")
        print("Skipping spaCy model install.")
        return

    wheel = wheels[0]
    print(f"Installing spaCy model from local wheel: {wheel}")

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            str(wheel),
            "--no-index",
        ],
        check=True,
    )


def test_spacy_model() -> None:
    try:
        import spacy
    except ImportError:
        print("spacy is not installed. Skipping spaCy test.")
        return

    install_spacy_wheel_if_needed()

    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError as exc:
        print("Could not load en_core_web_sm.")
        print("Install the local wheel manually from model_registry/spacy_models.")
        raise exc

    doc = nlp("This is a local spaCy test.")

    print("spaCy model loaded successfully.")
    print([token.text for token in doc])


# ---------------------------------------------------------------------
# 7. Test optional FlashRank
# ---------------------------------------------------------------------

def test_flashrank() -> None:
    try:
        from flashrank import Ranker, RerankRequest
    except ImportError:
        print("flashrank is not installed. Skipping FlashRank test.")
        return

    try:
        ranker = Ranker(
            model_name="ms-marco-MiniLM-L-12-v2",
            cache_dir=str(FLASHRANK_DIR),
        )
    except TypeError:
        print("FlashRank version may not support cache_dir. Trying default Ranker.")
        ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2")

    request = RerankRequest(
        query="What is model validation?",
        passages=[
            {
                "id": 1,
                "text": "Model validation checks whether a model is robust and fit for purpose.",
            },
            {
                "id": 2,
                "text": "The weather is sunny today.",
            },
        ],
    )

    results = ranker.rerank(request)

    print("FlashRank loaded successfully.")
    print(results)


# ---------------------------------------------------------------------
# 8. Quick ALBERT NLI test
# ---------------------------------------------------------------------

def test_albert_nli_pair() -> None:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch

    path = HF_DIR / "albert-xlarge-vitaminc"
    assert_exists(path, "ALBERT VitaminC folder")

    spiece_path = path / "spiece.model"
    assert_exists(spiece_path, "ALBERT SentencePiece tokenizer file")

    tokenizer = AutoTokenizer.from_pretrained(
        str(path),
        local_files_only=True,
        use_fast=False,
    )

    model = AutoModelForSequenceClassification.from_pretrained(
        str(path),
        local_files_only=True,
    )

    premise = "The company reported strong revenue growth."
    hypothesis = "The company performed well."

    inputs = tokenizer(
        premise,
        hypothesis,
        return_tensors="pt",
        truncation=True,
    )

    with torch.no_grad():
        outputs = model(**inputs)

    print("ALBERT pairwise NLI test completed.")
    print(f"Logits: {outputs.logits}")
    print(f"id2label: {model.config.id2label}")


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    print(f"Testing local assets from: {BASE_DIR}")

    assert_exists(BASE_DIR, "base model registry folder")
    assert_exists(HF_DIR, "Hugging Face model folder")

    run_test("Test bert-base-uncased", test_bert_base_uncased)
    run_test("Test toxic-bert", test_toxic_bert)
    run_test("Test albert-xlarge-vitaminc", test_albert_xlarge_vitaminc)
    run_test("Test albert-xlarge-vitaminc pairwise NLI", test_albert_nli_pair)
    run_test("Test deberta-xlarge-mnli", test_deberta_xlarge_mnli)
    run_test("Test all-MiniLM-L6-v2 SentenceTransformer", test_sentence_transformer)
    run_test("Test BERTScore with local BERT", test_bert_score)
    run_test("Test NLTK data", test_nltk_data)
    run_test("Test SummaC asset", test_summac_asset)
    run_test("Test spaCy model", test_spacy_model)
    run_test("Test optional FlashRank", test_flashrank)

    print_summary()


if __name__ == "__main__":
    main()