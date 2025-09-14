# LiJinTracker
禮金簿

## Python API 開發環境

1. 建立虛擬環境：
   ```bash
   python -m venv venv
   ```

2. 啟動虛擬環境（Windows Bash）：
   ```bash
   source venv/Scripts/activate
   ```

3. 安裝必要套件：
   ```bash
   pip install fastapi sqlalchemy pymysql uvicorn python-dotenv
   ```

4. 複製 `.env.example` 為 `.env` 並填入你的資料庫連線資訊。

5. 啟動 FastAPI 伺服器：
   ```bash
   uvicorn main:app --reload
   ```

## Docker 部署

1. 建立 Docker 映像檔：
   ```bash
   docker build -t lijintracker .
   ```

2. 啟動容器（將 8080 對外映射到容器 8000）：
   ```bash
   docker run -d -p 8080:8000 lijintracker
   ```

3. 可在瀏覽器開啟 http://localhost:8080 查看服務。

---

如需自訂環境變數，請將 `.env` 檔案一併複製到容器內。
