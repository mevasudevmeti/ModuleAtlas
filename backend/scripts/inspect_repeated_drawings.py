import math
import sys
from collections import defaultdict

import pymupdf


def normalise_style(value):
    if value is None:
        return None

    if isinstance(value, (tuple, list)):
        return tuple(
            round(float(item), 3)
            for item in value
        )

    if isinstance(value, (int, float)):
        return round(float(value), 3)

    return str(value)


def create_drawing_signature(
    drawing: dict,
    page_rect: pymupdf.Rect,
) -> tuple:

    rect = pymupdf.Rect(
        drawing["rect"]
    )

    page_width = page_rect.width
    page_height = page_rect.height

    normalised_rect = (
        round(rect.x0 / page_width, 3),
        round(rect.y0 / page_height, 3),
        round(rect.x1 / page_width, 3),
        round(rect.y1 / page_height, 3),
    )

    return (
        normalised_rect,
        drawing.get("type"),
        normalise_style(
            drawing.get("fill")
        ),
        normalise_style(
            drawing.get("color")
        ),
        round(
            float(
                drawing.get("width") or 0
            ),
            2,
        ),
        len(
            drawing.get("items") or []
        ),
    )


def main() -> None:

    if len(sys.argv) != 2:
        print(
            "Usage: python -m "
            "scripts.inspect_repeated_drawings "
            "<pdf-path>"
        )
        raise SystemExit(1)

    pdf_path = sys.argv[1]

    occurrences = defaultdict(set)

    with pymupdf.open(pdf_path) as document:

        page_count = len(document)

        for page_number, page in enumerate(
            document,
            start=1,
        ):

            drawings = page.get_drawings()

            signatures_on_page = set()

            for drawing in drawings:

                signature = (
                    create_drawing_signature(
                        drawing,
                        page.rect,
                    )
                )

                signatures_on_page.add(
                    signature
                )

            for signature in signatures_on_page:

                occurrences[signature].add(
                    page_number
                )

        minimum_pages = math.ceil(
            page_count * 0.8
        )

        print(
            "\n--- Repeated Drawings ---\n"
        )

        print(
            f"Document pages: {page_count}"
        )

        print(
            f"Template threshold: "
            f"{minimum_pages} pages"
        )

        print()

        for signature, pages in occurrences.items():

            if len(pages) < minimum_pages:
                continue

            (
                normalised_rect,
                drawing_type,
                fill,
                color,
                width,
                item_count,
            ) = signature

            x0, y0, x1, y1 = (
                normalised_rect
            )

            coverage = (
                (x1 - x0)
                * (y1 - y0)
            )

            print(
                f"Occurrences: "
                f"{len(pages)}/{page_count}"
            )

            print(
                f"Pages: {sorted(pages)}"
            )

            print(
                f"Normalised rect: "
                f"{normalised_rect}"
            )

            print(
                f"Approx coverage: "
                f"{coverage:.3f}"
            )

            print(
                f"Type: {drawing_type}, "
                f"fill={fill}, "
                f"color={color}, "
                f"width={width}, "
                f"items={item_count}"
            )

            print()


if __name__ == "__main__":
    main()