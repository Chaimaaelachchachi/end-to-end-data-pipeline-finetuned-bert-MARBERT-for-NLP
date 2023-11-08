from googleapiclient.discovery import build
from langdetect import detect
from googleapiclient.errors import HttpError
import pandas as pd
import re
from datetime import datetime
# Set your YouTube Data API key here
DEVELOPER_KEY = "xxx"

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# Initialize the YouTube Data API client
youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)

def get_comments(video_id, max_comments=10):
    comments_data = []
    try:
        # Get comments for the specified video
        response = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=max_comments
        ).execute()

        # Extract and store the comments and their upload dates
        for comment in response.get("items", []):
            comment_text = comment["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
            comment_date = comment["snippet"]["topLevelComment"]["snippet"]["publishedAt"]
            # Check if the comment is in Arabic
            clean_comment = re.sub(r'[^\w\s]', '', comment_text)
            if len(clean_comment) >= 3:
                # Check if the cleaned comment is in Arabic
                if detect(clean_comment) == "ar":
                    formatted_date = datetime.strptime(comment_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
                    comments_data.append({"date": formatted_date, "Text": comment_text})

    except HttpError as e:
        print("An HTTP error occurred:", e)

    return comments_data

def search_and_scrape(query, max_videos=5, max_comments_per_video=5):
    try:
        # Search for videos based on the query
        search_response = youtube.search().list(
            q=query,
            part="id",
            maxResults=max_videos
        ).execute()

        comments_data = []

        # Extract and process video IDs from the search results
        for search_result in search_response.get("items", []):
            video_id = search_result["id"]["videoId"]
            
            # Call the function to scrape comments and dates for the current video
            video_comments = get_comments(video_id, max_comments=max_comments_per_video)
            
            # Extend the list of comments_data with the new comments
            comments_data.extend(video_comments)

        # Create a DataFrame from the collected comments data
        comments_df = pd.DataFrame(comments_data, columns=["date", "Text"])
    except HttpError as e:
        print("An HTTP error occurred:", e)

    return comments_df

# Specify your search query and limits here
search_query = "كورونا المغرب"
max_videos_to_search = 5
max_comments_per_video = 50

# Call the function to search, scrape comments, and store results in a DataFrame
comments_dataframe = search_and_scrape(search_query, max_videos=max_videos_to_search, max_comments_per_video=max_comments_per_video)
source_value = "YouTube"  # Replace with the desired value
comments_dataframe["source"] = source_value
comments_dataframe.to_excel('youtube.xlsx', index=False)