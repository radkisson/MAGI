"""
Test suite for RIN Sensors
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rin.sensors import WebBrowser, APIConnector, SensorManager


def test_web_browser_initialization():
    """Test WebBrowser sensor initialization"""
    browser = WebBrowser()
    assert browser is not None


def test_web_browser_perceive():
    """Test WebBrowser perceive method"""
    browser = WebBrowser()
    result = browser.perceive("https://example.com")
    
    assert result is not None
    assert "url" in result
    assert "timestamp" in result
    assert result["url"] == "https://example.com"


def test_api_connector_initialization():
    """Test APIConnector sensor initialization"""
    connector = APIConnector()
    assert connector is not None


def test_api_connector_perceive():
    """Test APIConnector perceive method"""
    connector = APIConnector()
    result = connector.perceive("https://api.example.com/data")
    
    assert result is not None
    assert "endpoint" in result
    assert "timestamp" in result


def test_sensor_manager_initialization():
    """Test SensorManager initialization"""
    manager = SensorManager()
    assert manager is not None


def test_sensor_manager_available_sensors():
    """Test getting available sensors"""
    manager = SensorManager()
    sensors = manager.get_available_sensors()
    
    assert "web_browser" in sensors
    assert "api_connector" in sensors


def test_sensor_manager_perceive():
    """Test using SensorManager to perceive"""
    manager = SensorManager()
    result = manager.perceive("web_browser", "https://example.com")
    
    assert result is not None
    assert "url" in result


def test_sensor_manager_invalid_sensor():
    """Test using invalid sensor type"""
    manager = SensorManager()
    
    with pytest.raises(ValueError):
        manager.perceive("invalid_sensor", "target")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
