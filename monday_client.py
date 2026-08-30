import os
import requests

class MondayClient:
    def __init__(self):
        self.api_key = os.environ.get("MONDAY_API_TOKEN")
        if not self.api_key:
            raise ValueError("MONDAY_API_TOKEN environment variable is not set.")
        
        self.headers = {
            "Authorization": self.api_key,
            "API-Version": "2024-01",
            "Content-Type": "application/json"
        }
        self.url = "https://api.monday.com/v2"

    def fetch_board_data(self, board_id: int) -> list[dict]:
        # Upgraded query to fetch column titles and map them automatically
        query = """
        query($boardId: [ID!], $cursor: String) {
          boards(ids: $boardId) {
            columns {
              id
              title
            }
            items_page(limit: 100, cursor: $cursor) {
              cursor
              items {
                id
                name
                column_values {
                  id
                  text
                }
              }
            }
          }
        }
        """
        
        all_items = []
        cursor = None
        
        while True:
            variables = {"boardId": [board_id]}
            if cursor:
                variables["cursor"] = cursor
                
            payload = {"query": query, "variables": variables}
            response = requests.post(self.url, json=payload, headers=self.headers)
            
            if response.status_code != 200:
                raise Exception(f"Monday API Error {response.status_code}: {response.text}")
                
            data = response.json()
            if "errors" in data:
                raise Exception(f"GraphQL Error: {data['errors']}")
                
            boards_response = data.get("data", {}).get("boards", [])
            if not boards_response or boards_response[0] is None:
                raise Exception(f"Board ID {board_id} not found or you lack permission to view it.")
                
            board_info = boards_response[0]
            
            # Map Monday's internal column IDs to their human-readable CSV titles
            col_map = {col["id"]: col["title"] for col in board_info.get("columns", [])}
            
            board_data = board_info["items_page"]
            items = board_data["items"]
            
            for item in items:
                row = {"item_id": item["id"], "item_name": item["name"]}
                for col in item["column_values"]:
                    col_id = col["id"]
                    col_title = col_map.get(col_id, col_id) # Default to ID if title is missing
                    row[col_title] = col.get("text", "") 
                all_items.append(row)
                
            cursor = board_data.get("cursor")
            if not cursor:
                break
                
        return all_items