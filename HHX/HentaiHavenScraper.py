import requests
from bs4 import BeautifulSoup
import json


class FailedToReachHentaiHaven(Exception):
    pass


class HHX:
    def __init__(self):
        self.baseURL = "https://hentaihaven.xxx/"

    def Search(self, name: str) -> str:
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

        return json.dumps(parsedResult)
