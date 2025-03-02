import os
import requests
from crawl4ai import AsyncWebCrawler
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urljoin
import asyncio
from typing import List
from bs4 import BeautifulSoup
import html2text

######################
###   SETTINGS     ###
###   NASTAVENÍ    ###
######################
# en: Path to the directory in Obsidian where markdown files should be saved
# cs: Cesta k adresáři v obsidianu, kam se mají uložit markdown soubory
BASE_PATH = r"C:\Apps\Obsidian\CyberNote\🕷️crawl"
# en: File with URLs to process
# cs: Soubor s URL adresami k zpracování
URL_FILE = r"C:\Apps\Obsidian\CyberNote\🕷️crawl\__urls\toScrape.md"
# en: Marker for processed URL
# cs: Označení zpracované URL adresy
MARKER = "[X] - "
# en: Switch for cleaning markdown files after scraping
# cs: Přepínač pro čištění markdown souborů po scrapování
MD_CLEANER = False  
# en: Language (cs for Czech, en for English)
# cs: Jazyk (cs pro češtinu, en pro angličtinu)
LANGUAGE = "en"
# en: Debug flag
# cs: Debug flag
DEBUG = False

###############################
###        FUNCTIONS        ###
###         FUNKCE          ###
### DO NOT MODIFY FROM HERE ###
### ODTUD NIC  NEUPRAVOVAT  ###
###############################
TOTAL_URLS = 0

# en: Translations
# cs: Překlady
TRANSLATIONS = {
    "cs": {
        "BASE_PATH_ERROR": "Cesta BASE_PATH neexistuje: {BASE_PATH} - zkontroluj překlepy, cesta musí být absolutní (např. C:\\cesta\\k\\adresáři\\)",
        "URL_FILE_ERROR": "Cesta URL_FILE neexistuje: {URL_FILE} - zkontroluj překlepy, cesta musí být absolutní (např. C:\\cesta\\k\\souboru.md)",
        "MARKER_ERROR": "MARKER nesmí být prázdný řetězec. (default: '[X] - ')",
        "MD_CLEANER_ERROR": "MD_CLEANER musí být typu bool. (True nebo False)",
        "DEBUG_ERROR": "DEBUG musí být typu bool. (True nebo False)",
        "SETTINGS_ERRORS": "Nastavení obsahuje chyby:\n",
        "NO_URLS": "Žádné URL k zpracování.",
        "SCRAPING_PAGE": "Scrapuji stránku {url}",
        "REMAINING_URLS": "Zbývá zpracovat: {TOTAL_URLS} URL adres.",
        "SCRAPING_ERROR": "Chyba při scrapování {url}: Žádný obsah.",
        "PAGE_SAVED": "Stránka uložena do {file_path}",
        "SCRAPING_EXCEPTION": "Došlo k chybě při scrapování {url}: {e}",
        "SITEMAP_CHECK": "Kontroluji sitemap.xml na {sitemap_url}",
        "SITEMAP_FOUND": "Našel jsem {len(urls)} URL v sitemap.",
        "SITEMAP_ERROR": "Chyba při získávání sitemap: {e}",
        "UNEXPECTED_ERROR": "Neočekávaná chyba: {e}",
    },
    "en": {
        "BASE_PATH_ERROR": "BASE_PATH does not exist: {BASE_PATH} - check for typos, the path must be absolute (e.g., C:\\path\\to\\directory\\)",
        "URL_FILE_ERROR": "URL_FILE does not exist: {URL_FILE} - check for typos, the path must be absolute (e.g., C:\\path\\to\\file.md)",
        "MARKER_ERROR": "MARKER cannot be an empty string. (default: '[X] - ')",
        "MD_CLEANER_ERROR": "MD_CLEANER must be of type bool. (True or False)",
        "DEBUG_ERROR": "DEBUG must be of type bool. (True or False)",
        "SETTINGS_ERRORS": "Settings contain errors:\n",
        "NO_URLS": "No URLs to process.",
        "SCRAPING_PAGE": "Scraping page {url}",
        "REMAINING_URLS": "Remaining URLs to process: {TOTAL_URLS}.",
        "SCRAPING_ERROR": "Error scraping {url}: No content.",
        "PAGE_SAVED": "Page saved to {file_path}",
        "SCRAPING_EXCEPTION": "Error scraping {url}: {e}",
        "SITEMAP_CHECK": "Checking sitemap.xml at {sitemap_url}",
        "SITEMAP_FOUND": "Found {len(urls)} URLs in sitemap.",
        "SITEMAP_ERROR": "Error fetching sitemap: {e}",
        "UNEXPECTED_ERROR": "Unexpected error: {e}",
    }
}

