"""
Import and export of configuration options
"""

import os

from matplotlib.colors import is_color_like

import MetaWinLanguage
import MetaWinCharts

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "metawin.config")


def import_config() -> dict:
    """
    Attempt to import a configuration file if it exists. Return values in file,
    or defaults, as necessary

    invalid configuration options are simply ignored
    """
    config = default_config()
    try:
        with open(CONFIG_FILE, "r") as infile:
            for line in infile:
                try:
                    key, value = line.strip().split("=")
                    key, value = key.strip(), value.strip()
                    value = validate_config(key, value)
                    if value is not None:
                        config[key] = value
                except ValueError:
                    pass
    except IOError:
        pass
    return config


def default_config() -> dict:
    """
    create the default configuration
    """
    return {
        "language": "English",
        "data decimals": 2,
        "output decimals": 4,
        "filtered row color": "lightpink",
        "filtered col color": "red",
        "auto update check": True,
        "alpha": 0.05,
        "confidence interval distribution": "Normal",
        "color name space": "xkcd"
    }


def validate_config(key: str, value: str):
    """
    validate whether the imported value is valid for the specified key, including
    conversion from strings when appropriate

    if the value is invalid, return None
    if the key is not recognized, just return the value as is
    """
    if key in ("data decimals", "output decimals"):
        try:
            value = int(value)
            if (value < 0) or (value > 15):
                raise ValueError
            return value
        except ValueError:
            return None
    elif key == "language":
        if value in MetaWinLanguage.language_list():
            return value
        return None
    elif key in ("filtered row color", "filtered col color"):
        if is_color_like(value):
            return value
        return None
    elif key == "auto update check":
        if value.lower() == "true":
            return True
        return False
    elif key == "alpha":
        try:
            value = float(value)
            if (value < 0) or (value > 1):
                raise ValueError
            return value
        except ValueError:
            return None
    elif key == "confidence interval distribution":
        if value == "Students t":
            return value
        return "Normal"
    elif key == "color name space":
        if value == "X11/CSS4":
            return value
        return "xkcd"
    return value


def export_config(main_window) -> None:
    """
    export the current configuration options to the configuration file so they can be
    imported next time the program is executed
    """
    try:
        with open(CONFIG_FILE, "w") as outfile:
            outfile.write(f"language={MetaWinLanguage.current_language}\n")
            outfile.write(f"output decimals={main_window.output_decimals:d}\n")
            outfile.write(f"data decimals={main_window.data_decimals:d}\n")
            outfile.write(f"filtered row color={main_window.filtered_row_color}\n")
            outfile.write(f"filtered col color={main_window.filtered_col_color}\n")
            outfile.write(f"auto update check={main_window.auto_update_check}\n")
            outfile.write(f"alpha={main_window.alpha}\n")
            outfile.write(f"confidence interval distribution={main_window.confidence_interval_dist}\n")
            outfile.write(f"color name space={MetaWinCharts.color_name_space}\n")
    except IOError:
        pass
