This design emphasizes asynchronous operations with `httpx` and `asyncio`, type safety with Pydantic, and maximum flexibility to handle diverse data sources without modifying the core framework.

---

### High-Level Architecture Overview

The framework operates on an asynchronous, event-driven model orchestrated by the **Engine**. The data flows in a loop, processing requests and items concurrently.

**Conceptual Data Flow:**

```
[ Scraper ] -> provides initial Requests -> [ Engine ]
    ^                                         |
    |                                         v
(receives Response, yields Items/Requests)  [ Scheduler ] -> provides next Request
    |                                         ^
    |                                         | (new Requests)
    +<-------------------------------------- [ Downloader ] <- gets Request
    |                                         |
(sends Item)                                  v (returns Response)
    |                                         [ Scraper's Parse Method ]
    |                                         |
    v                                         v (yields Item)
[ Item Pipeline ] <---------------------+ [ Engine ]
    |
    v
[ Data Storage (DB, JSON, etc.) ]
```

- The **Engine** is the central coordinator, running the `asyncio` event loop.
- The **Scraper** defines the scraping logic (initial URLs, how to parse pages, what data to extract).
- The **Scheduler** holds the queue of URLs to be visited.
- The **Downloader** is responsible for all network communication.
- The **Parser** is a strategy object used by the Scraper to interpret HTML/XML.
- **Pydantic Items** are structured data containers.
- The **Item Pipeline** is a series of processing steps for each extracted item.

---

### Detailed Component Breakdown

Each component has a Single Responsibility (the 'S' in SOLID), promoting high cohesion and loose coupling.

#### 1\. Configuration Manager

- **Responsibility**: To load and provide type-safe configuration to all parts of the framework. This avoids hardcoding and makes the system highly adaptable.
- **Implementation**: We'll use `pydantic-settings` to load configuration from environment variables, a `.env` file, or a YAML file. This provides a single, validated source of truth.

<!-- end list -->

```python
# settings.py
from pydantic_settings import BaseSettings
from typing import List, Dict, Any

class Settings(BaseSettings):
    # Downloader settings
    REQUEST_TIMEOUT: int = 15
    DEFAULT_HEADERS: Dict[str, str] = {"User-Agent": "Mozilla/5.0..."}
    RETRY_ATTEMPTS: int = 3
    RETRY_BACKOFF_FACTOR: float = 0.5

    # Parser settings
    PARSER_ENGINE: str = "bs4" # 'bs4' or 'lxml'

    # Pipeline settings
    ITEM_PIPELINES: List[str] = [
        "framework.pipelines.validation.ValidationPipeline",
        "framework.pipelines.storage.SaveToJSONPipeline",
    ]

    # Concurrency settings
    CONCURRENT_REQUESTS: int = 16

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

#### 2\. Downloader

- **Responsibility**: To execute HTTP(S) requests asynchronously and return responses. It handles headers, proxies, timeouts, and implements a robust retry mechanism.
- **Implementation**: It wraps `httpx.AsyncClient`. Retry logic is handled using a library like `tenacity` or by implementing a custom `httpx.AsyncBaseTransport`. Configuration for timeouts, headers, and retries is pulled from the `Settings` object.

#### 3\. Parser (Abstract Base Class & Strategy Pattern)

- **Responsibility**: To provide a consistent interface for parsing HTML/XML content, abstracting away the underlying library (`BeautifulSoup4` or `lxml`). This is a classic example of the **Strategy Pattern**.
- **Implementation**: An abstract base class `BaseParser` defines the contract. Concrete implementations provide the specific parsing logic. The Scraper will be instantiated with a specific parser strategy based on the configuration.

#### 4\. Data Items (Pydantic Models)

- **Responsibility**: To define the schema for the data being scraped. This ensures that all extracted data is structured and validated automatically.
- **Implementation**: Simple Python classes inheriting from `pydantic.BaseModel`. This provides compile-time type checking with tools like MyPy and runtime data validation, which is critical for data integrity when scraping multiple, potentially inconsistent, sources.

#### 5\. Item Pipeline

- **Responsibility**: To process scraped items through a series of sequential steps. Each step is a small, focused component (e.g., clean data, validate against business rules, store in a database).
- **Implementation**: The `Engine` passes each scraped item to a chain of pipeline components. Each component in the chain receives the item from the previous one, processes it, and returns it for the next step. This design is highly extensible (Open/Closed Principle), as new processing steps can be added to the configuration without changing any framework code.

#### 6\. Scraper/Spider

- **Responsibility**: To contain the site-specific logic. A developer implements a Scraper class for each target website. The Scraper defines the starting URLs and the callback method for parsing the response.
- **Implementation**: A user-defined class that inherits from a `BaseScraper`. It specifies `start_urls` and a `parse` method. The `parse` method receives a `Response` object and uses the injected `Parser` to extract data, yielding either `Data Items` or new `Request` objects for the `Scheduler`.

---

### Code Skeletons & Examples

Here are the code skeletons that form the core of the framework.

#### Base Class Skeletons

```python
# framework/parsers/base_parser.py
from abc import ABC, abstractmethod
from typing import Any, List

