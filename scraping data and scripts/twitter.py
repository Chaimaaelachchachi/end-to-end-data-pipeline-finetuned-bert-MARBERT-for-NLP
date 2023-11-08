# Necessary libraries are imported
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import openpyxl
# Twitter username, password, search keyword, and number of tweets to be scraped are assigned to variables
twitter_user = "xxx"
twitter_pass = "xxx"
search_query = "كورونا_المغرب"
tweet_count = 100

# Selenium webdriver is started and the login process is performed on Twitter
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 30)

driver.get("https://twitter.com/login")

username_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
username_input.send_keys(twitter_user)
next_button = driver.find_element(By.CSS_SELECTOR, "div[data-testid='apple_sign_in_button'] + div + div + div[role='button']")
next_button.click()

password_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
password_input.send_keys(twitter_pass)
login_button = driver.find_element(By.CSS_SELECTOR, "div[data-testid='LoginForm_Footer_Container'] div[role='button']")
login_button.click()

# Navigates to Twitter search page and starts scraping tweets
wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[data-testid='sidebarColumn']")))

#driver.get(f"https://twitter.com/search?q={search_query}%20lang%3Aen%20-filter%3Alinks&src=typed_query&f=live")
driver.get(f"https://twitter.com/search?q=%23{search_query}%20lang%3Aar%20since%3A2020-01-01%20until%3A2021-01-31%20-filter%3Alinks&src=typed_query&f=live")
#driver.get(f"https://twitter.com/search?q={search_query}&src=typed_query&f=live")
wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "article[data-testid='tweet']")))

tweets_list = []
dates_list = []
def get_tweets():
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    for tweet in soup.findAll("article", {"data-testid": "tweet"}):
        tweet_text = tweet.find("div", {"data-testid": "tweetText"})
        if tweet_text is not None and search_query in tweet_text.text.lower():
            tweets_list.append(tweet_text.text.strip())
            # Extract the date information
            date_element = tweet.find("time")
            if date_element is not None and "datetime" in date_element.attrs:
                date_string = date_element["datetime"]
                dt = datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
                formatted_date = dt.strftime("%Y-%m-%d") #%H:%M")
                dates_list.append(formatted_date)
get_tweets()

# Scrolls down the page to load more tweets
last_height = driver.execute_script("return document.body.scrollHeight")
while len(tweets_list) < tweet_count:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div[role='progressbar']")))
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "div[role='progressbar']")))

    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
    get_tweets()

# Selenium is closed and the scraped tweets are transferred to a pandas dataframe
driver.quit()
tweets = pd.DataFrame({'date': dates_list,'Text': tweets_list})
source_value = "twitter"  # Replace with the desired value
tweets["source"] = source_value
tweets.to_excel('tweets.xlsx', index=False)