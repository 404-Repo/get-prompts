import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


class ImageGenerator:
    _WIDTH: int = 512
    _HEIGHT: int = 512

    @staticmethod
    def generate(*, output_dir: str, image_cnt: int) -> None:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        for i in range(image_cnt):
            try:
                salt = random.randint(0, 200000)
                img_path = Path(output_dir) / f"{i}_{salt}.webp"

                # Create a blank image
                img = Image.new("RGB", (ImageGenerator._WIDTH, ImageGenerator._HEIGHT), "white")

                # Add random background noise to simulate real images
                img = ImageGenerator._add_noise(img)

                # Draw multiple random shapes
                ImageGenerator._draw_random_shapes(img)

                # Apply slight blur to add realism
                img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0, 2)))  # noqa: S311

                # Save as Webp
                img.save(img_path, "WEBP", quality=100)
                print(f"Generated image at {img_path}")
            except Exception as e:
                print(f"Exception during generation of file {img_path}: {e}")

        print(f"✅ Successfully generated {image_cnt} heavy WebP images in '{output_dir}'")

    @staticmethod
    def _random_color() -> tuple[int, ...]:
        return tuple(random.randint(0, 255) for _ in range(3))  # noqa: S311

    @staticmethod
    def _add_noise(image: Image) -> Image:
        noise = np.random.randint(
            0, 50, (ImageGenerator._HEIGHT, ImageGenerator._WIDTH, 3), dtype="uint8"
        )  # noqa: S311
        noisy_image = Image.fromarray(np.clip(np.array(image) + noise, 0, 255).astype("uint8"))
        return noisy_image

    @staticmethod
    def _draw_random_shapes(image: Image) -> None:
        for _ in range(random.randint(5, 15)):  # noqa: S311
            shape_type = random.choice(["circle", "rectangle", "triangle", "line"])  # noqa: S311
            color = ImageGenerator._random_color()
            alpha = random.randint(100, 255)  # noqa: S311

            # Create transparent overlay for blending
            overlay = Image.new("RGBA", (ImageGenerator._WIDTH, ImageGenerator._HEIGHT), (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)

            if shape_type == "circle":
                x1, y1 = random.randint(20, 400), random.randint(20, 400)  # noqa: S311
                x2, y2 = x1 + random.randint(50, 150), y1 + random.randint(50, 150)  # noqa: S311
                overlay_draw.ellipse([x1, y1, x2, y2], fill=color + (alpha,))

            elif shape_type == "rectangle":
                x1, y1 = random.randint(20, 400), random.randint(20, 400)  # noqa: S311
                x2, y2 = x1 + random.randint(50, 150), y1 + random.randint(50, 150)  # noqa: S311
                overlay_draw.rectangle([x1, y1, x2, y2], fill=color + (alpha,))

            elif shape_type == "triangle":
                points = [
                    (random.randint(50, 450), random.randint(50, 450)),  # noqa: S311
                    (random.randint(50, 450), random.randint(50, 450)),  # noqa: S311
                    (random.randint(50, 450), random.randint(50, 450)),  # noqa: S311
                ]
                overlay_draw.polygon(points, fill=color + (alpha,))

            elif shape_type == "line":
                x1, y1 = random.randint(0, 512), random.randint(0, 512)  # noqa: S311
                x2, y2 = random.randint(0, 512), random.randint(0, 512)  # noqa: S311
                overlay_draw.line([x1, y1, x2, y2], fill=color + (alpha,), width=random.randint(5, 15))  # noqa: S311

            # Blend the overlay with the main image
            image.paste(overlay, (0, 0), overlay)


# ImageGenerator.generate(output_dir="resources/images/default", image_cnt=10000)
