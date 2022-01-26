import os

from loguru import logger
from notion_client import Client


class MyNotionClient:
    def __init__(self, client):
        self.client = Client(auth=os.environ["NOTION_TOKEN"], client=client)

    def create_page(self, *args, **kwargs):
        properties = kwargs.get('properties', 'empty')
        logger.debug("Creating page, properties: {}".format(properties))
        return self.client.pages.create(*args, **kwargs)
