from config import GRSAI_API_KEY, GRSAI_URL_RESULT
import requests
import time
import json



def extract_image_urls_from_response(task_id):
    while True:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer " + GRSAI_API_KEY,
        }
        #print(task_id)
        data = requests.post(
                GRSAI_URL_RESULT,
                headers=headers,
                json={"id": task_id},
                ).json()["data"]
        #  3. 提取 URL
        #print("data:", data)
        if data is not None:
            if data["status"] == "succeeded":
                return data["results"][0]["url"]
            if data["status"] == "failed":
                print("❌ 任务失败:", data)
                return None
        time.sleep(30)