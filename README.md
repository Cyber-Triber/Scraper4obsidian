# Obsidian Web Scraper

## Popis / Description

Tento Python skript umožňuje scrapování webových stránek a ukládání jejich obsahu do Markdown souborů v adresáři aplikace Obsidian. Podporuje zpracování jednotlivých stránek i sitemap.xml pro získání více URL k scrapování.

This Python script allows scraping web pages and saving their content as Markdown files in the Obsidian application directory. It supports processing individual pages and sitemap.xml to fetch multiple URLs for scraping.

## Požadavky / Requirements

- Python 3.8+
- Knihovny: `requests`, `BeautifulSoup4`, `html2text`, `crawl4ai`

```bash
pip install requests beautifulsoup4 html2text crawl4ai
```

## Nastavení / Configuration

V souboru skriptu lze upravit následující proměnné:

In the script file, you can modify the following variables:

```python
BASE_PATH = r"C:\Path_to_your_obsidian_folder_to_store_scraped_sites"  # Cesta k výstupní složce
URL_FILE = r"C:\Path_to_your_obsidian_file\toScrape.md"  # Soubor s URL adresami
MARKER = "[X] - "  # Označení zpracovaných URL
MD_CLEANER = False  # Čištění Markdown souborů
LANGUAGE = "en"  # Jazyk (cs/en)
DEBUG = False  # Debug mód
```

## Použití / Usage

1. Přidejte URL adresy k scrapování do souboru `toScrape.md`.
2. Spusťte skript:

```bash
python scraper.py
```

1. Výstupy se uloží do složky `BASE_PATH`.



## Verze: 0.9.0

### Popis funkcí (CZ):
✅ **Automatické stahování obsahu** – Skript umožňuje extrahovat textový obsah z webových stránek.

✅ **Zpracování a formátování** – Stažená data jsou zpracována do formátu vhodného pro použití v Obsidianu.

✅ **Ukládání do Markdown souborů** – Každý stažený článek či stránka je uložena jako samostatný Markdown soubor.

✅ **Možnost filtrování obsahu** – Uživatel může nastavit specifické prvky stránky, které chce extrahovat (např. nadpisy, odstavce, odkazy).

✅ **Podpora více zdrojů** – Skript může pracovat s více webovými stránkami současně.

### Features (EN):
✅ **Automated content scraping** – Extracts text content from web pages.

✅ **Processing and formatting** – Downloaded data is formatted for use in Obsidian.

✅ **Saving as Markdown files** – Each article or page is stored as a separate Markdown file.

✅ **Content filtering options** – Users can specify which elements to extract (e.g., headings, paragraphs, links).

✅ **Multi-source support** – Can scrape multiple web pages at once.

## Changes tracker:
- **v0.9.0**
  - Přidáno verzování a Changes tracker
  - Dopsán popis funkcí v češtině i angličtině
  - Základní implementace skriptu



## Autor / Author

With 💗 and lots of ☕ [CyberTriber]