def translate(key: str, **kwargs) -> str:
    """
    en: Returns the translated text based on the key and current language.
    cs: Vrátí přeložený text podle klíče a aktuálního jazyka.
    """
    return TRANSLATIONS[LANGUAGE].get(key, key).format(**kwargs)


# en: Function to check settings
# cs: Funkce pro kontrolu nastavení
def check_settings() -> None:
    """
    en: Checks if all variables in the 'SETTINGS' section are set and correct.
    cs: Zkontroluje, zda jsou všechny proměnné v části 'NASTAVENÍ' nastaveny a správné.
    """
    errors = []
    if not os.path.exists(BASE_PATH):
        errors.append(translate("BASE_PATH_ERROR", BASE_PATH=BASE_PATH))
    if not os.path.exists(URL_FILE):
        errors.append(translate("URL_FILE_ERROR", URL_FILE=URL_FILE))
    if not isinstance(MARKER, str) or not MARKER:
        errors.append(translate("MARKER_ERROR"))
    if not isinstance(MD_CLEANER, bool):
        errors.append(translate("MD_CLEANER_ERROR"))
    if not isinstance(DEBUG, bool):
        errors.append(translate("DEBUG_ERROR"))
    
    if errors:
        error_message = translate("SETTINGS_ERRORS") + "\n".join(errors)
        print(error_message)
        exit(1)

# en: Function to print debug messages
# cs: Funkce pro výpis debugovacích zpráv
def debug_print(message: str) -> None:
    if DEBUG:
        print(message)

