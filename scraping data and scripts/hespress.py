import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
import re
from datetime import datetime

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'}

def is_arabic(text):
    arabic_pattern = re.compile(r'[\u0600-\u06FF]+')
    return bool(arabic_pattern.search(text))

def parse_arabic_date(arabic_date):
    arabic_months = {
        'يناير': 'January', 'فبراير': 'February', 'مارس': 'March',
        'أبريل': 'April', 'ماي': 'May', 'يونيو': 'June',
        'يوليوز': 'July', 'غشت': 'August', 'شتنبر': 'September',
        'أكتوبر': 'October', 'نونبر': 'November', 'دجنبر': 'December'
    }

    # Use regex to extract Arabic day, month, year, hour, and minute
    match = re.match(r'(\S+)\s+(\d+)\s+(\S+)\s+(\d+)\s*-\s*(\d+):(\d+)', arabic_date)
    if match:
        day, day_number, month, year, hour, minute = match.groups()
        # Convert Arabic month name to English
        english_month = arabic_months[month]
        # Combine and parse the date in English format
        english_date = f"{english_month} {day_number} {year} - {hour}:{minute}"
        #return datetime.strptime(english_date, '%B %d %Y - %H:%M')
        return datetime.strptime(english_date, '%B %d %Y - %H:%M').strftime("%Y-%m-%d")
    else:
        raise ValueError("Invalid Arabic date format")

def scrape_comments(article_url):
    response = requests.get(article_url, headers=headers)
    if not response.ok:
        print(f"Failed to access the comments section: {article_url}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    comments_section = soup.find('ul', class_='comment-list')
    if not comments_section:
        return None

    comments = []
    for comment in comments_section.find_all('li', class_='comment'):
        date = comment.find('div', class_='comment-date').text.strip()
        text = comment.find('div', class_='comment-text').find('p').text.strip()

        if is_arabic(text):
            # Convert the Arabic date to a datetime format
            date = parse_arabic_date(date)

            comments.append({
                'date': date,
                'Text': text
            })

    return comments

# ... (rest of the code remains unchanged)
def scroll_down_page(driver):
    # Scroll down the page to load more articles
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)  # Wait for some time to load more articles

def scrape_search_results(search_url):
    # Use Selenium to interact with the page
    driver = webdriver.Chrome()  # Replace with the path to your Chrome driver executable
    driver.get(search_url)

    # Scroll down the page multiple times to load more articles
    for _ in range(10):  # Adjust the number of times to scroll as per your requirement
        scroll_down_page(driver)

    # Get the page source after scrolling to get all the loaded articles
    page_source = driver.page_source
    driver.quit()

    # Continue with BeautifulSoup as before
    soup = BeautifulSoup(page_source, 'html.parser')
    results_container = soup.find('div', class_='search_results row')
    if not results_container:
        print("No search results found")
        return []

    articles_info = []
    articles = results_container.find_all('div', class_='overlay card')
    for article in articles:
        link = article.find('a', class_='stretched-link')
        if link:
            article_url = link['href']
            articles_info.append(article_url)

    return articles_info

def scrape_comments_for_articles(articles_info):
    all_comments = []

    for article_url in articles_info:
        comments = scrape_comments(article_url)

        if comments:
            all_comments.extend(comments)

    return all_comments

# Set the page number you want to scrape, for example, 1
page_number = 1
search_url = 'https://www.hespress.com/?s=covid'  # Update with the search URL you want

# Scrape the list of articles
articles_info = scrape_search_results(search_url)

# Scrape comments for all articles in the list
all_comments = scrape_comments_for_articles(articles_info)

# Convert the list of dictionaries to a DataFrame
df = pd.DataFrame(all_comments)
source_value = "hespress"  # Replace with the desired value
df["source"] = source_value
df.to_excel('hespress.xlsx', index=False)