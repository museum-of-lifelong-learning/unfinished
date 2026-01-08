import logging

logger = logging.getLogger(__name__)

def get_temperature(zone_path: str, name: str) -> float:
    """Read temperature from a thermal zone."""
    try:
        with open(zone_path, "r") as f:
            raw = f.read().strip()
        value = float(raw)
        temp_c = value / 1000.0 if value > 200 else value
        if -30.0 < temp_c < 120.0:
            return temp_c
        logger.debug(f"Discarding out-of-range {name} temp from {zone_path}: {temp_c}C (raw={raw})")
    except Exception as e:
        logger.debug(f"Could not read {name} temperature from {zone_path}: {e}")
    return None

def log_temperatures():
    """Log CPU and WiFi temperatures."""
    cpu_temp = get_temperature("/sys/class/thermal/thermal_zone2/temp", "CPU")
    wifi_temp = get_temperature("/sys/class/thermal/thermal_zone1/temp", "WiFi")
    
    if cpu_temp is not None:
        logger.info(f"CPU Temperature: {cpu_temp:.1f}°C")
    else:
        logger.info("CPU Temperature: unavailable")
        
    if wifi_temp is not None:
        logger.info(f"WiFi Temperature: {wifi_temp:.1f}°C")
    else:
        logger.info("WiFi Temperature: unavailable")