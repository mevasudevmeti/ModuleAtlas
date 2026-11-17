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


def calculate_metrics(
    predictions: dict[int, bool],
    ground_truth: dict[int, bool],
) -> dict:

    tp = 0
    fp = 0
    tn = 0
    fn = 0

    for page_number, actual in ground_truth.items():

        predicted = predictions.get(
            page_number,
            False,
        )

        if predicted and actual:
            tp += 1

        elif predicted and not actual:
            fp += 1

        elif not predicted and actual:
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
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "accuracy": accuracy,
    }


def print_result(
    name: str,
    metrics: dict,
) -> None:

    print(f"\n{name}")
    print("-" * len(name))

    print(
        f"TP={metrics['tp']} "
        f"FP={metrics['fp']} "
        f"TN={metrics['tn']} "
        f"FN={metrics['fn']}"
    )

    print(
        f"Precision={metrics['precision']:.3f} "
        f"Recall={metrics['recall']:.3f} "
        f"F1={metrics['f1']:.3f} "
        f"Accuracy={metrics['accuracy']:.3f}"
    )


def main() -> None:

    if len(sys.argv) != 3:
        print(
            "Usage: python -m "
            "scripts.evaluate_extraction_rules "
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

    baseline_50: dict[int, bool] = {}
    baseline_125: dict[int, bool] = {}
    multi_signal_v1: dict[int, bool] = {}

    for page in document.pages:

        characters = len(
            page.text.strip()
        )

        baseline_50[page.page_number] = (
            characters < 50
        )

        baseline_125[page.page_number] = (
            characters < 125
        )

        multi_signal_v1[page.page_number] = (
            characters < 50
            or page.image_count >= 3
            or page.drawing_count >= 20
        )

    print_result(
        "Character baseline: 50",
        calculate_metrics(
            baseline_50,
            ground_truth,
        ),
    )

    print_result(
        "Character baseline: 125",
        calculate_metrics(
            baseline_125,
            ground_truth,
        ),
    )

    print_result(
        "Multi-signal heuristic v1",
        calculate_metrics(
            multi_signal_v1,
            ground_truth,
        ),
    )


if __name__ == "__main__":
    main()