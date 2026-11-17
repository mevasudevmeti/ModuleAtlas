import csv
import sys
from pathlib import Path

from app.services.document_ingestion import (
    DocumentIngestionService,
)


def load_ground_truth(
    csv_path: Path,
    document_name: str,
) -> dict[int, bool]:

    labels: dict[int, bool] = {}

    with csv_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            if row["document"] != document_name:
                continue

            labels[int(row["page_number"])] = (
                row["needs_enhanced_extraction"]
                .strip()
                .lower()
                == "true"
            )

    return labels


def evaluate_threshold(
    document,
    ground_truth: dict[int, bool],
    threshold: int,
) -> dict:

    tp = 0
    fp = 0
    tn = 0
    fn = 0

    for page in document.pages:

        character_count = len(page.text.strip())

        predicted_enhanced = (
            character_count < threshold
        )

        actual_enhanced = ground_truth.get(
            page.page_number
        )

        if actual_enhanced is None:
            continue

        if predicted_enhanced and actual_enhanced:
            tp += 1

        elif predicted_enhanced and not actual_enhanced:
            fp += 1

        elif not predicted_enhanced and actual_enhanced:
            fn += 1

        else:
            tn += 1

    precision = (
        tp / (tp + fp)
        if tp + fp > 0
        else 0
    )

    recall = (
        tp / (tp + fn)
        if tp + fn > 0
        else 0
    )

    f1 = (
        2 * precision * recall
        / (precision + recall)
        if precision + recall > 0
        else 0
    )

    accuracy = (
        (tp + tn)
        / (tp + fp + tn + fn)
    )

    return {
        "threshold": threshold,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
    }


def main() -> None:

    if len(sys.argv) != 3:
        print(
            "Usage: python -m "
            "scripts.evaluate_extraction_thresholds "
            "<pdf-path> <ground-truth-csv>"
        )
        raise SystemExit(1)

    pdf_path = Path(sys.argv[1])
    csv_path = Path(sys.argv[2])

    ingestion_service = DocumentIngestionService()

    document = ingestion_service.ingest_pdf(
        pdf_path
    )

    ground_truth = load_ground_truth(
        csv_path,
        document.filename,
    )

    thresholds = [
        25,
        50,
        75,
        100,
        125,
        150,
        200,
        250,
    ]

    print(
        "\n"
        "Threshold | Precision | Recall | F1    | Accuracy"
    )

    print("-" * 56)

    for threshold in thresholds:

        result = evaluate_threshold(
            document,
            ground_truth,
            threshold,
        )

        print(
            f"{threshold:9} | "
            f"{result['precision']:.3f}     | "
            f"{result['recall']:.3f}  | "
            f"{result['f1']:.3f} | "
            f"{result['accuracy']:.3f}"
        )


if __name__ == "__main__":
    main()