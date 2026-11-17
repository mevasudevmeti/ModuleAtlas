import sys
from collections import defaultdict

import pymupdf


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: python -m "
            "scripts.inspect_repeated_images <pdf-path>"
        )
        raise SystemExit(1)

    pdf_path = sys.argv[1]

    image_occurrences = defaultdict(list)

    with pymupdf.open(pdf_path) as document:

        for page_number, page in enumerate(
            document,
            start=1,
        ):
            page_area = page.rect.get_area()

            images = page.get_image_info(
                hashes=True,
                xrefs=True,
            )

            for image in images:

                bbox = pymupdf.Rect(
                    image["bbox"]
                )

                coverage = (
                    bbox.get_area() / page_area
                    if page_area > 0
                    else 0
                )

                digest = image.get("digest")

                image_occurrences[digest].append(
                    {
                        "page": page_number,
                        "coverage": coverage,
                        "xref": image.get("xref"),
                        "width": image.get("width"),
                        "height": image.get("height"),
                    }
                )

    print("\n--- Repeated Images ---\n")

    for digest, occurrences in image_occurrences.items():

        if len(occurrences) <= 1:
            continue

        pages = [
            item["page"]
            for item in occurrences
        ]

        coverages = [
            item["coverage"]
            for item in occurrences
        ]

        first = occurrences[0]

        print(
            f"Occurrences: {len(occurrences)}, "
            f"Pages: {pages}"
        )

        print(
            f"Size: "
            f"{first['width']}x{first['height']}, "
            f"xref={first['xref']}"
        )

        print(
            f"Coverage range: "
            f"{min(coverages):.3f} - "
            f"{max(coverages):.3f}"
        )

        print()


if __name__ == "__main__":
    main()