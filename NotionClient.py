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

    def update_page(self, *args, **kwargs):
        properties = kwargs.get('properties', 'empty')
        logger.debug("Creating page, properties: {}".format(properties))
        return self.client.pages.create(*args, **kwargs)

    def update_block(self, block_id, child):
        # properties = kwargs.get('properties', 'empty')
        # logger.debug("Creating page, properties: {}".format(properties))
        return self.client.blocks.update(block_id=block_id, child=child)

    def append_block_children(self, block_id, children):
        return self.client.blocks.children.append(block_id=block_id, children=children)

    def retrieve_block_children(self, block_id):
        logger.debug("Retrieving block children, block_id: {}".format(block_id))
        return self.client.blocks.children.list(block_id=block_id)
