import csv
import sys
from pathlib import Path

from app.services.document_ingestion import (
    DocumentIngestionService,
)
from app.services.extraction_analysis import (
    ExtractionAnalysisService,
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

            page_number = int(row["page_number"])

            needs_enhanced = (
                row["needs_enhanced_extraction"]
                .strip()
                .lower()
                == "true"
            )

            labels[page_number] = needs_enhanced

    return labels


def main() -> None:

    if len(sys.argv) != 3:
        print(
            "Usage: python -m "
            "scripts.evaluate_extraction_heuristic "
            "<pdf-path> <ground-truth-csv>"
        )
        raise SystemExit(1)

    pdf_path = Path(sys.argv[1])
    csv_path = Path(sys.argv[2])

    ingestion_service = DocumentIngestionService()

    document = ingestion_service.ingest_pdf(
        pdf_path
    )

    analysis_service = ExtractionAnalysisService()

    stats = analysis_service.analyse(
        document
    )

    ground_truth = load_ground_truth(
        csv_path,
        document.filename,
    )

    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0

    for page in stats.pages:

        predicted_enhanced = (
            page.classification
            in {"empty", "sparse"}
        )

        actual_enhanced = ground_truth.get(
            page.page_number
        )

        if actual_enhanced is None:
            continue

        if predicted_enhanced and actual_enhanced:
            true_positive += 1

        elif predicted_enhanced and not actual_enhanced:
            false_positive += 1

        elif not predicted_enhanced and actual_enhanced:
            false_negative += 1

        else:
            true_negative += 1

    total = (
        true_positive
        + false_positive
        + true_negative
        + false_negative
    )

    precision = (
        true_positive
        / (true_positive + false_positive)
        if true_positive + false_positive > 0
        else 0
    )

    recall = (
        true_positive
        / (true_positive + false_negative)
        if true_positive + false_negative > 0
        else 0
    )

    accuracy = (
        (true_positive + true_negative) / total
        if total > 0
        else 0
    )

    print("\n--- Extraction Heuristic Evaluation ---\n")

    print(f"True Positives: {true_positive}")
    print(f"False Positives: {false_positive}")
    print(f"True Negatives: {true_negative}")
    print(f"False Negatives: {false_negative}")

    print()

    print(f"Precision: {precision:.3f}")
    print(f"Recall: {recall:.3f}")
    print(f"Accuracy: {accuracy:.3f}")


if __name__ == "__main__":
    main()