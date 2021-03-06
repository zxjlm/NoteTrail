import os

import httpx
from loguru import logger
from notion_client import Client

from notetrail.utils.decorators import log


class MyNotionClient:
    def __init__(self, client):
        # todo: httpx.ConnectError
        self.client = Client(auth=os.environ["NOTION_TOKEN"], client=client)

    def create_page(self, *args, **kwargs):
        properties = kwargs.get('properties', 'empty')
        parent = kwargs.get('parent')
        logger.debug("Creating page, properties: {}, parent: {}".format(properties, parent))
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

    def update_database_properties(self, database_id, properties):
        logger.debug("Updating database properties, database_id: {}, properties: {}".format(database_id, properties))
        return self.client.databases.update(database_id=database_id, properties=properties)

    def delete_all_children(self, block_id, children):
        logger.debug("Deleting all children, block_id: {}".format(block_id))
        if block_id and children is None:
            response = self.client.blocks.children.list(block_id=block_id)
            children = response['result']

        for child in children:
            self.client.blocks.delete(block_id=child['id'])

    @log
    def delete_block(self, block_id: str):
        return self.client.blocks.delete(block_id)

    @log
    def search(self, query):
        return self.client.search(query=query)


# client_ = httpx.Client(proxies={'http://': 'http://127.0.0.1:7890', 'https://': 'http://127.0.0.1:7890'}, timeout=30)
client_ = httpx.Client(timeout=30)
notion_client = MyNotionClient(client_)
