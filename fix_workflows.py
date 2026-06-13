import json
import os

WORKFLOWS_DIR = "n8n/workflows"
URL_MAPPINGS = {
    "http://localhost:8000": "http://localhost:8005",
    "http://host.docker.internal:8000": "http://host.docker.internal:8005"
}

def transform_supabase_to_postgres(node):
    params = node.get("parameters", {})
    url = params.get("url", "")
    if not isinstance(url, str) or "/rest/v1/" not in url:
        return node

    table = url.split("/rest/v1/")[-1].split("?")[0]
    method = params.get("method", "GET").upper()
    
    new_node = {
        "id": node["id"],
        "name": node["name"].replace("Supabase", "Postgres"),
        "type": "n8n-nodes-base.postgres",
        "typeVersion": 2,
        "position": node["position"],
        "parameters": {
            "operation": "executeQuery",
            "connection": "postgres_local",
        }
    }

    if method == "POST":
        new_node["parameters"]["query"] = f"-- Insert into {table}\nINSERT INTO {table} SELECT * FROM json_populate_record(NULL:: {table}, {{ $json }});"
    elif method == "GET":
        query = f"SELECT * FROM {table}"
        if "status=eq." in url:
            status = url.split("status=eq.")[1].split("&")[0]
            query += f" WHERE status = '{status}'"
        if "order=" in url:
            order = url.split("order=")[1].split("&")[0].replace(".", "_")
            query += f" ORDER BY {order}"
        if "limit=" in url:
            limit = url.split("limit=")[1].split("&")[0]
            query += f" LIMIT {limit}"
        new_node["parameters"]["query"] = query

    return new_node

def fix_workflow(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    modified = False
    new_nodes = []
    for node in data.get("nodes", []):
        params = node.get("parameters", {})
        if "url" in params and isinstance(params["url"], str):
            for old, new in URL_MAPPINGS.items():
                if old in params["url"]:
                    params["url"] = params["url"].replace(old, new)
                    modified = True
        
        if node.get("type") == "n8n-nodes-base.httpRequest":
            url = params.get("url", "")
            if isinstance(url, str) and "/rest/v1/" in url:
                node = transform_supabase_to_postgres(node)
                modified = True
        
        new_nodes.append(node)
    
    data["nodes"] = new_nodes
    
    if modified:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"Fixed {file_path}")

if __name__ == "__main__":
    for file in os.listdir(WORKFLOWS_DIR):
        if file.endswith(".json"):
            fix_workflow(os.path.join(WORKFLOWS_DIR, file))
