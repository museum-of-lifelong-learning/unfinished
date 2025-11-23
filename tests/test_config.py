"""
Tests for configuration loading
"""
import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestConfig:
    """Test configuration loading and environment switching"""
    
    def test_dev_config_loads(self):
        """Test that dev config loads with correct settings"""
        os.environ['FIGURINE_ENV'] = 'dev'
        
        # Force reload of config module
        if 'config' in sys.modules:
            del sys.modules['config']
        
        from config import config
        
        assert config.DEBUG is True
        assert config.CAMERA_WIDTH == 1280
        assert config.SHOW_DEBUG_WINDOW is True
    
    def test_pi_config_loads(self):
        """Test that pi config loads with correct settings"""
        os.environ['FIGURINE_ENV'] = 'pi'
        
        # Force reload
        if 'config' in sys.modules:
            del sys.modules['config']
        
        from config import config
        
        assert config.DEBUG is False
        assert config.CAMERA_WIDTH == 640
        assert config.SHOW_DEBUG_WINDOW is False
    
    def test_config_has_required_attributes(self):
        """Test that config has all required attributes"""
        from config import config
        
        required_attrs = [
            'CAMERA_WIDTH', 'CAMERA_HEIGHT', 'CAMERA_FPS',
            'MIN_CONTOUR_AREA', 'MAX_SHAPES',
            'CONFIDENCE_THRESHOLD', 'INFERENCE_THREADS'
        ]
        
        for attr in required_attrs:
            assert hasattr(config, attr), f"Config missing attribute: {attr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
