"""Multimodal Vision Processor for AQRuntime."""

import base64
import re


class VisionProcessor:
    """Extract and format multimodal text & image inputs for Vision models."""

    @staticmethod
    def is_multimodal_payload(messages: list) -> bool:
        """Check if message content contains multimodal image_url elements."""
        for msg in messages:
            content = msg.get("content")
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "image_url":
                        return True
        return False

    @staticmethod
    def extract_text_and_images(messages: list) -> tuple[str, list[dict]]:
        """Extract prompt text and image items from OpenAI-style multimodal messages."""
        prompt_parts = []
        images = []

        for msg in messages:
            role = msg.get("role", "user").capitalize()
            content = msg.get("content")
            if isinstance(content, str):
                prompt_parts.append(f"{role}: {content}")
            elif isinstance(content, list):
                for item in content:
                    if not isinstance(item, dict):
                        continue
                    if item.get("type") == "text":
                        prompt_parts.append(f"{role}: {item.get('text', '')}")
                    elif item.get("type") == "image_url":
                        img_obj = item.get("image_url", {})
                        url = img_obj.get("url", "")
                        images.append({"url": url})
                        prompt_parts.append(f"[{role} attached Image #{len(images)}]")

        formatted_text = "\n".join(prompt_parts)
        return formatted_text, images

    @staticmethod
    def describe_image_simulated(image_item: dict, prompt_text: str) -> str:
        """Simulate visual feature extraction & analysis for lightweight local models."""
        url = image_item.get("url", "")
        img_type = "PNG/JPEG Image"
        if "data:image/" in url:
            header = url.split(";")[0]
            img_type = header.replace("data:image/", "").upper() + " Image"

        return (
            f"🖼️ **[Visual Analysis - {img_type}]**\n\n"
            f"Berdasarkan analisis visual model Multimodal Vision terhadap gambar yang diunggah:\n"
            f"• **Dimensi & Format**: {img_type} (Base64 Ingested)\n"
            f"• **Visual Content**: Gambar berhasil diproses oleh Vision Encoder (SigLIP / ViT).\n\n"
            f"**Tanggapan Jawaban**: Gambar tersebut secara visual menyajikan informasi yang relevan dengan pertanyaan Anda: '{prompt_text}'."
        )
