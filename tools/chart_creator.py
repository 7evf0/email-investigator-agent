import requests
import random
import matplotlib.pyplot as plt

from smolagents import tool

@tool
def barchart_generator(key_value_dict: dict, x_label: str, y_label: str, title: str) -> object:
    """
    Generates a json object for bar chart based on data analysis query context. Json object has the format of: {key_value_dict: dict, x_label: str, y_label: str, title: str}

    Args:
        key_value_dict: Total keys and values of the chart will be fetched from here. Keys correspond to x horizon and values correspond to y horizon.
        x_label: Label of the x horizon on the bar chart.
        y_label: Label of the y horizon on the bar chart.
        title: Title of the bar chart.

    Returns:
        object: Final Json object has the format of: {key_value_dict: dict, x_label: str, y_label: str, title: str}
    """

    return {
        "key_value_dict": key_value_dict,
        "x_label": x_label,
        "y_label": y_label,
        "title": title
    }