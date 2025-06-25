
"""
Configuration constants for the GAIA agent project.
Contains API URLs and agent instructions used throughout the application.
"""
# pylint: disable=line-too-long

DEFAULT_API_URL = 'https://agents-course-unit4-scoring.hf.space'

INSTRUCTIONS = """
YOUR FINAL ANSWER should be a number OR as few words as possible OR a comma separated list of numbers and/or strings. If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise. If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise. If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string.
"""
