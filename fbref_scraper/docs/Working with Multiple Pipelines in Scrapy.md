# Working with Multiple Pipelines in Scrapy

## 1. Creating Multiple Independent Pipelines

You can define multiple pipelines in your `pipelines.py` file:

```python name=pipelines.py
class CleaningPipeline:
    def process_item(self, item, spider):
        # Clean data (strip whitespace, normalize text, etc.)
        if 'title' in item:
            item['title'] = item['title'].strip()
        if 'description' in item:
            item['description'] = item['description'].strip()
        return item

class ValidationPipeline:
    def process_item(self, item, spider):
        # Validate data (check required fields, data types, etc.)
        if 'price' in item and not isinstance(item['price'], (int, float)):
            raise DropItem(f"Invalid price in {item}")
        return item

class DatabasePipeline:
    def __init__(self, db_settings):
        self.db_settings = db_settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_settings=crawler.settings.get('DATABASE_SETTINGS')
        )

    def open_spider(self, spider):
        # Connect to database
        # ...

    def close_spider(self, spider):
        # Close connection
        # ...

    def process_item(self, item, spider):
        # Store item in database
        # ...
        return item

class LoggingPipeline:
    def process_item(self, item, spider):
        # Log the item
        spider.logger.info(f"Processed: {item['title']}")
        return item
```

## 2. Configuring Pipeline Order in settings.py

In `settings.py`, you control which pipelines are active and their execution order:

```python name=settings.py
ITEM_PIPELINES = {
    'yourproject.pipelines.CleaningPipeline': 100,      # Runs first (lowest number)
    'yourproject.pipelines.ValidationPipeline': 200,    # Runs second
    'yourproject.pipelines.DatabasePipeline': 300,      # Runs third
    'yourproject.pipelines.LoggingPipeline': 400,       # Runs last (highest number)
}
```

The numbers (100, 200, etc.) determine the order of execution. Lower numbers run first.

## 3. Multiple Processing Steps in a Single Pipeline

You can also implement multiple processing steps within a single pipeline:

```python name=pipelines.py
class ComplexProcessingPipeline:
    def process_item(self, item, spider):
        item = self._clean_item(item)
        self._validate_item(item)
        self._transform_item(item)
        self._store_item(item)
        return item

    def _clean_item(self, item):
        # Clean data
        if 'title' in item:
            item['title'] = item['title'].strip()
        return item

    def _validate_item(self, item):
        # Validate data
        if 'price' not in item:
            raise DropItem("Missing price")
        return item

    def _transform_item(self, item):
        # Transform data
        if 'price' in item:
            item['price_usd'] = item['price'] * self.exchange_rate
        return item

    def _store_item(self, item):
        # Store data
        # ...
        return item
```

## 4. Spider-Specific Pipelines

You can create pipelines that only process items from specific spiders:

```python name=pipelines.py
class ProductSpiderPipeline:
    def process_item(self, item, spider):
        if spider.name == 'product_spider':
            # Process items from product_spider only
            # ...
        return item

class ReviewSpiderPipeline:
    def process_item(self, item, spider):
        if spider.name == 'review_spider':
            # Process items from review_spider only
            # ...
        return item
```

## 5. Conditional Pipeline Execution Based on Item Type

```python name=pipelines.py
from yourproject.items import ProductItem, ReviewItem

class ItemTypeBasedPipeline:
    def process_item(self, item, spider):
        if isinstance(item, ProductItem):
            # Process product items
            # ...
        elif isinstance(item, ReviewItem):
            # Process review items
            # ...
        return item
```

## 6. Using Built-in Pipelines

Scrapy provides some built-in pipelines you can use:

```python name=settings.py
ITEM_PIPELINES = {
    'scrapy.pipelines.images.ImagesPipeline': 1,
    'scrapy.pipelines.files.FilesPipeline': 2,
    'yourproject.pipelines.CustomPipeline': 300,
}

# Configuration for ImagesPipeline
IMAGES_STORE = 'path/to/images/directory'
```

## 7. Dropping Items in Pipelines

You can drop items to prevent further processing:

```python name=pipelines.py
from scrapy.exceptions import DropItem

class FilterPipeline:
    def process_item(self, item, spider):
        if not item.get('price'):
            raise DropItem("Missing price")
        if float(item['price']) < 10:
            raise DropItem("Price too low")
        return item
```

## 8. Asynchronous Pipelines

You can also create asynchronous pipelines for non-blocking operations:

