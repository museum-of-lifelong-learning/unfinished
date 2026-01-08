"""
FilePrinter - Mock printer that outputs to Markdown files.
Implements PrinterInterface to be compatible with receipt generation code.
"""
import os
import base64
from datetime import datetime
from io import BytesIO
from typing import Optional
from PIL import Image
from printer_interface import PrinterInterface


class FilePrinter(PrinterInterface):
    """
    Mock printer that writes receipt output to a Markdown file.
    
    Images are embedded as base64 data URIs for inline display.
    Formatting is represented using Markdown syntax (bold, alignment approximations).
    """
    
    def __init__(self, output_dir: str = "test_outputs", figurine_id: Optional[int] = None):
        """
        Initialize the file printer.
        
        Args:
            output_dir: Directory where markdown files will be saved
            figurine_id: Optional figurine ID for the filename
        """
        self.output_dir = output_dir
        self.figurine_id = figurine_id
        self.content = []
        self.current_align = 'left'
        self.current_bold = False
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def image(self, img: Image.Image) -> None:
        """Embed image as base64 data URI."""
        # Convert PIL Image to base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Add as markdown image with base64 data URI
        self.content.append(f"\n![Receipt Image](data:image/png;base64,{img_str})\n")
    
    def text(self, text: str) -> None:
        """Add text without newline."""
        formatted_text = self._format_text(text)
        self.content.append(formatted_text)
    
    def textln(self, text: str) -> None:
        """Add text with newline."""
        formatted_text = self._format_text(text)
        
        # Apply alignment using HTML for better markdown rendering
        if self.current_align == 'center':
            self.content.append(f'<div align="center">{formatted_text}</div>\n\n')
        elif self.current_align == 'right':
            self.content.append(f'<div align="right">{formatted_text}</div>\n\n')
        else:
            self.content.append(f'{formatted_text}\n\n')
    
    def ln(self, count: int = 1) -> None:
        """Add newline(s)."""
        self.content.append('\n' * count)
    
    def set(self, **kwargs) -> None:
        """Set formatting options (align, bold)."""
        if 'align' in kwargs:
            self.current_align = kwargs['align']
        if 'bold' in kwargs:
            self.current_bold = kwargs['bold']
    
    def qr(self, data: str, **kwargs) -> None:
        """Represent QR code as a link and text."""
        size = kwargs.get('size', 6)
        
        # Add QR code as both a link and visual placeholder
        qr_content = f'<div align="center">\n\n'
        qr_content += f'**[QR Code: {data}]({data})**\n\n'
        qr_content += f'`QR Code (size {size}): {data}`\n\n'
        qr_content += f'</div>\n\n'
        
        self.content.append(qr_content)
    
    def cut(self) -> None:
        """Finalize and save the markdown file."""
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if self.figurine_id is not None:
            filename = f"receipt_{self.figurine_id:04d}_{timestamp}.md"
        else:
            filename = f"receipt_{timestamp}.md"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Add separator at the end
        self.content.append('\n---\n\n')
        self.content.append('*Receipt printed to file*\n')
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(''.join(self.content))
        
        print(f"Receipt saved to: {filepath}")
        
        # Clear content for potential reuse
        self.content = []
        self.current_align = 'left'
        self.current_bold = False
    
    def _format_text(self, text: str) -> str:
        """Apply current formatting to text."""
        if self.current_bold:
            return f'**{text}**'
        return text
