from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

# 假設這是一個簡單的資料
data = {
    "id": 1,
    "name": "Example",
    "description": "This is an example data for demonstration."
}

# 提供 JSON 資料的 API
@app.get("/api/data")
async def get_data():
    return data

# 提供 HTML 頁面的 API
@app.get("/", response_class=HTMLResponse)
async def get_html():
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>FastAPI Example</title>
    </head>
    <body>
        <h1>Data from FastAPI</h1>
        <p>ID: {data['id']}</p>
        <p>Name: {data['name']}</p>
        <p>Description: {data['description']}</p>
    </body>
    </html>
    """
    return html_content
