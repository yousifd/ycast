import requests
import pyaudio
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

        channel.language = channelElement.find("language").text if channelElement.find("language") is not None else ""
        channel.copyright = channelElement.find("copyright").text if channelElement.find("copyright") is not None else ""
        channel.managingEditor = channelElement.find("managingEditor").text if channelElement.find("managingEditor") is not None else ""
        channel.webMaster = channelElement.find("webMaster").text if channelElement.find("webMaster") is not None else ""
        channel.pubDate = channelElement.find("pubDate").text if channelElement.find("pubDate") is not None else ""
        channel.lastBuildDate = channelElement.find("lastBuildDate").text if channelElement.find("lastBuildDate") is not None else ""
        
        for category in channelElement.findall("category"):
                cat = Category()
                cat.value = category.text
                # TODO: Deal with domains
                cat.domain = category.attrib["domain"] if category.attrib else ""
                channel.category.append(cat)
        
        channel.generator = channelElement.find("generator").text if channelElement.find("generator") is not None else ""
        channel.docs = channelElement.find("docs").text if channelElement.find("docs") is not None else ""
        
        if channelElement.find("cloud") is not None:
            channel.cloud = Cloud()
            for key, value in channelElement.find("cloud").items():
                    setattr(channel.cloud, key, value)

        channel.ttl = int(channelElement.find("ttl").text) if channelElement.find("ttl") is not None else 60
        
        channel.image = Image()
        imageElement = channelElement.find("image")
        channel.image.url = imageElement.find("url").text if imageElement.find("url") is not None else ""
        channel.image.title = imageElement.find("title").text if imageElement.find("title") is not None else ""
        channel.image.link = imageElement.find("link").text if imageElement.find("link") is not None else ""
        channel.image.description = imageElement.find("description").text if imageElement.find("description") is not None else ""
        channel.image.width = int(imageElement.find("width").text) if imageElement.find("width") is not None else 88
        channel.image.height = int(imageElement.find("height").text) if imageElement.find("height") is not None else 31

        textInputElement = channelElement.find("textinput")
        if textInputElement:
            channel.textInput = TextInput()
            channel.textInput.title = textInputElement.find("title").text if textInputElement.find("title") is not None else ""
            channel.textInput.description = textInputElement.find("description").text if textInputElement.find("description") is not None else ""
            channel.textInput.name = textInputElement.find("name").text if textInputElement.find("name") is not None else ""
            channel.textInput.link = textInputElement.find("link").text if textInputElement.find("link") is not None else ""

        channel.skipHours = channelElement.find("skipHours").text if channelElement.find("skipHours") is not None else ""
        channel.skipDays = channelElement.find("skipDays").text if channelElement.find("skipDays") is not None else ""

        for itemElement in channelElement.findall("item"):
            item = Item()
            item.title = itemElement.find("title").text
            item.link = itemElement.find("link").text
            item.description = itemElement.find("description").text
            item.author = itemElement.find("author").text if itemElement.find("author") is not None else ""
            
            for category in itemElement.findall("category"):
                cat = Category()
                cat.value = category.text
                # TODO: Deal with domains
                cat.domain = category.attrib["domain"] if category.attrib else ""
                item.category.append(cat)
            
            item.comments = itemElement.find("comments").text if itemElement.find("comments") is not None else ""
            
            if itemElement.find("enclosure") is not None:
                item.enclosure = Enclosure()
                for key, value in itemElement.find("enclosure").items():
                    setattr(item.enclosure, key, value)

            item.guid = GUID()
            item.guid.value = itemElement.find("guid").text if itemElement.find("guid") is not None else ""
            item.guid.isPermaLink = bool(itemElement.find("guid").attrib["isPermaLink"]) if itemElement.find("guid").keys() is not None else True

            item.pubDate = itemElement.find("pubDate").text if itemElement.find("pubDate") is not None else ""
            
            item.source = Source()
            item.source.value = itemElement.find("source").text if itemElement.find("source") is not None else ""
            item.source.url = itemElement.find("source").attrib["url"] if itemElement.find("source") is not None else ""

            channel.items.append(item)

        # TODO: Play Audio
        CHUNK = 1024
        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(2),
                        channels=2, rate=44100, output=True)
        podcast = requests.get(channel.items[0].enclosure, stream=True)

        for chunk in podcast.iter_content(chunk_size=CHUNK):
            stream.write(chunk)
        
        stream.stop_stream()
        stream.close()
        p.terminate()

    def start(self):
        pass
