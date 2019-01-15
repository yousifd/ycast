import xml.etree.ElementTree as ET
import os
import logging

import requests

from feed.channel import Channel
from feed.item import Item
from feed.category import Category
from feed.enclosure import Enclosure
from feed.guid import GUID
from feed.source import Source
from feed.cloud import Cloud
from feed.image import Image
from feed.textinput import TextInput

class Manager:
    def __init__(self):
        self.channels = {}
        self.title_to_url = {}

        if not os.path.exists("downloads"):
            os.makedirs("downloads")

    def show_channels(self):
        if not self.channels.keys():
            print("No Podcasts Yet!")
        for url, channel in self.channels.items():
            print(channel.title)
            for item in channel.items:
                # Sort Episodes by Pub Date
                print(f"\t{item.title} ({item.enclosure.url})")
    
    def download_podcast(self, url, filename):
        r = requests.get(url, stream=True)
        with open(f"downloads/{filename}", "wb") as file:
            for chunk in r.iter_content(chunk_size=1024):
                file.write(chunk)

    def subscribe_to_podcast(self, url):
        if url in self.channels:
            print(f"Channel {url} already subscribed to!")
            return
        r = requests.get(url)
        logging.debug(r.text)
        root = ET.fromstring(r.text)
        channel = Channel()
        channelElement = root.find("channel")
        channel.title = channelElement.find("title").text
        channel.link = channelElement.find("link").text
        channel.description = channelElement.find("description").text

        channel.language = channelElement.find(
            "language").text if channelElement.find("language") is not None else ""
        channel.copyright = channelElement.find(
            "copyright").text if channelElement.find("copyright") is not None else ""
        channel.managingEditor = channelElement.find(
            "managingEditor").text if channelElement.find("managingEditor") is not None else ""
        channel.webMaster = channelElement.find(
            "webMaster").text if channelElement.find("webMaster") is not None else ""
        channel.pubDate = channelElement.find(
            "pubDate").text if channelElement.find("pubDate") is not None else ""
        channel.lastBuildDate = channelElement.find(
            "lastBuildDate").text if channelElement.find("lastBuildDate") is not None else ""

        for category in channelElement.findall("category"):
                cat = Category()
                cat.value = category.text
                # TODO: Deal with domains
                cat.domain = category.attrib["domain"] if category.attrib else ""
                channel.category.append(cat)

        channel.generator = channelElement.find(
            "generator").text if channelElement.find("generator") is not None else ""
        channel.docs = channelElement.find(
            "docs").text if channelElement.find("docs") is not None else ""

        if channelElement.find("cloud") is not None:
            channel.cloud = Cloud()
            for key, value in channelElement.find("cloud").items():
                    setattr(channel.cloud, key, value)

        channel.ttl = int(channelElement.find("ttl").text) if channelElement.find(
            "ttl") is not None else 60

        imageElement = channelElement.find("image")
        if imageElement:
            channel.image = Image()
            channel.image.url = imageElement.find(
                "url").text if imageElement.find("url") is not None else ""
            channel.image.title = imageElement.find(
                "title").text if imageElement.find("title") is not None else ""
            channel.image.link = imageElement.find(
                "link").text if imageElement.find("link") is not None else ""
            channel.image.description = imageElement.find(
                "description").text if imageElement.find("description") is not None else ""
            channel.image.width = int(imageElement.find(
                "width").text) if imageElement.find("width") is not None else 88
            channel.image.height = int(imageElement.find(
                "height").text) if imageElement.find("height") is not None else 31

        textInputElement = channelElement.find("textinput")
        if textInputElement:
            channel.textInput = TextInput()
            channel.textInput.title = textInputElement.find(
                "title").text if textInputElement.find("title") is not None else ""
            channel.textInput.description = textInputElement.find(
                "description").text if textInputElement.find("description") is not None else ""
            channel.textInput.name = textInputElement.find(
                "name").text if textInputElement.find("name") is not None else ""
            channel.textInput.link = textInputElement.find(
                "link").text if textInputElement.find("link") is not None else ""

        channel.skipHours = channelElement.find(
            "skipHours").text if channelElement.find("skipHours") is not None else ""
        channel.skipDays = channelElement.find(
            "skipDays").text if channelElement.find("skipDays") is not None else ""

        for itemElement in channelElement.findall("item"):
            item = Item()
            item.title = itemElement.find("title").text
            item.link = itemElement.find("link").text
            item.description = itemElement.find("description").text
            item.author = itemElement.find("author").text if itemElement.find(
                "author") is not None else ""

            for category in itemElement.findall("category"):
                cat = Category()
                cat.value = category.text
                # TODO: Deal with domains
                cat.domain = category.attrib["domain"] if category.attrib else ""
                item.category.append(cat)

            item.comments = itemElement.find("comments").text if itemElement.find(
                "comments") is not None else ""

            if itemElement.find("enclosure") is not None:
                item.enclosure = Enclosure()
                for key, value in itemElement.find("enclosure").items():
                    setattr(item.enclosure, key, value)

            item.guid = GUID()
            item.guid.value = itemElement.find(
                "guid").text if itemElement.find("guid") is not None else ""
            item.guid.isPermaLink = bool(itemElement.find(
                "guid").attrib["isPermaLink"]) if itemElement.find("guid").keys() is not None else True

            item.pubDate = itemElement.find("pubDate").text if itemElement.find(
                "pubDate") is not None else ""

            item.source = Source()
            item.source.value = itemElement.find(
                "source").text if itemElement.find("source") is not None else ""
            item.source.url = itemElement.find(
                "source").attrib["url"] if itemElement.find("source") is not None else ""

            channel.items.append(item)
        self.channels[url] = channel
        self.title_to_url[channel.title] = url
