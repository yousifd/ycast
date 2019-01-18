import xml.etree.ElementTree as ET
import os
import shutil
import logging
import threading
from datetime import datetime

import requests
from dateutil.parser import parse

from feed.channel import Channel
from feed.item import Item
from feed.category import Category
from feed.enclosure import Enclosure
from feed.guid import GUID
from feed.source import Source
from feed.cloud import Cloud
from feed.image import Image
from feed.textinput import TextInput
from exceptions import YCastException

class ManagerException(YCastException):
    pass

class ManagerAlreadyDownloaded(ManagerException):
    pass

class ManagerNotDownloaded(ManagerException):
    pass

class ManagerAlreadySubscribed(ManagerException):
    pass

class ManagerInvalidURL(ManagerException):
    pass

class Manager:
    def __init__(self):
        self.channels = {} # Pickled
        self.title_to_url = {}
        self.channel_to_items = {}
        self.threads = []

        if not os.path.exists("downloads"):
            os.makedirs("downloads")         
    
    def __getstate__(self):
        d = dict(self.__dict__)
        del d['title_to_url']
        del d['channel_to_items']
        del d['threads']
        return d
    
    def __setstate__(self, d):
        self.__dict__.update(d)
        self.title_to_url = {}
        self.channel_to_items = {}
        self.threads = []
        # Check if a downloaded file has been deleted since last time
        for url, channel in self.channels.items():
            self.title_to_url[channel.title] = url
            self.channel_to_items[channel.title] = set(channel.items)
            for item in channel.items:
                if item.downloaded and not os.path.isfile(item.filename):
                    item.downloaded = False
    
    def quit(self):
        self.wait_for_all_threads()
    
    def wait_for_all_threads(self):
        for thread in self.threads:
            if thread.is_alive():
                print(f"Waiting for: {thread.name}")
            thread.join()

    def download_item(self, item, channel):
        if item.downloaded:
            raise ManagerAlreadyDownloaded

        if not os.path.exists(f"downloads/{channel.title}"):
            try:
                os.makedirs(f"downloads/{channel.title}")
            except FileExistsError:
                pass

        t = threading.Thread(target=self.download_thread, args=(
            channel, item), name=f"Downloading {channel.title}: {item.title}")
        t.start()
        self.threads.append(t)
    
    def download_thread(self, channel, item):
        url = item.enclosure.url
        try:
            r = requests.get(url, stream=True)
        except requests.exceptions.RequestException:
            raise ManagerInvalidURL
        filename = f"downloads/{channel.title}/{item.guid}.mp3"
        item.filename = filename
        with open(filename, "wb") as file:
            for chunk in r.iter_content(chunk_size=1024):
                file.write(chunk)
        item.downloaded = True

    def delete_item(self, item, channel):
        if not item.downloaded:
            raise ManagerNotDownloaded

        t = threading.Thread(target=self.delete_thread, args=(item,), name=f"Deleting {channel.title}: {item.title}")
        t.start()
        self.threads.append(t)

    def delete_thread(self, item):
        os.remove(item.filename)
        item.downloaded = False

    def update_all(self):
        ret = list()
        for _, channel in self.channels.items():
            ret.extend(self.update(channel))
        return ret

    def update(self, channel):
        updated = False
        try:
            r = requests.get(self.title_to_url[channel.title])
        except requests.exceptions.RequestException:
            raise ManagerInvalidURL
        channel_new = self.parse_channel(r.text)
        ret = [f"{channel.title}\n"]
        for item_new in channel_new.items:
            # Assuming that all channels follow pubDate order
            # and first mismatch means no new episodes
            if item_new.title in self.channel_to_items[channel.title]:
                if not updated:
                    ret = list()
                else:
                    ret[-1] = ret[-1][:-1]
                break
            else:
                channel.items.insert(0, item_new)
                ret.append(f"{item_new.title}\n")
                updated = True
        return ret

    def unsubscribe_from_channel(self, channel):
        channel_title = channel.title
        if os.path.exists(f"downloads/{channel_title}"):
            shutil.rmtree(f"downloads/{channel_title}")
        del self.channels[self.title_to_url[channel_title]]

    def subscribe_to_channel(self, url):
        if url in self.channels:
            raise ManagerAlreadySubscribed

        t = threading.Thread(target=self.sub_to_channel_thread, args=(url,), name=f"Subscribing to {url}")
        t.start()
        self.threads.append(t)
    
    def sub_to_channel_thread(self, url):
        try:
            r = requests.get(url)
        except requests.exceptions.RequestException:
            raise ManagerInvalidURL
        logging.debug(r.text)
        channel = self.parse_channel(r.text)
        self.channels[url] = channel
        self.title_to_url[channel.title] = url
    
    def parse_channel(self, text):
        root = ET.fromstring(text)
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
        
        if channelElement.find("pubDate") is not None:
            pubDate = channelElement.find("pubDate").text
            channel.pubDate = parse_pub_date(pubDate)
        
        channel.lastBuildDate = channelElement.find(
            "lastBuildDate").text if channelElement.find("lastBuildDate") is not None else ""

        for category in channelElement.findall("category"):
            cat = Category()
            cat.value = category.text
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

        self.channel_to_items[channel.title] = set()

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

            if itemElement.find("pubDate") is not None:
                pubDate = itemElement.find("pubDate").text
                item.pubDate = parse_pub_date(pubDate)

            item.source = Source()
            item.source.value = itemElement.find(
                "source").text if itemElement.find("source") is not None else ""
            item.source.url = itemElement.find(
                "source").attrib["url"] if itemElement.find("source") is not None else ""

            channel.items.append(item)
            self.channel_to_items[channel.title].add(item.title)

        channel.items.sort(key=lambda x: x.pubDate if x.pubDate is not None else datetime.now(), reverse=True)
        return channel


def parse_pub_date(pubDate):
    return parse(pubDate, ignoretz=True)
