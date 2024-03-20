import random
import string
from aiohttp import ClientError
import os
import bittensor as bt
import orjson as json
import pandas as pd
from io import StringIO
import boto3
from typing import List, Dict, Any
import aiohttp
from environs import Env
from logging import getLogger
from hashlib import md5

logger = getLogger(__name__)

env = Env()
env.read_env()

indexing_api_key = env.str("INDEXING_API_KEY")
s3 = boto3.resource(
    "s3",
    endpoint_url=env.str("WASABI_ENDPOINT_URL"),
    aws_access_key_id=env.str("WASABI_ACCESS_KEY_ID"),
    aws_secret_access_key=env.str("WASABI_ACCESS_KEY"),
)


def scoring_bucket():
    return s3.Bucket("scoring")


async def store_scoring_metrics(metrics: dict, type: str):
    block = metrics["block"]
    filename = f"{block:09}_{md5(str(metrics).encode()).hexdigest()}.json"
    data = json.dumps(metrics)
    key = f"{type}/{filename}"
    s3.Bucket("scoring").put_object(Key=key, Body=data)
    logger.info(f"Stored scoring metrics to {key}")


async def save_indexing_row(file_name, source_type, row_count, search_keys: list):

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                    env.str("INDEXING_API_URL"),
                    headers={"Content-Type": "application/json"},
                    json={
                        "file_name": file_name,
                        "source_type": source_type,
                        "row_count": row_count,
                        "search_keys": search_keys,
                        "api_key": indexing_api_key,
                    }
            ) as response:
                return await response.json()
        except aiohttp.client_exceptions.ClientConnectorError:
            logger.error(f"Could not connect to indexing API")
            return {}


async def write_file_and_index(df_final, filename, search_keys, source_type):
    total_count = df_final.shape[0]
    if total_count == 0:
        return {"msg": "data length is 0"}

    csv_buffer = StringIO()
    df_final.to_csv(csv_buffer, index=False)

    sss = boto3.resource('s3')
    try:
        logger.info(
            f"Storing {total_count} results as {source_type}scrapingbucket/{source_type}/{filename}"
        )
        result = sss.Bucket(f'{source_type}scrapingbucket').put_object(
            Key=f"{source_type}/{filename}", Body=csv_buffer.getvalue()
        )
    except ClientError as e:
        bt.logging.error(str(e))
        return {}
    else:
        if result.get('ResponseMetadata').get('HTTPStatusCode') > 210:
            bt.logging.error(f"Error committing {source_type} file to S3. HTTP status c0de: {result.get('ResponseMetadata').get('HTTPStatusCode')}")
            return {}

    return save_indexing_row(
        filename,
        source_type,
        total_count,
        search_keys,
    )


async def twitter_store(data: List[List[Dict[str, Any]]], search_keys: List[str]) -> Dict[str, Any]:
    """
    Stores filtered Twitter data to a CSV file in S3 and indexes the file.

    Args:
        data: A list of lists, where each inner list contains dictionaries representing tweets.
        search_keys: A list of search keys used to filter the tweets.

    Returns:
        A dictionary indicating the result of the operation. If successful, returns indexing result.
        If no data is stored, returns a message indicating the data length is 0.
    """
    filename = f"twitter_{md5(str(data).encode()).hexdigest()}.csv"
    required_fields = ["id", "url", "text", "likes", "images", "timestamp"]
    fieldnames = [
        "id", "url", "text", "likes", "images", "timestamp", "username", "hashtags"
    ]

    # Flatten the list of lists and filter out None or empty responses
    flattened_data = [item for sublist in data if sublist for item in sublist]
    df = pd.DataFrame(flattened_data)

    # Filter rows based on required fields and unique IDs
    df_filtered = df.dropna(subset=required_fields).drop_duplicates(subset=['id'])

    # Keep only the columns that match the specified fieldnames
    df_final = df_filtered[fieldnames]

    return await write_file_and_index(df_final, filename, search_keys, "twitter")


async def reddit_store(data: List[List[Dict[str, Any]]], search_keys: List[str]) -> Dict[str, Any]:
    """
    Stores filtered Reddit data to a CSV file in S3 and indexes the file.

    Args:
        data: A list of lists, where each inner list contains dictionaries representing Reddit posts.
        search_keys: A list of search keys used to filter the posts.

    Returns:
        A dictionary indicating the result of the operation. If successful, returns indexing result.
        If no data is stored, returns a message indicating the data length is 0.
    """
    filename = f"reddit_{md5(str(data).encode()).hexdigest()}.csv"
    required_fields = ["id", "url", "text", "likes", "dataType", "timestamp"]
    fieldnames = [
        "id", "url", "text", "likes", "dataType", "timestamp", "username", "parent",
        "community", "title", "num_comments", "user_id"
    ]

    # Flatten the list of lists and filter out None or empty responses
    flattened_data = [item for sublist in data if sublist for item in sublist]
    df = pd.DataFrame(flattened_data)

    # Filter rows based on required fields and unique IDs
    df_filtered = df.dropna(subset=required_fields).drop_duplicates(subset=['id'])

    # Keep only the columns that match the specified fieldnames
    df_final = df_filtered[fieldnames]

    return await write_file_and_index(df_final, filename, search_keys, "reddit")
