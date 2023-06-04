import time
import requests
import colorama


class Scrap:
    def __init__(self, base_url):
        """ Needs the base url of the website to scrap """
        self.base_url = base_url
        self.html = []
        self.headers = {"User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}


    def fetch_url(self, url):
        """ Fetch the url and add the result to the html list """
        connected = False
        error_message_displayed = False

        while not connected:
            try:
                response = requests.get(self.base_url + url, headers=self.headers, cookies=None, timeout=None)
                connected = True
                self.html.append(response.content)

            except requests.exceptions.RequestException:
                if not error_message_displayed:
                    print(colorama.Fore.RED, "ERREUR DE CONNEXION : Veuillez vérifier votre connexion internet",
                          colorama.Fore.RESET)
                    error_message_displayed = True
                time.sleep(10)

    def get_one(self):
        """ Return the first element of the html list and remove it """
        return self.html.pop(0)

    def clear_html(self):
        """ Clear the html list """
        return self.html.clear()