class BaseParser(ABC):
    def __init__(self, content: str):
        self._document = self._load_document(content)

    @abstractmethod
    def _load_document(self, content: str) -> Any:
        """Loads content into the parser's internal document representation."""
        pass

    @abstractmethod
    def css(self, selector: str) -> List[Any]:
        """Select elements using a CSS selector."""
        pass

    @abstractmethod
    def xpath(self, query: str) -> List[Any]:
        """Select elements using an XPath query."""
        pass

# framework/pipelines/base_pipeline.py
from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Type # For Scraper type hint

class BasePipelineStep(ABC):
    @abstractmethod
    async def process_item(self, item: BaseModel, scraper: Type['BaseScraper']) -> BaseModel:
        """
        Process an item. Must return the item for the next stage.
        Can raise DropItem exception to halt processing for this item.
        """
        pass
```

#### Pydantic Item Example

This defines the data structure for player statistics.

```python
# project_scrapers/items.py
from pydantic import BaseModel, Field
from typing import Optional

class PlayerStatsItem(BaseModel):
    player_name: str
    player_url: str = Field(..., alias="playerUrl")
    club: str
    nationality: str
    position: str
    games_played: int = Field(default=0, alias="gamesPlayed")
    goals: int = 0
    assists: int = 0
    market_value_eur: Optional[float] = Field(default=None, alias="marketValueEur")
    source_site: str # To track which website the data came from
```

#### Full Scraper Example

This is what a developer using your framework would write to scrape player data from a hypothetical site.

```python
# project_scrapers/transfermarkt_scrapers.py
from typing import AsyncGenerator, Union
from framework.core.scraper import BaseScraper
from framework.http.request import Request
from framework.http.response import Response
from .items import PlayerStatsItem

class TransfermarktPlayerScraper(BaseScraper):
    name = "transfermarkt_players"
    start_urls = ["https://www.hypothetical-transfer-stats.com/players/all"]

    async def parse(self, response: Response) -> AsyncGenerator[Union[PlayerStatsItem, Request], None]:
        """Parses the main player list page."""
        # Use the injected parser (e.g., BS4Parser) via self.parser
        player_rows = response.parser.css("table.items > tbody > tr")

        for row in player_rows:
            # The parser's element wrapper would have its own .css()/.text/.attr() methods
            player_name = row.css("td.hauptlink a").text()
            player_url = row.css("td.hauptlink a").attr("href")
            club = row.css("td.zentriert a > img").attr("alt")

            # Yield a validated data item
            yield PlayerStatsItem(
                playerUrl=response.urljoin(player_url),
                playerName=player_name,
                club=club,
                nationality=row.css("td.zentriert > img.flaggenrahmen").attr("title"),
                position=row.css("td:nth-of-type(4)").text(),
                source_site=self.name
            )

        # Example of handling pagination
        next_page_url = response.parser.css("li.tm-pagination__item--next-page > a").attr("href")
        if next_page_url:
            # Yield a new Request to be scheduled and crawled
            yield Request(url=response.urljoin(next_page_url), callback=self.parse)
```

---

### Proposed Directory Structure

This structure separates the core, reusable framework from the project-specific scrapers.

```
soccer_stats_project/
├── .env                  # Environment variables (API keys, DB connections)
├── pyproject.toml        # Project dependencies and metadata
├── README.md
├── main.py               # Main entry point to run the engine
|
├── framework/            # The core, reusable scraping framework
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── engine.py     # The main orchestrator
│   │   └── scraper.py    # BaseScraper class
│   ├── exceptions.py     # Custom exceptions (e.g., DropItem)
│   ├── http/
│   │   ├── __init__.py
│   │   ├── downloader.py # Manages httpx client, retries
│   │   ├── request.py    # Request object definition
│   │   └── response.py   # Response object definition
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── base_parser.py # ABC for parsers
│   │   ├── bs4_parser.py  # BeautifulSoup4 implementation
│   │   └── lxml_parser.py # lxml implementation
│   └── pipelines/
│       ├── __init__.py
│       ├── base_pipeline.py # ABC for pipeline steps
│       ├── storage.py    # e.g., SaveToJSONPipeline, SaveToDbPipeline
│       └── validation.py # e.g., DataValidationPipeline
|
└── project_scrapers/     # Project-specific implementation
    ├── __init__.py
    ├── items.py          # Pydantic data models (PlayerStatsItem, ClubStatsItem)
    ├── pipelines.py      # Custom project-specific pipelines
    └── scrapers/
        ├── __init__.py
        ├── transfermarkt_scrapers.py
        └── sofascore_scrapers.py
```