# en: Function to clean HTML content
# cs: Funkce pro čištění HTML obsahu
def clean_html_content(html_content):
    """
    en: Cleans HTML content from unwanted parts.
    cs: Vyčistí HTML obsah od nechtěných částí.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # en: Remove only specific unwanted parts
    # cs: Odstranit pouze specifické nechtěné části
    for selector in ['.menu', '.language-options']:
        for element in soup.select(selector):
            element.decompose()

    return str(soup)

# en: Function to load URLs from file
# cs: Funkce pro načtení URL adres ze souboru
def load_urls() -> List[str]:
    """
    en: Loads URLs from the file and returns them as a list.
    cs: Načte URL adresy ze souboru a vrátí je jako seznam.
    """
    global TOTAL_URLS
    if not os.path.exists(URL_FILE):
        debug_print(f"Soubor {URL_FILE} neexistuje.")
        return []

    with open(URL_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    urls = [line.strip() for line in lines if line.strip() and not line.startswith(MARKER)]
    TOTAL_URLS = len(urls)
    debug_print(f"Načteno {len(urls)} URL adres k zpracování.")
    return urls 

# en: Function to mark URL as scraped
# cs: Funkce pro označení URL adresy jako zpracované
def mark_url_as_scraped(url: str) -> None:
    """
    en: Marks the URL as processed by adding the MARKER prefix. (see Settings)
    cs: Označí URL adresu jako zpracovanou přidáním MARKER prefixu. (viz. Nastavení)
    """
    with open(URL_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    with open(URL_FILE, "w", encoding="utf-8") as f:
        for line in lines:
            if line.strip() == url:
                f.write(f"{MARKER}{line}")  # en: Mark as done / cs: Označíme jako hotové
            else:
                f.write(line)

# en: Function to get URLs from sitemap.xml
# cs: Funkce pro získání URL adres ze sitemap.xml
async def get_sitemap_urls(url: str) -> List[str]:
    """
    en: Attempts to get URLs from sitemap.xml.
    cs: Pokusí se získat URL z sitemap.xml.
    """
    sitemap_url = url.rstrip("/") + "/sitemap.xml"
    debug_print(translate("SITEMAP_CHECK", sitemap_url=sitemap_url))

    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()
        tree = ET.ElementTree(ET.fromstring(response.text))
        root = tree.getroot()

        urls = []
        for elem in root.iter():
            if 'loc' in elem.tag:
                loc = elem.text.strip()
                if loc and loc.startswith("http"):
                    urls.append(urljoin(url, loc))

        debug_print(translate("SITEMAP_FOUND", len=len(urls)))
        return urls
    except (requests.exceptions.RequestException, ET.ParseError) as e:
        debug_print(translate("SITEMAP_ERROR", e=e))
        return []

# en: Function to scrape page content
# cs: Funkce pro scrapování obsahu
async def scrap_page(url: str) -> None:
    """
    en: Scrapes the page content and saves it in markdown format.
    cs: Scrapuje obsah stránky a uloží do markdown formátu.
    """
    debug_print(translate("SCRAPING_PAGE", url=url))
    global TOTAL_URLS
    print(translate("REMAINING_URLS", TOTAL_URLS=TOTAL_URLS))
    TOTAL_URLS -= 1

    async with AsyncWebCrawler() as crawler:
        try:
            result = await crawler.arun(url=url)
            if not result or not hasattr(result, 'markdown') or not result.markdown:
                debug_print(translate("SCRAPING_ERROR", url=url))
                return

            if MD_CLEANER:
                # en: Clean HTML content before converting to markdown
                # cs: Vyčistit HTML obsah před konverzí na markdown
                cleaned_html = clean_html_content(result.html)
                h = html2text.HTML2Text()
                h.ignore_links = False  # en: Preserve links / cs: Zachování odkazů
                h.ignore_images = False  # en: Preserve images / cs: Zachování obrázků
                h.ignore_tables = False  # en: Preserve tables / cs: Zachování tabulek
                h.ignore_emphasis = False  # en: Preserve bold and italics / cs: Zachování tučného a kurzívy
                h.body_width = 0  # en: Do not artificially wrap lines / cs: Nezalamovat řádky uměle
                md_content = h.handle(cleaned_html)
                markdown_content = f"# {url}\n\n{md_content}"
            else:
                markdown_content = f"# {url}\n\n{result.markdown}"
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace("www.", "").replace(":", "_")
            save_path = os.path.join(BASE_PATH, domain)

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            file_name = parsed_url.path.strip("/").replace("/", "_").replace(":","").replace(".","_") + ".md" if parsed_url.path.strip("/") else "index.md"
            file_path = os.path.join(save_path, file_name)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            debug_print(translate("PAGE_SAVED", file_path=file_path))
        except Exception as e:
            debug_print(translate("SCRAPING_EXCEPTION", url=url, e=e))

# en: Function to process domain
# cs: Funkce pro zpracování domény
async def crawl_domain(url: str) -> None:
    """
    en: Processes the domain: either by sitemap or as a single page.
    cs: Zpracuje doménu: buď podle sitemap, nebo jako single page.
    """
    global TOTAL_URLS
    try:
        urls = await get_sitemap_urls(url)  # en: Get URLs from sitemap.xml if available / cs: Získá URL z sitemap.xml poku je k dispozici
        if urls:
            TOTAL_URLS += len(urls)  
            for page_url in urls:
                await scrap_page(page_url)  # en: Scrape individual pages / cs: Scrapuje jednotlivé stránky
        else:
            await scrap_page(url)  # en: Scrape single page / cs: Scrapuje singlepage stránku

        mark_url_as_scraped(url)  # en: Mark URL as done in Obsidian / cs: Označí URL jako hotovou v obsidianu
    except Exception as e:
        debug_print(translate("UNEXPECTED_ERROR", e=e))

# en: Main function
# cs: Hlavní funkce
async def main() -> None:
    check_settings()
    urls = load_urls()
    if not urls:
        debug_print(translate("NO_URLS"))
        return

    for url in urls:
        await crawl_domain(url)

if __name__ == "__main__":
    asyncio.run(main())
