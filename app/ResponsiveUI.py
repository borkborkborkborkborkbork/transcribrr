import logging
from PyQt6.QtWidgets import QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout, QApplication
from PyQt6.QtCore import Qt, QSize, QObject, QEvent

# Configure logging
logger = logging.getLogger('transcribrr')


class ResponsiveSizePolicy:
    """Standard responsive size policies."""
    
    @staticmethod
    def fixed():
        """Fixed size policy."""
        return QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
    
    @staticmethod
    def preferred():
        """Preferred size policy."""
        return QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
    
    @staticmethod
    def expanding():
        """Expanding size policy."""
        return QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
    
    @staticmethod
    def minimum():
        """Minimum size policy."""
        return QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)


class ResponsiveWidget(QWidget):
    """Base responsive widget."""
    
    def __init__(self, parent=None):
        """Init responsive widget."""
        super().__init__(parent)
        self.setMinimumSize(QSize(250, 100))  # Reasonable minimum size
        self.setSizePolicy(ResponsiveSizePolicy.expanding())
        
    def createLayout(self, orientation=Qt.Orientation.Vertical, margins=(8, 8, 8, 8)):
        if orientation == Qt.Orientation.Vertical:
            layout = QVBoxLayout(self)
        else:
            layout = QHBoxLayout(self)
            
        layout.setContentsMargins(*margins)
        layout.setSpacing(8)  # Consistent spacing
        
        return layout


class ResponsiveUIManager(QObject):
    """Manage responsive UI across app."""
    
    _instance = None
    
    @classmethod
    def instance(cls):
        """Return singleton ResponsiveUIManager."""
        if cls._instance is None:
            cls._instance = ResponsiveUIManager()
        return cls._instance
    
    def __init__(self):
        """Init UI manager."""
        super().__init__()
        self.scale_factor = 1.0
        self.min_font_size = 9
        self.base_font_size = 10
        self.responsive_widgets = []
        
        # Auto-detect initial scale factor based on screen DPI
        self._detect_scale_factor()
        
    def _detect_scale_factor(self):
        """Detect scale factor."""
        app = QApplication.instance()
        if app:
            # Get primary screen DPI
            screen = app.primaryScreen()
            dpi = screen.logicalDotsPerInch()
            
            # Base scale factor calculation (adjust as needed)
            self.scale_factor = max(1.0, dpi / 96.0)
            logger.info(f"Detected DPI: {dpi}, scale factor: {self.scale_factor}")
        
    def register_widget(self, widget):
        """Register widget."""
        if widget not in self.responsive_widgets:
            self.responsive_widgets.append(widget)
            
    def unregister_widget(self, widget):
        """Unregister widget."""
        if widget in self.responsive_widgets:
            self.responsive_widgets.remove(widget)
            
    def update_scale_factor(self, scale_factor):
        """Update scale factor."""
        if scale_factor <= 0:
            logger.warning(f"Invalid scale factor: {scale_factor}")
            return
            
        self.scale_factor = scale_factor
        self._apply_scaling()
        
    def _apply_scaling(self):
        """Apply scaling."""
        app = QApplication.instance()
        if not app:
            return
            
        # Update font sizes
        font = app.font()
        scaled_size = max(self.min_font_size, int(self.base_font_size * self.scale_factor))
        font.setPointSize(scaled_size)
        app.setFont(font)
        
        # Update each widget
        for widget in self.responsive_widgets:
            if widget and not widget.isDestroyed():
                # Update margins, padding, icon sizes, etc.
                if hasattr(widget, 'apply_responsive_scaling'):
                    widget.apply_responsive_scaling(self.scale_factor)
                    
        logger.info(f"Applied scaling factor: {self.scale_factor}")
        
    def update_size(self, width, height):
        """Update size scaling."""
        # Adjust scaling based on window size if needed
        # This is a simple implementation that can be enhanced
        if width < 800:
            new_scale = 0.9
        elif width > 1600:
            new_scale = 1.1
        else:
            new_scale = 1.0
            
        # Only update if scale factor changed
        if new_scale != self.scale_factor:
            self.update_scale_factor(new_scale)
            
        logger.debug(f"Window resized to {width}x{height}, scale factor: {self.scale_factor}")


class ResponsiveEventFilter(QObject):
    """
    Event filter that handles window resize events for responsive behavior.
    
    This class monitors resize events and triggers UI adjustments based on
    responsive design principles.
    """
    
    def __init__(self, parent=None):
        """
        Initialize responsive event filter.
        
        Args:
            parent: Parent object
        """
        super().__init__(parent)
        
    def eventFilter(self, watched, event):
        """
        Filter events to handle resize and other responsive UI triggers.
        
        Args:
            watched: Object being watched
            event: Event that occurred
            
        Returns:
            True if event handled, False to pass to default handler
        """
        if event.type() == QEvent.Type.Resize:
            # Handle resize events
            if hasattr(watched, 'handle_resize'):
                watched.handle_resize(event.size())
        
        # Pass event to default handler
        return super().eventFilter(watched, event)