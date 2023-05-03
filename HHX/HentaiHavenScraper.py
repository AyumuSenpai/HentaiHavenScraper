from typing import List, Dict, Any

import requests
from bs4 import BeautifulSoup
import re


class FailedToReachHentaiHaven(Exception):
    pass

class FailedToFindSummary(Exception):
    pass

class HHX:
    def __init__(self):
        self.baseURL = "https://hentaihaven.xxx/"

    def Search(self, name: str = "") -> list[dict[str, str]]:
        titles = []
        studios = []
        covers = []
        releaseDates = []
        episodes = []

        searchURL = self.baseURL + "?s=" + name.replace(" ", "+")
        try:
            data = requests.get(searchURL).content
            parsedData = BeautifulSoup(data, "html.parser")
            results = str(parsedData.find_all("a", class_=""))
        except FailedToReachHentaiHaven:
            results = ""

        # Title Parsing
        titleParsing = True
        titleIndex = 0
        while titleParsing:
            titleIndex = (results.find('title="', titleIndex) + 7)
            title = ""
            while results[titleIndex] != '"':
                title = title + results[titleIndex]
                titleIndex = titleIndex + 1
            if title in titles:
                titleParsing = False
                titles.pop()  # Garbage data at the end and too lazy to fix so just gonna pop it away
            else:
                titles.append(title)

        # Studio Parsing
        studioIndex = 0
        for _ in titles:
            studioIndex = results.find("/studio/", studioIndex)
            studio = ""
            # Get to start of Studio Name
            while results[studioIndex] != ">":
                studioIndex = studioIndex + 1
            studioIndex = studioIndex + 1
            # Input Studio Name until start of new tag is found
            while results[studioIndex] != "<":
                studio = studio + results[studioIndex]
                studioIndex = studioIndex + 1
            studios.append(studio)

        # Cover URL Parsing
        coverIndex = 0
        for _ in titles:
            coverIndex = (results.find('src="', coverIndex) + 5)
            cover = ""
            while results[coverIndex] != '"':
                cover = cover + results[coverIndex]
                coverIndex = coverIndex + 1
            covers.append(cover)

        # Release Date Parsing
        releaseIndex = 0
        for _ in titles:
            releaseIndex = results.find("/release/", releaseIndex)
            year = ""
            # Get start of release date
            while results[releaseIndex] != ">":
                releaseIndex = releaseIndex + 1
            releaseIndex = releaseIndex + 1

            # Input release date
            while results[releaseIndex] != "<":
                year = year + results[releaseIndex]
                releaseIndex = releaseIndex + 1
            releaseDates.append(year)

        # Number of Episodes Parsing
        episodeIndex = 0
        for _ in titles:
            episodeIndex = results.find("/episode-", episodeIndex)

            # Get start of episodes
            while results[episodeIndex] != ">":
                episodeIndex = episodeIndex + 1
            episodeIndex = episodeIndex + 1

            # Input number of episodes
            while results[episodeIndex] != "<":
                episodeIndex = episodeIndex + 1
            episodes.append(results[episodeIndex - 1])

        resultDict = {
            "title": "",
            "cover": "",
            "studio": "",
            "release": "",
            "episodes": ""
        }
        parsedResult = []
        for i in range(0, len(titles)):
            parsedResult.append(resultDict.copy())
            parsedResult[i]["title"] = titles[i]
            parsedResult[i]["cover"] = covers[i]
            parsedResult[i]["studio"] = studios[i]
            parsedResult[i]["release"] = releaseDates[i]
            parsedResult[i]["episodes"] = episodes[i]

        return parsedResult

    def Info(self, name: str) -> dict[str, str | list[str] | Any]:
        filteredName = name.lower().replace(" ", "-")
        searchURL = self.baseURL + "watch/" + filteredName

        try:
            data = requests.get(searchURL).content
            parsedData = BeautifulSoup(data, "html.parser")
        except FailedToReachHentaiHaven:
            parsedData = ""

        #Grabs Title
        title = parsedData.find("div", class_="post-title")
        tagsToRemove = re.compile('<.*?>')
        title = tagsToRemove.sub("", str(title)).strip()
        # Grabs Cover URL
        tempCover = str(parsedData.find("div", class_="position-relative"))
        coverIndex = (tempCover.find('src="') + 5)
        cover = ""
        while tempCover[coverIndex] != ' ' and '"':
            cover = cover + tempCover[coverIndex]
            coverIndex = coverIndex + 1
        cover = cover[:-1]
        #Grabs Summary
        try:
            summary = parsedData.find("div", class_="description-summary").find_all("p")
            summary = tagsToRemove.sub("", str(summary)).replace("[", "").replace("]", "").strip()
        except FailedToFindSummary:
            summary = ""
        #Grabs Studio
        studio = parsedData.find("div", class_="author-content")
        studio = tagsToRemove.sub("", str(studio)).strip()
        #Grabs Release
        release = parsedData.find(
            "div", class_="post-status").find("div", class_="post-content_item").find("div", class_="summary-content")
        release = tagsToRemove.sub("", str(release)).strip()
        # Grabs Genres in a list of strings
        genres = []
        tempGenres = parsedData.find("div", class_="genres-content").find_all("a")
        for genre in tempGenres:
            temp = tagsToRemove.sub("", str(genre)).strip()
            genres.append(temp)
        # Grabs latest episode number
        episodes = parsedData.find("li", "wp-manga-chapter").find("a")
        episodes = tagsToRemove.sub("", str(episodes)).replace("Episode", "").strip()

        result = {
            "title": title,
            "cover": cover,
            "studio": studio,
            "release": release,
            "episodes": episodes,
            "genres": genres
        }
        return result
