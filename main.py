from requests_html import HTMLSession, HTML
from sys import argv
from argparse import ArgumentParser
import re

class ProxyManager:
    def __init__(self):
        self.session = HTMLSession()
        self.getResults = WebScraper.getResults
        self.selectors = {
                            "IPs" : {
                                "cssSelector" : "#proxylisttable tbody tr td:nth-child(1)",
                                "getFromAttribute" : "innerText"
                            },
                            "ports" : {
                                "cssSelector" : "#proxylisttable tbody tr td:nth-child(2)",
                                "getFromAttribute" : "innerText"
                            },
                            "countries" : {
                                "cssSelector" : "#proxylisttable tbody tr td:nth-child(3)",
                                "getFromAttribute" : "innerText"
                            },
                            "https" : {
                                "cssSelector" : "#proxylisttable tbody tr td.hx",
                                "getFromAttribute" : "innerText"
                            }
                        }
        self.getAll()
    def getAll(self) -> list:
            url = "https://free-proxy-list.net/"
            html = self.session.get(url).html.html
            IPs = self.getResults(html, self.selectors["IPs"])
            ports = self.getResults(html, self.selectors["ports"])
            countries = self.getResults(html, self.selectors["countries"])
            protocolType = self.getResults(html, self.selectors["https"])
            protocols = list()
            for server in protocolType:
                if server == "yes":
                    protocols.append("https")
                else:
                    protocols.append("http")

            proxies = list()
            for i in range(min(len(IPs), len(ports), len(countries))):
                proxies.append({
                    "country"   : countries[i],
                    "ip"        : IPs[i],
                    "port"      : ports[i],
                    "protocol"  : protocols[i]
                })
            self.proxies = proxies
            return self.turnIntoList(proxies)
    def turnIntoList(self, proxies : list) -> list:
        return [{proxy["protocol"] : proxy["ip"] + ":" + proxy["port"]} for proxy in proxies]
    def getByCountry(self, countryCode : list = ["DE", "GB", "FR", "PL", "AT", "IT", "CH", "CZ", "HU", "GR", "SE"], raw=False) -> list:
        matches = [proxy for proxy in self.proxies if proxy["country"] in countryCode]
        return self.turnIntoList(matches) if not raw else matches
    def getByProtocol(self, protType : str = "https", filterWithCountry=True) -> list:
        toFilter = self.getByCountry(raw=True) if filterWithCountry else self.proxies
        matches = [proxy for proxy in toFilter if proxy["protocol"] == protType]
        return self.turnIntoList(matches)

