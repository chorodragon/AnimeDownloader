#! /usr/bin/env python
import sqlite3
import feedparser
import subprocess
import os

def parseRss():
    feed = "https://horriblesubs.info/rss.php?res=1080"
    parsed = feedparser.parse(feed)
    return parsed


def getAnimes():
    f = open("animeList.txt", "r")
    entries = f.read().splitlines()
    result = []
    for entry in entries:
        result.append(entry)
    return result


def addEntry(entry):
    conn = sqlite3.connect('anime.db')
    query = conn.cursor()
    query.execute('select * from downloaded where magnet = "' + entry[1] + '"')
    if len(query.fetchall()) != 0:
        conn.close()
        return
    downloadDir = os.environ['HOME'] + "/Videos/" + entry[0]
    print(downloadDir)
    addMagnet = subprocess.Popen(['transmission-remote', '-w', downloadDir, '-a', entry[1]],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
    stdout,stderr = addMagnet.communicate()
    if stderr == None:
        query.execute('insert into downloaded values("' + entry[1] + '")')
        sendNotification = subprocess.Popen(['notify-send', entry[0], 'Nuevo episodio agregado'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
        stdout,stderr = sendNotification.communicate()
        conn.commit()
        conn.close()
    else:
        print("An error ocurred")
    

def parseName(name):
    result = ""
    result = name.split(']')[1]
    result = result.rsplit('-', 1)[0].strip()
    return result


def parseEntries(feed, animes):
    result = []
    for entry in feed.entries:
        name = parseName(entry.title)
        if name in animes:
            info = []
            info.append(name)
            info.append(entry.link)
            result.append(info)
    return result
        

def main():
    feed = parseRss()
    animes = getAnimes()
    entries = parseEntries(feed, animes)
    for entry in entries:
        addEntry(entry)

        
if __name__ == "__main__":
    main()
