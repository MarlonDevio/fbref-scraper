class UrlBuilder:
    """
    url structures:
        https://fbref.com/en/comps/9/history/Premier-League-Seasons
    """

    def __init__(self, base_url, type_of_url):
        self.base_url = base_url
        self.type_of_url = type_of_url

    @property
    def base_url(self) -> str:
        return self.base_url

    @base_url.setter
    def base_url(self, value: str) -> None:
        self.base_url = value

    @property
    def url_type(self):
        return self.type_of_url


    @url_type.setter
    def url_type(self, value: tuple[str,str]) -> None:
        self.url_type = value