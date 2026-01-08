"""
Abstract base class for printer interface.
Defines the contract that all printer implementations must follow.
"""
from abc import ABC, abstractmethod
from typing import Any
from PIL import Image


class PrinterInterface(ABC):
    """
    Abstract interface for printer implementations.
    
    This ensures that both real thermal printers (escpos) and mock printers
    (FilePrinter) implement the same methods, making them interchangeable.
    """
    
    @abstractmethod
    def image(self, img: Image.Image) -> None:
        """Print an image."""
        pass
    
    @abstractmethod
    def text(self, text: str) -> None:
        """Print text without newline."""
        pass
    
    @abstractmethod
    def textln(self, text: str) -> None:
        """Print text with newline."""
        pass
    
    @abstractmethod
    def ln(self, count: int = 1) -> None:
        """Print newline(s)."""
        pass
    
    @abstractmethod
    def set(self, **kwargs) -> None:
        """
        Set text formatting options.
        Common kwargs: align ('left', 'center', 'right'), bold (True/False)
        """
        pass
    
    @abstractmethod
    def qr(self, data: str, **kwargs) -> None:
        """
        Print QR code.
        Common kwargs: size (int)
        """
        pass
    
    @abstractmethod
    def cut(self) -> None:
        """Cut the paper (or finalize the output)."""
        pass
