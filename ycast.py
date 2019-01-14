import requests
import xml.etree.ElementTree as ET
import logging

from channel import Channel
from item import Item
from category import Category
from enclosure import Enclosure
from guid import GUID
from source import Source
from cloud import Cloud
from image import Image
from textinput import TextInput

class YCast:
    def __init__(self):
        # RT https://roosterteeth.com/show/rt-podcast/feed/mp3
        r = requests.get("http://leoville.tv/podcasts/sn.xml")
        logging.debug(r.text)
        root = ET.fromstring(r.text)
        channel = Channel()
        channelElement = root.find("channel")
        channel.title = channelElement.find("title").text
        channel.link = channelElement.find("link").text
        channel.description = channelElement.find("description").text

        channel.language = channelElement.find("language").text if channelElement.find("langange") else ""
        channel.copyright = channelElement.find("copyright").text if channelElement.find("copyright") else ""
        channel.managingEditor = channelElement.find("managingEditor").text if channelElement.find("managingEditor") else ""
        channel.webMaster = channelElement.find("webMaster").text if channelElement.find("webMaster") else ""
        channel.pubDate = channelElement.find("pubDate").text if channelElement.find("pubDate") else ""
        channel.lastBuildDate = channelElement.find("lastBuildDate").text if channelElement.find("lastBuildDate") else ""
        
        for category in channelElement.findall("category"):
                cat = Category()
                cat.value = category.text
                # TODO: Deal with domains
                cat.domain = category.attrib["domain"] if category.attrib else ""
                channel.category.append(cat)
        
        channel.generator = channelElement.find("generator").text if channelElement.find("generator") else ""
        channel.docs = channelElement.find("docs").text if channelElement.find("docs") else ""
        
        if channelElement.find("cloud"):
            channel.cloud = Cloud()
            for key, value in channelElement.find("cloud").items():
                    setattr(channel.cloud, key, value)

        channel.ttl = int(channelElement.find("ttl").text) if channelElement.find("ttl") else 60
        
        channel.image = Image()
        imageElement = channelElement.find("image")
        channel.image.url = imageElement.find("url").text if imageElement.find("url") else ""
        channel.image.title = imageElement.find("title").text if imageElement.find("title") else ""
        channel.image.link = imageElement.find("link").text if imageElement.find("link") else ""
        channel.image.description = imageElement.find("description").text if imageElement.find("description") else ""
        channel.image.width = int(imageElement.find("width").text) if imageElement.find("width") else 88
        channel.image.height = int(imageElement.find("height").text) if imageElement.find("height") else 31

        textInputElement = channelElement.find("textinput")
        if textInputElement:
            channel.textInput = TextInput()
            channel.textInput.title = textInputElement.find("title").text if textInputElement.find("title") else ""
            channel.textInput.description = textInputElement.find("description").text if textInputElement.find("description") else ""
            channel.textInput.name = textInputElement.find("name").text if textInputElement.find("name") else ""
            channel.textInput.link = textInputElement.find("link").text if textInputElement.find("link") else ""

        channel.skipHours = channelElement.find("skipHours").text if channelElement.find("skipHours") else ""
        channel.skipDays = channelElement.find("skipDays").text if channelElement.find("skipDays") else ""

        for itemElement in channelElement.findall("item"):
            item = Item()
            item.title = itemElement.find("title").text
            item.link = itemElement.find("link").text
            item.description = itemElement.find("description").text
            item.author = itemElement.find("author").text if itemElement.find("author") else ""
            
            for category in itemElement.findall("category"):
                cat = Category()
                cat.value = category.text
                # TODO: Deal with domains
                cat.domain = category.attrib["domain"] if category.attrib else ""
                item.category.append(cat)
            
            item.comments = itemElement.find("comments").text if itemElement.find("comments") else ""
            
            if itemElement.find("enclosure").keys():
                item.enclosure = Enclosure()
                for key, value in itemElement.find("enclosure").items():
                    setattr(item.enclosure, key, value)
            print(item.enclosure)

            item.guid = GUID()
            item.guid.value = itemElement.find("guid").text if itemElement.find("guid") else ""
            item.guid.isPermaLink = bool(itemElement.find("guid").attrib["isPermaLink"]) if itemElement.find("guid").keys() else True

            item.pubDate = itemElement.find("pubDate").text if itemElement.find("pubDate") else ""
            
            item.source = Source()
            item.source.value = itemElement.find("source").text if itemElement.find("source") else ""
            item.source.url = itemElement.find("source").attrib["url"] if itemElement.find("source") else ""

            channel.items.append(item)
        
        for item in channel.items:
            print(item.title + ": " + item.enclosure.url)
            # p = requests.get(item.enclosure)
        print(f"channel: {channel.language}")

    def start(self):
        pass
