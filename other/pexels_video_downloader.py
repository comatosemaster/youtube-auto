import requests
import os

PEXELS_API_KEY = "oBEjuM354ReDaJm3ZTr4Apa3apwXGuskRA5ivdaGJpq3CiLNy2fJAAA9"
DOWNLOAD_FOLDER = "assets"

def download_video_by_topic(topic):
    headers = {
        "Authorization": PEXELS_API_KEY
    }

    params = {
        "query": topic,
        "per_page": 1
    }

    response = requests.get(
        "https://api.pexels.com/videos/search",
        headers=headers,
        params=params
    )

    if response.status_code != 200:
        print("Error fetching video:", response.text)
        return

    data = response.json()

    if not data["videos"]:
        print("No videos found for this topic.")
        return

    video = data["videos"][0]

    # Pick highest quality file
    video_files = video["video_files"]
    best_file = max(video_files, key=lambda x: x["width"])

    video_url = best_file["link"]

    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_FOLDER, f"{topic.replace(' ', '_')}.mp4")

    print("Downloading video...")

    video_data = requests.get(video_url)

    with open(file_path, "wb") as f:
        f.write(video_data.content)

    print("Saved to:", file_path)


if __name__ == "__main__":
    topic = input("Enter topic: ")
    download_video_by_topic(topic)
