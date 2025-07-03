"""Configuration constants for the GAIA agent project."""

from smolagents import OpenAIServerModel, InferenceClientModel

# pylint: disable=line-too-long

# Which questions to answer
QUESTIONS = [1,3,5,8,9,11,13,17,18,20]

# GAIA benchmark scoring API
DEFAULT_API_URL = 'https://agents-course-unit4-scoring.hf.space'

# Additional instructions for agent. See here: https://huggingface.co/spaces/gaia-benchmark/leaderboard
INSTRUCTIONS = """
You are a general AI assistant. I will ask you a question. Your final answer should be a number OR as few words as possible OR a comma separated list of numbers and/or strings. If you are asked for a number, don't use comma to write your number neither use units such as $ or percent sign unless specified otherwise. If you are asked for a string, don't use articles, neither abbreviations (e.g. for cities), and write the digits in plain text unless specified otherwise. If you are asked for a comma separated list, apply the above rules depending of whether the element to be put in the list is a number or a string. Submit the final answer via the final_answer tool.
"""

# Agent model definitions
MANAGER_MODEL = InferenceClientModel(
    "deepseek-ai/DeepSeek-V3",
    provider="together",
    max_tokens=64000
)

WORKER_MODEL = InferenceClientModel(
    "deepseek-ai/DeepSeek-V3",
    provider="together",
    max_tokens=64000
)

CHECK_MODEL = InferenceClientModel(
    "deepseek-ai/DeepSeek-V3",
    provider="together",
    max_tokens=64000
)

MODEL = OpenAIServerModel(
    model_id="gpt-4.1",
    max_tokens=8000
)

TOKEN_LIMITER = 5000
STEP_WAIT = 60
