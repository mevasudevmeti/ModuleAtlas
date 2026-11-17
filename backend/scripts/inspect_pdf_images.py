import sys

import pymupdf


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: python -m scripts.inspect_pdf_images <pdf-path>"
        )
        raise SystemExit(1)

    pdf_path = sys.argv[1]

    with pymupdf.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):

            page_area = page.rect.get_area()

            images = page.get_image_info(
                hashes=True,
                xrefs=True,
            )

            print(f"\nPage {page_number}")

            for index, image in enumerate(images, start=1):

                bbox = pymupdf.Rect(
                    image["bbox"]
                )

                coverage = (
                    bbox.get_area() / page_area
                    if page_area > 0
                    else 0
                )

                print(
                    f"  Image {index}: "
                    f"coverage={coverage:.3f}, "
                    f"size={image['width']}x"
                    f"{image['height']}, "
                    f"xref={image.get('xref')}"
                )


if __name__ == "__main__":
    main()