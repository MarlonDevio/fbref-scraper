# FBRef Scraper - Multiple Spiders Setup

This document explains the comprehensive spider setup for scraping football data from FBRef.com.

## 📁 Project Structure

```
fbref_scraper/
├── spiders/
│   ├── competition_spider.py      # Extract competition information
│   ├── season_spider.py          # Extract season data
│   ├── club_urls_spider.py       # Extract club URLs and basic info
│   ├── player_urls_spider.py     # Extract player URLs and basic info
│   ├── player_stats_spider.py    # Extract detailed player statistics
│   └── club_spider.py           # Original spider (seasons URLs)
├── pipelines/
│   ├── cleaning.py               # Data cleaning pipeline
│   ├── validation.py             # Data validation pipeline
│   └── database.py              # PostgreSQL storage pipeline
├── items.py                      # All item definitions
├── main.py                      # CLI runner script
└── utils/
    └── urls.py                  # URL utility functions
```

## 🕷️ Available Spiders

### 1. Competition Spider (`competitions`)
**Purpose**: Extract information about football competitions/leagues
- **Input**: FBRef competitions main page
- **Output**: Competition details, countries, tiers, available seasons
- **Usage**: `python main.py competitions`

### 2. Season Spider (`seasons`)
**Purpose**: Extract season information for major competitions
- **Input**: Competition history pages
- **Output**: Season years, participating clubs, URLs
- **Usage**: `python main.py seasons`

### 3. Club URLs Spider (`club_urls`)
**Purpose**: Extract club information from current season stats
- **Input**: Current season stats pages for top 5 leagues
- **Output**: Club names, countries, leagues, player counts
- **Usage**: `python main.py club_urls`

### 4. Player URLs Spider (`player_urls`)
**Purpose**: Extract player information from club squad pages
- **Input**: Club squad pages
- **Output**: Player names, positions, nationalities, DOB
- **Usage**: 
  - `python main.py player_urls` (uses default clubs)
  - `python main.py player_urls "url1,url2,url3"` (custom club URLs)

### 5. Player Stats Spider (`player_stats`)
**Purpose**: Extract detailed player statistics
- **Input**: Individual player pages
- **Output**: Season-by-season stats (goals, assists, cards, minutes, etc.)
- **Usage**:
  - `python main.py player_stats` (requires URLs)
  - `python main.py player_stats "url1,url2,url3"` (custom player URLs)

## 🔧 Pipeline System

### 1. Cleaning Pipeline (Priority: 100)
- Normalizes text fields (strip whitespace, normalize spaces)
- Cleans URLs and numeric fields
- Extracts IDs from URL patterns
- Converts numeric strings to integers

### 2. Validation Pipeline (Priority: 200)
- Validates required fields per item type
- Checks URL formats
- Validates numeric field types
- Drops invalid items with detailed error messages

### 3. Database Pipeline (Priority: 300)
- Stores items in PostgreSQL database
- Creates tables automatically
- Handles conflicts with UPSERT operations
- Supports all item types with proper relationships

## 🗄️ Database Schema

### Tables Created Automatically:
- `competitions` - Competition/league information
- `seasons` - Season data with participating clubs
- `clubs` - Club information and metadata
- `players` - Player personal information
- `player_stats` - Detailed player statistics per season

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install scrapy psycopg2-binary python-dotenv

# Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_USER=your_username
export POSTGRES_PASSWORD=your_password
export POSTGRES_DB=fbref_db
export POSTGRES_PORT=5432
```

### 2. Run Individual Spiders
```bash
# Extract competitions
python main.py competitions

# Extract club information
python main.py club_urls

# Extract players from specific clubs
python main.py player_urls "https://fbref.com/en/squads/b8fd03ef/2024-2025/Manchester-City-Stats"

# Run all spiders in sequence
python main.py all
```

### 3. Using Scrapy Commands Directly
```bash
# Run with custom settings
scrapy crawl competitions -s DOWNLOAD_DELAY=5

# Save output to file
scrapy crawl club_urls -o clubs.json

# Run with specific arguments
scrapy crawl player_urls -a club_urls="url1,url2"
```

## 📊 Data Flow

```
1. competitions → Extract all available competitions
2. seasons → Get historical season data
3. club_urls → Current season club information
4. player_urls → Player information from clubs
5. player_stats → Detailed statistics per player
```

## ⚙️ Configuration

### Custom Settings Per Spider
- **Download delays**: Configured per spider to avoid being blocked
- **Concurrent requests**: Limited to prevent overloading the server
- **User agents**: Configured to appear as regular browser requests

### Xpath Patterns Used
Based on `doc.md`, the spiders use these key patterns:
- Competitions: `//table[@id='comps_club']//th[contains(@class, "left")]`
- Clubs: `//table[contains(@id, "overall")]//td[contains(@class, "left") and contains(@data-stat, "team")]//a`
- Players: `//table[contains(@id, "standard")]//th[contains(@class, "left") and contains(@data-stat, "player")]//a`

## 🔍 Monitoring and Debugging

### Check Spider Status
```bash
# View spider logs
scrapy crawl club_urls -L INFO

# Debug mode
scrapy crawl competitions -L DEBUG

# Check specific items
python main.py read
```

### Common Issues
1. **Rate limiting**: Increase `DOWNLOAD_DELAY` in settings
2. **Database connection**: Check PostgreSQL credentials
3. **Missing data**: Verify xpath selectors on current page structure

## 📈 Performance Tips

1. **Batch Processing**: Run spiders in logical order (competitions → seasons → clubs → players)
2. **Incremental Updates**: Use database constraints to avoid duplicates
3. **Monitoring**: Check logs for failed requests and validation errors
4. **Resource Management**: Adjust concurrent requests based on server response

## 🛠️ Extending the System

### Adding New Spiders
1. Create new spider in `spiders/` directory
2. Define corresponding item in `items.py`
3. Update validation pipeline for new item type
4. Add database schema in database pipeline
5. Update main.py CLI interface

### Custom Pipelines
Create additional pipelines for:
- Data transformation
- External API integration  
- File exports
- Data enrichment

This setup provides a robust, scalable system for comprehensive football data extraction from FBRef.com with proper data validation, cleaning, and storage.