```python name=pipelines.py
import asyncio
import aiohttp

class AsyncDatabasePipeline:
    async def process_item(self, item, spider):
        await self.store_item_async(item)
        return item

    async def store_item_async(self, item):
        # Async database operation
        async with aiohttp.ClientSession() as session:
            await session.post('https://your-api.com/items', json=dict(item))
```

## 9. Example of a Complete Multi-Stage Processing System

Here's a more complete example showing different pipelines for a product scraping system:

```python name=pipelines.py
from scrapy.exceptions import DropItem
import psycopg2
import redis
from elasticsearch import Elasticsearch

class DataCleaningPipeline:
    def process_item(self, item, spider):
        # Clean text fields
        for field in ['title', 'description', 'brand']:
            if field in item:
                item[field] = item[field].strip()

        # Normalize prices
        if 'price' in item and isinstance(item['price'], str):
            item['price'] = float(item['price'].replace('$', '').replace(',', ''))

        return item

class DataValidationPipeline:
    def process_item(self, item, spider):
        # Check required fields
        required_fields = ['title', 'price', 'url']
        for field in required_fields:
            if field not in item or not item[field]:
                raise DropItem(f"Missing {field} in {item}")

        # Validate data types
        if not isinstance(item['price'], (int, float)):
            raise DropItem(f"Invalid price type in {item}")

        return item

class DuplicateCheckPipeline:
    def __init__(self):
        self.seen_urls = set()

    def process_item(self, item, spider):
        if item['url'] in self.seen_urls:
            raise DropItem(f"Duplicate item found: {item}")
        self.seen_urls.add(item['url'])
        return item

class PostgreSQLPipeline:
    def __init__(self, db_settings):
        self.db_settings = db_settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            db_settings=crawler.settings.get('POSTGRES_SETTINGS')
        )

    def open_spider(self, spider):
        self.conn = psycopg2.connect(**self.db_settings)
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.conn.close()

    def process_item(self, item, spider):
        self.cursor.execute(
            "INSERT INTO products (title, price, url) VALUES (%s, %s, %s)",
            (item['title'], item['price'], item['url'])
        )
        self.conn.commit()
        return item

class ElasticsearchPipeline:
    def __init__(self, es_settings):
        self.es_settings = es_settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            es_settings=crawler.settings.get('ELASTICSEARCH_SETTINGS')
        )

    def open_spider(self, spider):
        self.es = Elasticsearch([self.es_settings])

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        self.es.index(
            index="products",
            document=dict(item)
        )
        return item

class RedisCachePipeline:
    def __init__(self, redis_settings):
        self.redis_settings = redis_settings

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            redis_settings=crawler.settings.get('REDIS_SETTINGS')
        )

    def open_spider(self, spider):
        self.redis = redis.Redis(**self.redis_settings)

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        # Cache the item URL to avoid re-scraping
        self.redis.set(f"scraped:{item['url']}", 1, ex=86400)  # expires in 24h
        return item
```

And in `settings.py`:

```python name=settings.py
ITEM_PIPELINES = {
    'yourproject.pipelines.DataCleaningPipeline': 100,
    'yourproject.pipelines.DataValidationPipeline': 200,
    'yourproject.pipelines.DuplicateCheckPipeline': 300,
    'yourproject.pipelines.PostgreSQLPipeline': 400,
    'yourproject.pipelines.ElasticsearchPipeline': 500,
    'yourproject.pipelines.RedisCachePipeline': 600,
}

# Database settings
POSTGRES_SETTINGS = {
    'host': 'localhost',
    'database': 'products',
    'user': 'postgres',
    'password': 'password'
}

ELASTICSEARCH_SETTINGS = {
    'host': 'localhost',
    'port': 9200
}

REDIS_SETTINGS = {
    'host': 'localhost',
    'port': 6379,
    'db': 0
}
```

## Key Points to Remember

1. **Order matters**: Lower numbers in `ITEM_PIPELINES` run first
2. **Chain of processing**: Each pipeline receives the item from the previous one
3. **Spider-specific processing**: Check `spider.name` to process only certain spiders
4. **Item-specific processing**: Check item type to handle different items differently
5. **Error handling**: Use try/except blocks to handle errors gracefully
6. **Dropping items**: Raise `DropItem` exception to stop processing an item
7. **Component initialization**: Use `open_spider` and `close_spider` for setup/teardown

Let me know if you need more specific examples or have questions about any particular aspect of pipeline processing!

