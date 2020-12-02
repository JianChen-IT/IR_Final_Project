import pandas as pd

"""
def set_full_text(data: pd.DataFrame) -> None:
    if data["truncated"] is True:
        data["text"] = data["extended_tweet"]["full_text"]

"""


def unique_tweets(data: pd.DataFrame) -> pd.DataFrame:
    return data.drop_duplicates(subset=["id"])


def binary_search(arr, x):
    low = 0
    high = len(arr) - 1
    mid = 0

    while low <= high:

        mid = (high + low) // 2

        # Check if x is present at mid
        if arr[mid] < x:
            low = mid + 1

        # If x is greater, ignore left half
        elif arr[mid] > x:
            high = mid - 1

        # If x is smaller, ignore right half
        else:
            return False

    # If we reach here, then the element was not present
    return True
