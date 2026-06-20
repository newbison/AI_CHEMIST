# Zeabur 部署使用方式：
# 1. 在 Zeabur 创建项目，选择「从 GitHub 导入」
# 2. 选择此仓库
# 3. 服务类型选择「Web 服务」
# 4. 根目录设置为 webapp/backend
# 5. 构建命令留空（使用默认 pip install -r requirements.txt）
# 6. 启动命令: uvicorn main:app --host 0.0.0.0 --port $PORT
# 7. 环境变量中设置 DEEPSEEK_API_KEY
# 8. 前端静态资源需要额外添加一个「静态网站」服务，根目录设为 webapp/frontend，
#    构建命令: npm install && npm run build
#    输出目录: dist
#    并将 /api 请求转发到后端服务的域名
