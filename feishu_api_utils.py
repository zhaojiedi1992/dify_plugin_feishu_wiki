import json
from typing import Any, Optional, cast

import httpx

from dify_plugin.errors.tool import ToolProviderCredentialValidationError


def auth(credentials):
    app_id = credentials.get("app_id")
    app_secret = credentials.get("app_secret")
    if not app_id or not app_secret:
        raise ToolProviderCredentialValidationError("app_id and app_secret is required")
    try:
        assert FeishuRequest(app_id, app_secret).tenant_access_token is not None
    except Exception as e:
        raise ToolProviderCredentialValidationError(str(e))



class FeishuRequest:
    API_BASE_URL = "https://open.feishu.cn/open-apis/"
    API_BASE_URL_WIKI= "https://open.feishu.cn/open-apis"

    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret

    @property
    def tenant_access_token(self):
        res = self.get_tenant_access_token(self.app_id, self.app_secret)
        return res.get("tenant_access_token")

    def _send_request(
        self,
        url: str,
        method: str = "post",
        require_token: bool = True,
        payload: Optional[dict] = None,
        params: Optional[dict] = None,
    ):
        headers = {
            "Content-Type": "application/json",
            "user-agent": "Dify",
        }
        if require_token:
            headers["tenant-access-token"] = f"{self.tenant_access_token}"
            headers["Authorization"] = f"Bearer {self.tenant_access_token}"
        res = httpx.request(method=method, url=url, headers=headers, json=payload, params=params, timeout=30).json()
        if res.get("code") != 0:
            raise Exception(res)
        return res

    def get_tenant_access_token(self, app_id: str, app_secret: str) -> dict:
        """
        refer: https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal
        API url: https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal
        Example Response:
        {
            "code": 0,
            "msg": "ok",
            "tenant_access_token": "t-caecc734c2e3328a62489fe0648c4b98779515d3",
            "expire": 7200
        }
        """
        url = f"{self.API_BASE_URL}/auth/v3/tenant_access_token/internal"
        payload = {"app_id": app_id, "app_secret": app_secret}
        res: dict = self._send_request(url, require_token=False, payload=payload)
        print("access token:", res["tenant_access_token"])
        print(res)
        return res


    def get_wiki_nodes(self, space_id: str, parent_node_token: str, page_token: str, page_size: int = 20) -> dict:
        # 获取知识库全部子节点列表
        url = f"{self.API_BASE_URL}wiki/v2/spaces/{space_id}/nodes"
        payload = {
            "space_id": space_id,
            "parent_node_token": parent_node_token,
            "page_token": page_token,
            "page_size": page_size,
        }
        res: dict = self._send_request(url, payload=payload)
        if "data" in res:
            data: dict = res.get("data", {})
            return data
        return res
    def create_wiki_node(self, space_id:str, title: str, parent_node_token:str,
                         obj_type:str ="docx",node_type:str="origin",origin_node_token:str=None) -> dict:
        """
        refer: https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/create?appId=cli_a865d45cdb3d901c
        """
        url = f"{self.API_BASE_URL}/wiki/v2/spaces/{space_id}/nodes"
        payload = {
            "title": title,
            "parent_node_token": parent_node_token,
            "obj_type": obj_type if obj_type else "docx" ,
            "node_type": node_type if node_type else "origin",
            "origin_node_token": origin_node_token,
        }
        print(payload)
        payload = {k: v for k, v in payload.items() if v is not None}
        print(payload)
        res: dict = self._send_request(url, payload=payload)
        print(res)
        if "data" in res:
            data: dict = res.get("data", {})
            node: dict = data.get("node",{})
            return node
        return res