class WebScraper:
    def __init__(self, useProxies : bool = True, **kwargs):
        '''
            This class is meant for scraping webpages.
            Currently it has 2 functions:
                ``getPage``:
                    INPUT:  
                        ->  url (str)   => the needed webpage URL
                        ->  **kwargs    => everything that the "requests.get"-function takes as arguments
                    OUTPUT:
                        ->  (HTML) the HTML-Document of that url as an instance of a HTML-Class
                
                ``getResults``:
                    PARTICULARITIES:
                        -> staticmethod
                    INPUT:
                        ->  html (str/HTML)     => the HTML of an webpage as a string or as an isntance of a HTML-Class
                        ->  selector (dict)     => the selectors to select certain elements inside the Document
                        ->  callback (function) => an callback function, which gets assigned on every element which gets found with the selectors
                    OUTPUT:
                        ->  list of string objects or a single string
        '''

        self.kwargs = kwargs
        self.session = HTMLSession()
        self.proxies = ProxyManager().getByProtocol(kwargs.get("protocolType", "https"), kwargs.get("filterWithCountry", True)) if useProxies else None
    def getPage(self, url : str, **kwargs) -> HTML:
        '''
            ``returns the webpage of the url as an instance of a HTML object``
        '''
        response = self.session.get(url, proxies=self.proxies, **kwargs)
        if kwargs.get("render", False):
            response.html.render()
        return response
    @staticmethod
    def getResults(html : str, selector : dict, callback=None, **kwargs) -> list:
        '''
            ``returns a list, which contains the result of the search``
            :param html:        is the HTML code as a string
            :param selector:    are the css selectors as a string with the structure follows:\n
            {
                "cssSelector"       : "div.className1 span.text",   # the selector
                "alt_cssSelector"   : "h1[name='title']",           # the alternate css selector, if the first returns no result
                "getFromAttribute"  : "innerText",                  # can be "innerText" or the attribute name of the element
                "first"             : False                         # returns the first object in list if True
            }\n
            :param callback:    if set, function will apply to every element
        '''
        html = HTML(html=html) if type(html) == type(str()) else html.html

        # search for the first cssSelector
        # "tr[role='row'].odd"
        results = html.find(selector["cssSelector"])
        # check if something could be found, if not, search again with the "alt_cssSelector"
        if results == None:
            try:
                results = html.find(selector["alt_cssSelector"])
            except KeyError as e:
                raise KeyError(f"Fehler beim finden eines Elements mit '{selector['cssSelector']}'. Kein 'alt_cssSelector' (alternativen Selector) angegeben.")

        # gets the inner Text of the selected elements
        if selector["getFromAttribute"] == "innerText":
            results = [x.text for x in results]
        # if defined else, it looks for an attribute of the HTML element
        else:
            # define a function to apply it to every element of the result list
            def f(result):
                try:
                    return result.attrs[selector["getFromAttribute"]]
                except KeyError as e:
                    raise KeyError(f"Das Element {result} hat kein {selector['getFromAttribute']}-Parameter")
            results = list(map(f, results))

        # check if a callback function is set and apply it to the list, if it is
        if callback:
            results = list(map(callback, results))

        # check for the arument 'first', if it is true, the function only returns the first element of the list
        if selector.get("first", False):
            try:
                result = results[0]
            except IndexError:
                result = results
        else:
            result = results
        return result

    def getResultsFromSelectors(self, html : str, selectors : dict) -> dict:
        results = dict()
        for key in selectors.keys():
            results[key] = self.getResults(html, selectors[key])
        if max(*[len(values) for values in results.values()]) == min(*[len(values) for values in results.values()]):
            results = self.dict2List(results)
        else:
            print("didnt work")
        return results
    @staticmethod
    def dict2List(dictionary : dict) -> list:
        results = list()
        for key, value in dictionary.items():
            for i in range(len(value)):
                if key == list(dictionary.keys())[0]:
                    results.append({
                        key : value[i]
                    })
                else:
                    results[i] = {
                        **results[i],
                        key : value[i]
                    }
        return results
    def getAllPages(self, urls : list) -> list:
        for url in urls:
            pagesContent = self.getPage(url).html

if __name__ == "__main__":
    parser = ArgumentParser(prog="Webscraper", description="This is a simple script to scrape webpages. Uses proxies by default.")
    parser.add_argument("url", help="The URL of the webpage to scrape", type=str)
    parser.add_argument("cssSelector", help="The CSS selector to select the elements", type=str)
    parser.add_argument("--attr", required=False, help="'innerText' or the attribute name (default: innerText)", type=str, default="innerText")
    parser.add_argument("--first", required=False, help="whether the first element should be returned or all (default: True)", const=True, nargs="?", default=False)
    parser.add_argument("--noProxy", required=False, help="use if you want to use no proxy (default: True)", const=False, nargs="?", default=True)
    parser.add_argument("--regex", required=False, help="Regex pattern which will get used on every result", type=str, default=None)
    args = parser.parse_args(argv[1:])
    scraper = WebScraper(useProxies=True)
    html = scraper.getPage(args.url)
    result = scraper.getResults(html, {
        'cssSelector' : args.cssSelector,
        'getFromAttribute' : args.attr,
        "first": args.first
    })
    if args.regex:
        if args.first:
            result = re.search(args.regex, result).group(0)
            print(result)
        else:
            newResult = []
            for line in result:
                try:
                    newResult.append(re.search(args.regex, line).group(0))
                except AttributeError:
                    continue
            print(newResult)
    