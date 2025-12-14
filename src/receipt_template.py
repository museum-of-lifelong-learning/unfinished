"""
Receipt Template System for Thermal Printer Output.
Uses Jinja2 for text templating and PIL for image composition.
"""
from dataclasses import dataclass, field
from typing import Optional, List
from PIL import Image, ImageDraw, ImageFont
from jinja2 import Environment, FileSystemLoader, BaseLoader
import os
import textwrap

# Paper width for TM-T88V/TM-T70II profile (80mm paper, 512px at 180dpi)
PAPER_WIDTH_PX = 512
CHAR_WIDTH = 42  # Approximate characters per line for standard font


@dataclass
class ReceiptData:
    """Data structure for receipt content."""
    # Header
    image_path: str
    image_overlay_text: str
    figurine_number: str
    total_count: str
    
    # Body
    body_paragraphs: List[str] = field(default_factory=list)
    mighty_question: str = ""
    informal_opportunity: str = ""
    official_offer: str = ""
    inspiration: str = ""
    next_step: str = ""
    
    # QR Code
    qr_url: str = ""
    
    # Footer
    footer_quote: str = ""
    footer_quote_author: str = ""
    footer_thanks: List[str] = field(default_factory=list)


class ReceiptRenderer:
    """Renders receipts using templates and PIL for image composition."""
    
    def __init__(self, template_dir: Optional[str] = None, font_path: Optional[str] = None):
        self.paper_width = PAPER_WIDTH_PX
        self.char_width = CHAR_WIDTH
        
        # Setup Jinja2 environment
        if template_dir and os.path.isdir(template_dir):
            self.jinja_env = Environment(loader=FileSystemLoader(template_dir))
        else:
            self.jinja_env = Environment(loader=BaseLoader())
        
        # Font setup - DejaVu as default
        self.font_path = font_path or self._find_dejavu_font()
        self.overlay_font_size = 28
        
    def _find_dejavu_font(self) -> str:
        """Find DejaVu font on the system."""
        possible_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/DejaVuSans-Bold.ttf",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return ""  # Will use default PIL font
    
    def create_image_with_overlay(self, image_path: str, overlay_text: str) -> Image.Image:
        """
        Create an image with text overlay, resized to fit paper width.
        Text is centered vertically on the image.
        Image is cropped to 50% height (not compressed) to maintain aspect ratio.
        """
        img = Image.open(image_path).convert('RGB')
        
        # Resize to paper width while maintaining aspect ratio
        if img.width != self.paper_width:
            ratio = self.paper_width / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((self.paper_width, new_height), Image.Resampling.LANCZOS)
        
        # Crop to 50% height (center crop) instead of compressing
        target_height = img.height // 2
        top = (img.height - target_height) // 2
        bottom = top + target_height
        img = img.crop((0, top, self.paper_width, bottom))
        
        # Draw overlay text
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype(self.font_path, self.overlay_font_size)
        except (IOError, OSError):
            font = ImageFont.load_default()
        
        # Wrap text to fit image width (with some padding)
        max_text_width = self.paper_width - 40  # 20px padding on each side
        lines = self._wrap_text_to_width(overlay_text, font, max_text_width, draw)
        
        # Calculate total text block height
        line_heights = []
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_heights.append(bbox[3] - bbox[1])
        
        total_text_height = sum(line_heights) + (len(lines) - 1) * 5  # 5px line spacing
        
        # Center vertically
        y_start = (img.height - total_text_height) // 2
        
        # Draw each line centered horizontally
        y = y_start
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (img.width - text_width) // 2
            
            # Draw text with thick outline and filled center for maximum visibility
            outline_color = "black"
            text_color = "white"
            outline_width = 3
            
            # Draw thick outline
            for dx in range(-outline_width, outline_width + 1):
                for dy in range(-outline_width, outline_width + 1):
                    if dx != 0 or dy != 0:
                        draw.text((x + dx, y + dy), line, font=font, fill=outline_color)
            
            # Draw filled main text
            draw.text((x, y), line, font=font, fill=text_color)
            
            y += line_heights[i] + 5
        
        return img
    
    def _wrap_text_to_width(self, text: str, font, max_width: int, draw) -> List[str]:
        """Wrap text to fit within max_width pixels."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def render_to_printer(self, printer, data: ReceiptData):
        """
        Render the full receipt to a printer instance.
        """
        # === HEADER: Image with overlay ===
        if data.image_path and os.path.exists(data.image_path):
            img = self.create_image_with_overlay(data.image_path, data.image_overlay_text)
            printer.image(img)
        
        printer.set(align='center')
        printer.ln()
        
        # Figurine number
        printer.textln(f"Figurina Nr. {data.figurine_number} / {data.total_count}")
        printer.ln()
        
        # === BODY ===
        printer.set(align='left')
        
        # Body paragraphs
        for para in data.body_paragraphs:
            wrapped = textwrap.fill(para, width=self.char_width)
            printer.textln(wrapped)
            printer.ln()
        
        # Labeled sections (bold labels)
        if data.mighty_question:
            self._print_labeled_section(printer, "Mächtige Frage:", data.mighty_question)
        
        if data.informal_opportunity:
            self._print_labeled_section(printer, "Informal Opportunity:", data.informal_opportunity)
        
        if data.official_offer:
            self._print_labeled_section(printer, "Offizielles Angebot:", data.official_offer)
        
        if data.inspiration:
            self._print_labeled_section(printer, "Inspiration:", data.inspiration)
        
        if data.next_step:
            self._print_labeled_section(printer, "Nächster Schritt:", data.next_step)
        
        printer.ln()
        
        # === QR CODE ===
        if data.qr_url:
            printer.set(align='center')
            printer.qr(data.qr_url, size=6)
            printer.ln()
        
        # === FOOTER ===
        printer.set(align='center')
        
        if data.footer_quote:
            printer.textln(f"«{data.footer_quote}»")
            if data.footer_quote_author:
                printer.textln(data.footer_quote_author)
        
        printer.ln()
        
        for line in data.footer_thanks:
            printer.textln(line)
        
        printer.cut()
    
    def _print_labeled_section(self, printer, label: str, text: str):
        """Print a section with a bold label followed by normal text."""
        printer.set(align='left', bold=True)
        printer.text(f"{label} ")
        printer.set(bold=False)
        
        # First line includes label, subsequent lines are full width
        words = text.split()
        first_line = []
        remaining_words = []
        first_line_width = self.char_width - len(label) - 1
        
        # Build first line
        current_length = 0
        for i, word in enumerate(words):
            test_length = current_length + len(word) + (1 if current_length > 0 else 0)
            if test_length <= first_line_width:
                first_line.append(word)
                current_length = test_length
            else:
                remaining_words = words[i:]
                break
        
        # Print first line (already on same line as label)
        printer.textln(' '.join(first_line))
        
        # Print remaining lines with full width
        if remaining_words:
            remaining_text = ' '.join(remaining_words)
            wrapped = textwrap.fill(remaining_text, width=self.char_width)
            printer.textln(wrapped)
        
        printer.ln()


# Example usage
if __name__ == "__main__":
    # Create sample data
    sample_data = ReceiptData(
        image_path="../assets/figurine.png",
        image_overlay_text="Die Antwort ist schon da.",
        figurine_number="5678",
        total_count="27 000",
        body_paragraphs=[
            "Wenn andere schon am Verzweifeln sind, blühst du erst richtig auf. In jeder Erfahrung siehst du eine Chance und schreckst nicht davor zurück, dich Neuem zu stellen und in unbekanntes Gelände vorzudringen.",
            "Das einzige, was dir schlaflose Nächte bereitet, ist die Fülle an Möglichkeiten. Wie bloss soll man da die Nadel im Heuhaufen finden?"
        ],
        mighty_question="Wie treffe ich die richtige Entscheidung?",
        informal_opportunity="Wer kennt dich am besten? Sprich mit dieser Person.",
        official_offer="viamia, berufliche Standortbestimmung für Menschen ab 40.",
        inspiration="Beginners, Tom Vanderbilt (Buch)",
        next_step="Peer-Workshop für Aufsteiger*innen",
        qr_url="https://youtu.be/dQw4w9WgXcQ",
        footer_quote="Courage, dear heart!",
        footer_quote_author="C.S. Lewis",
        footer_thanks=[
            "Vielen Dank, dass du",
            "den Status quo hinterfragst.",
            "Figurati!"
        ]
    )
    
    print("Sample ReceiptData created:")
    print(f"  Image: {sample_data.image_path}")
    print(f"  Overlay: {sample_data.image_overlay_text}")
    print(f"  QR URL: {sample_data.qr_url}")
