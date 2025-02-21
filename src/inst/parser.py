from abc import ABC, abstractmethod
import json
import os
from typing import Any, Dict, List, Optional

import requests

from .types import MediaType, InstException, Media, Post, Story


class InterfaceInstParser(ABC):
    default_timeout = 45

    @abstractmethod
    def get_user_id(self, username: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_user_stories(self, user_id: str) -> List[Story]:
        raise NotImplementedError

    @abstractmethod
    def get_user_posts(self, user_id: str, count: int = 10) -> List[Post]:
        raise NotImplementedError


class InstParser(InterfaceInstParser):
    def __init__(
        self,
        cookies: Optional[Dict[str, str]] = None,
        headers: Optional[Dict[str, str]] = None,
        proxy: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        self._is_logged: bool = False
        self.set_cookies(cookies or {})
        self.set_headers(headers or {})
        self._proxies: Optional[Dict[str, str]] = None
        if proxy:
            self.set_proxy(proxy)
        self._timeout = timeout or self.default_timeout

    @property
    def is_logged(self) -> bool:
        return self._is_logged

    def set_proxy(self, proxy: str) -> None:
        self._proxies = {"http": proxy, "https": proxy}

    def set_headers(self, headers: Dict[str, str]) -> None:
        self._headers = headers

    def set_cookies(self, cookies: Dict[str, str]) -> None:
        self._cookies = cookies

    def set_timeout(self, timeout: int) -> None:
        self._timeout = timeout

    def login_from_file(self, filename: str) -> None:
        if not os.path.exists(filename):
            raise FileNotFoundError("File not found")

        with open(filename, "r") as f:
            data = json.load(f)

        self.set_cookies(data.get("cookies"))
        self.set_headers(data.get("headers"))
        self._is_logged = True

    def _request(self, method: str, url: str) -> requests.Response:
        if not self.is_logged:
            raise InstException("Not logged in")

        return requests.api.request(method.upper(), url, cookies=self._cookies,
                                    headers=self._headers, proxies=self._proxies, timeout=self._timeout)
    
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


    def get_user_stories(self, user_id: str) -> List[Story]:
        """Get user stories

        Args:
            user_id (str): User id

        Returns:
            List[Story]: List of stories
        """
        url = f"https://www.instagram.com/api/v1/feed/reels_media/?reel_ids={user_id}"
        response = self._request("GET", url)

        if response.status_code != 200:
            raise InstException(f"Failed to get stories: {response.status_code}, {response.text}")

        data = response.json()
        stories = data.get("reels", {}).get(user_id, {}).get("items", [])
        return [Story(Media(
            type=MediaType.VIDEO.value if "video_versions" in story else MediaType.IMAGE.value,
            url=story["video_versions"][0]["url"] if "video_versions" in story else story["image_versions2"]["candidates"][0]["url"],
        )) for story in stories]

    def get_user_posts(self, user_id: str, count: int = 10) -> List[Dict[str, Any]]:
        """Get user posts

        Args:
            user_id (str): User id
            count (int, optional): Count of posts. Defaults to 10.

        Returns:
            List[Post]: List of posts
        """
        url = f"https://www.instagram.com/api/v1/feed/user/{user_id}/?count={count}"
        response = self._request("GET", url)

        if response.status_code != 200:
            raise InstException(f"Failed to get posts: {response.status_code}, {response.text}")

        data = response.json()
        posts = []
        for item in data.get("items", []):
            media_list = []
            if "carousel_media" in item:
                for media in item["carousel_media"]:
                    media_type = MediaType.VIDEO.value if "video_versions" in media else MediaType.IMAGE.value
                    media_url = media.get("video_versions", [{}])[0].get("url") or media.get("image_versions2", {}).get("candidates", [{}])[0].get("url")
                    media_list.append(Media(type=media_type, url=media_url))
            else:
                media_type = MediaType.VIDEO.value if "video_versions" in item else MediaType.IMAGE.value
                media_url = item.get("video_versions", [{}])[0].get("url") or item.get("image_versions2", {}).get("candidates", [{}])[0].get("url")
                media_list.append(Media(type=media_type, url=media_url))

            posts.append(Post(
                media_list=media_list,
                caption=item.get("caption", {}).get("text", ""),
            ))
        return posts
