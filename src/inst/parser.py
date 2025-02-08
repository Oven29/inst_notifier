from abc import ABC, abstractmethod
import json
import os
from typing import Any, Dict, List, Optional

import requests


class InstException(Exception):
    """Base class for exceptions in this module."""


class InterfaceInstParser(ABC):
    @abstractmethod
    def get_user_id(self, username: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_user_stories(self, user_id: str) -> List[str]:
        raise NotImplementedError

    @abstractmethod
    def get_user_posts(self, user_id: str, count: int = 10) -> List[Dict[str, Any]]:
        raise NotImplementedError


class InstParser(InterfaceInstParser):
    def __init__(
        self,
        cookies: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        proxy: Optional[str] = None,
    ) -> None:
        self._is_logged: bool = False
        self.set_cookies(cookies or {})
        self.set_headers(headers or {})
        self._proxies: Optional[Dict[str, str]] = None
        if proxy:
            self.set_proxy(proxy)

    @property
    def is_logged(self) -> bool:
        return self._is_logged

    def set_proxy(self, proxy: str) -> None:
        self._proxies = {"http": proxy, "https": proxy}

    def set_headers(self, headers: Dict[str, str]) -> None:
        self._headers = headers

    def set_cookies(self, cookies: Dict[str, str]) -> None:
        self._cookies = cookies

    def login_from_file(self, filename: str) -> None:
        if not os.path.exists(filename):
            raise FileNotFoundError("File not found")

        with open(filename, "r") as f:
            data = json.load(f)

        self.set_cookies(data.get("cookies"))
        self.set_headers(data.get("headers"))
        self._is_logged = True

    def _request(self, method: str, url: str) -> Any:
        if not self.is_logged:
            raise InstException("Not logged in")

        return requests.api.request(method.upper(), url, cookies=self._cookies, headers=self._headers, proxies=self._proxies)
    
    def get_user_id(self, username: str) -> str:
        """Get user id

        Args:
            username (str): Username

        Returns:
            str: User id
        """
        url = f"https://www.instagram.com/api/v1/users/web_profile_info/?username={username}"
        response = self._request("GET", url)

        if response.status_code != 200:
            raise InstException(f"Failed to get user ID: {response.status_code}, {response.text}")

        data = response.json()
        return data["data"]["user"]["id"]


    def get_user_stories(self, user_id: str) -> List[str]:
        """Get user stories

        Args:
            user_id (str): User id

        Returns:
            List[str]: List of urls on stories
        """
        url = f"https://www.instagram.com/api/v1/feed/reels_media/?reel_ids={user_id}"
        response = self._request("GET", url)

        if response.status_code != 200:
            raise InstException(f"Failed to get stories: {response.status_code}, {response.text}")

        data = response.json()
        stories = data.get("reels", {}).get(user_id, {}).get("items", [])
        return [story["video_versions"][0]["url"] if "video_versions" in story else story["image_versions2"]["candidates"][0]["url"] for story in stories]

    def get_user_posts(self, user_id: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get user posts

        Args:
            user_id (str): User id
            count (int, optional): Count of posts. Defaults to 10.

        Returns:
            List[Dict[str, Any]]: List of posts

        Types:
            Post = {
                "media": List[str],
                "caption": str
            }
        """
        url = f"https://www.instagram.com/api/v1/feed/user/{user_id}/?count={count}"
        response = self._request("GET", url)

        if response.status_code != 200:
            raise InstException(f"Failed to get posts: {response.status_code}, {response.text}")

        data = response.json()
        posts = []
        for item in data.get("items", []):
            media_urls = []
            if "carousel_media" in item:
                for media in item["carousel_media"]:
                    media_urls.append(media.get("video_versions", [{}])[0].get("url") or media.get("image_versions2", {}).get("candidates", [{}])[0].get("url"))
            else:
                media_urls.append(item.get("video_versions", [{}])[0].get("url") or item.get("image_versions2", {}).get("candidates", [{}])[0].get("url"))
            posts.append({
                "media": media_urls,
                "caption": item.get("caption", {}).get("text", "")
            })
        return posts
