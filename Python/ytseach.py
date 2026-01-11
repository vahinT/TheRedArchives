from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import Counter
import re
import time

def extract_hashtags(text):
    return re.findall(r"#\w+", text)

def get_video_info(driver, video_url):
    driver.get(video_url)
    time.sleep(3)

    hashtags = []
    views = "N/A"
    likes = "N/A"
    duration = "N/A"

    try:
        tag_elements = driver.find_elements(By.XPATH, '//a[starts-with(@href, "/hashtag/")]')
        for tag in tag_elements:
            hashtags.append(tag.text)

        views_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//span[contains(text(), "views")]'))
        )
        views = views_element.text

        like_button = driver.find_element(By.XPATH, '//ytd-toggle-button-renderer[1]//button')
        likes = like_button.get_attribute("aria-label")

        meta_duration = driver.find_elements(By.XPATH, '//meta[@itemprop="duration"]')
        if meta_duration:
            duration = meta_duration[0].get_attribute("content")

    except Exception as e:
        print(f"[Warning] Couldn't extract from {video_url}: {e}")

    return {
        "url": video_url,
        "hashtags": hashtags,
        "views": views,
        "likes": likes,
        "duration": duration,
    }

def get_video_links(topic, max_videos=10, scrolls=3):
    options = Options()
    options.binary_location = r"C:\Program Files\chrome-win64\chrome.exe"
    options.add_argument("--headless")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(
        service=Service(r"C:\Program Files\chrome-win64\chromedriver-win64\chromedriver.exe"),
        options=options
    )

    search_url = f"https://www.youtube.com/results?search_query={topic}"
    driver.get(search_url)

    for _ in range(scrolls):
        driver.execute_script("window.scrollBy(0, 2000);")
        time.sleep(2)

    video_elements = driver.find_elements(By.XPATH, '//a[@id="video-title"]')
    links = []
    for video in video_elements:
        href = video.get_attribute("href")
        if href and "/watch?v=" in href:
            links.append(href)
        if len(links) >= max_videos:
            break

    driver.quit()
    return links

def analyze_youtube_trends(topic, max_videos=10):
    video_links = get_video_links(topic, max_videos)

    options = Options()
    options.binary_location = r"C:\Program Files\chrome-win64\chrome.exe"
    options.add_argument("--headless")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(
        service=Service(r"C:\Program Files\chrome-win64\chromedriver-win64\chromedriver.exe"),
        options=options
    )

    all_hashtags = []
    video_data = []

    for link in video_links:
        info = get_video_info(driver, link)
        all_hashtags.extend(info["hashtags"])
        video_data.append(info)

    driver.quit()

    top_tags = Counter(all_hashtags).most_common(10)
    return top_tags, video_data

# 🔍 Example usage
if __name__ == "__main__":
    topic = input("enter topic : ")  # or try "gaming", "python", etc.
    print(f"Analyzing YouTube trends for: {topic}...\n")

    hashtags, videos = analyze_youtube_trends(topic, max_videos=10)

    print("🔝 Top 10 Hashtags:")
    for tag, count in hashtags:
        print(f"{tag}: {count} times")

    print("\n📊 Video Details:")
    for vid in videos:
        print(f"\n🎥 URL: {vid['url']}")
        print(f"   📌 Hashtags: {', '.join(vid['hashtags']) if vid['hashtags'] else 'None'}")
        print(f"   👁️ Views: {vid['views']}")
        print(f"   👍 Likes: {vid['likes']}")
        print(f"   ⏱️ Duration: {vid['duration']}")

print("---ProgFin-Vahin--")
