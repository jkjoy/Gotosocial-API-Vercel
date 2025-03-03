# 项目介绍
获取Gotosocial指定用户的Timeline

# 使用

环境变量

- `HOST`为Gotosocial实例地址
- `USER_ID`为Gotosocial用户ID
- `TOKEN`为`access_token`可通过 https://blog.0tz.top/mastodon-access-token/ 获取 

通过路由 /api 获取到 json 数据

### 获取第一页
GET /api?limit=20

### 获取下一页（使用最后一个条目的ID）
GET /api?limit=20&max_id=01HP3D6Z8Q5X2K4T3R7S9VW0Y

### 获取最新内容（使用已知最新ID）
GET /api?limit=20&since_id=01HP3D7B6T8X4K2R9S1VW0Y
