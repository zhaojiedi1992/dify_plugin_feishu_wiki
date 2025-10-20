from typing import Any, Generator

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage
from feishu_api_utils import FeishuRequest


class CreateWikiNodeTool(Tool):
    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        app_id = self.runtime.credentials.get("app_id")
        app_secret = self.runtime.credentials.get("app_secret")
        client = FeishuRequest(app_id, app_secret)
        space_id = tool_parameters.get("space_id")
        parent_node_token = tool_parameters.get("parent_node_token")
        obj_type = tool_parameters.get("obj_type")
        node_type = tool_parameters.get("node_type")
        origin_node_token = tool_parameters.get("origin_node_token")
        title = tool_parameters.get("title")
        print(title)
        print(origin_node_token)
        print(origin_node_token)
        res = client.create_wiki_node(space_id=space_id, parent_node_token=parent_node_token,
                                    title=title, obj_type=obj_type, node_type=node_type,
                                      origin_node_token=origin_node_token)
        yield self.create_json_message(res)
