import requests
from bs4 import BeautifulSoup
import time
import re

def fetch_game_info(appid):
    """Fetch game information from Steam, bypassing age check if needed."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0"
    })

    # Set the birthtime cookie to bypass age check (e.g., Jan 1, 1990)
    session.cookies.set("birthtime", str(int(time.mktime(time.strptime("1990-01-01", "%Y-%m-%d")))))
    session.cookies.set("lastagecheckage", "1-January-1990")
    session.cookies.set("mature_content", "1")  # Sometimes needed

    url = f"https://store.steampowered.com/app/{appid}"
    res = session.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')

    # Check if we still got redirected to the age check page
    if soup.title and "Age Check" in soup.title.text:
        raise ValueError("Age check not bypassed – something went wrong with cookies.")

    # Game Name
    game_name_elem = soup.find("div", id="appHubAppName")
    if not game_name_elem:
        raise ValueError("Game name not found - invalid App ID or game not accessible")
    game_name = game_name_elem.get_text(strip=True)

    # About
    about = soup.find("div", id="game_area_description")
    if not about:
        raise ValueError("Game description not found")

    for tag in about.select("img, .bb_wide_img_ctn"):
        tag.decompose()
    about_html = ' '.join(str(c) for c in about.contents).replace("<h2>About This Game</h2>", "").strip()

    # System requirements (Windows)
    sysreq = soup.find("div", class_="game_area_sys_req sysreq_content active", attrs={"data-os": "win"})
    min_reqs_html = str(sysreq.find("ul", class_="bb_ul")) if sysreq and sysreq.find("ul", class_="bb_ul") else ""

    # Genre, developer, and publisher
    block = soup.find("div", id="genresAndManufacturer")
    genres = []
    developer = ""
    publisher = ""

    if block:
        genre_links = block.select("b:-soup-contains('Genre:') + span a")
        genres = [a.text.strip() for a in genre_links]

        dev_tag = block.select_one("b:-soup-contains('Developer:') + a")
        developer = dev_tag.text.strip() if dev_tag else ""

        pub_tag = block.select_one("b:-soup-contains('Publisher:') + a")
        publisher = pub_tag.text.strip() if pub_tag else ""

    # Categories
    categories = []
    category_tags = soup.select(".glance_tags.popular_tags a")
    for tag in category_tags:
        category_text = tag.get_text(strip=True)
        if category_text:
            categories.append(category_text)

    # Screenshots
    screenshot_imgs = soup.select(".highlight_strip_item img")
    screenshots = []
    for img in screenshot_imgs[-2:]:
        if "src" in img.attrs:
            screenshot_url = img["src"].split("?")[0].replace("116x65", "600x338")
            screenshots.append(screenshot_url)

        # Filter valid screenshot URLs (exclude movie thumbnails and keep only ss_*.jpg with proper size)
    valid_screenshots = []
    for img in screenshot_imgs:
        src = img.get("src", "")
        if re.search(r'/ss_.*\.600x338\.jpg$', src):
            cleaned_url = src.split("?")[0]
            valid_screenshots.append(cleaned_url)

    # Select two screenshots from the middle
    num_screenshots = len(valid_screenshots)
    if num_screenshots >= 2:
        mid_index = num_screenshots // 2
        ss1_url = valid_screenshots[mid_index - 1] if mid_index - 1 >= 0 else ""
        ss2_url = valid_screenshots[mid_index] if mid_index < num_screenshots else ""
    else:
        ss1_url, ss2_url = (valid_screenshots + ["", ""])[:2]


    # SEO Metadata
    focus_keyphrase = f"{game_name} SteamRIP com"
    meta_description = f"{game_name} Free Download SteamRIP.com Get {game_name} PC game for free instantly and play pre-installed on SteamRIP"

    return {
        "game_name": game_name,
        "about_html": about_html,
        "minimum_sysreq_html": min_reqs_html,
        "genres": genres,
        "developer": developer,
        "publisher": publisher,
        "categories": categories,
        "focus_keyphrase": focus_keyphrase,
        "meta_description": meta_description,
        "ss1_url": ss1_url,
        "ss2_url": ss2_url,
    }
