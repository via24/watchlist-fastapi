import unittest

import bcrypt
from fastapi.testclient import TestClient

from watchlist.config import settings

settings.database_url = "sqlite+pysqlite:///./test.db"

from watchlist.database import Base, engine, SessionLocal
from watchlist.models import User, Movie
from watchlist.main import app


class WatchlistTestCase(unittest.TestCase):
    def setUp(self):
        # 更新配置

        # 创建数据库和表
        Base.metadata.create_all(engine)
        # 创建测试数据，一个用户，一个电影条目
        with SessionLocal() as session:
            pwd = bcrypt.hashpw(b"123", bcrypt.gensalt(13))
            user = User(name="Test", email="test@123.com", hashed_password=pwd.decode())
            movie = Movie(title="Test Movie Title", year="2019")
            # 使用 add_all() 方法一次添加多个模型类实例，传入列表
            session.add_all([user, movie])
            session.commit()

        self.client = TestClient(app)  # 创建测试客户端

    def tearDown(self):
        # 删除数据库表
        Base.metadata.drop_all(engine)

    # 测试程序实例是否存在
    def test_app_exist(self):
        self.assertIsNotNone(app)

    def test_404_page(self):
        response = self.client.get("/nothing")  # 传入目标 URL
        data = response.text
        self.assertIn("Page Not Found - 404", data)
        self.assertIn("Go Back", data)
        self.assertEqual(response.status_code, 404)  # 判断响应状态码

    # 测试主页
    def test_index_page(self):
        response = self.client.get("/")
        data = response.text
        self.assertIn("Test's Watchlist", data)
        self.assertIn("Test Movie Title", data)
        self.assertEqual(response.status_code, 200)

    def login(self):
        self.client.post(
            "/login",
            data=dict(username="test@123.com", password="123"),
            follow_redirects=True,
        )

    def test_create_item(self):
        self.login()
        # 测试创建条目操作
        response = self.client.post(
            "/", data=dict(title="New Movie", year="2019"), follow_redirects=True
        )
        data = response.text
        self.assertIn("Item created.", data)
        self.assertIn("New Movie", data)

        # 测试创建条目操作，但电影标题为空
        response = self.client.post(
            "/", data=dict(title="", year="2019"), follow_redirects=True
        )
        data = response.text
        self.assertNotIn("Item created.", data)
        self.assertIn("Invalid input.", data)

        # 测试创建条目操作，但电影年份为空
        response = self.client.post(
            "/", data=dict(title="New Movie", year=""), follow_redirects=True
        )
        data = response.text
        self.assertNotIn("Item created.", data)
        self.assertIn("Invalid input.", data)

    # 测试更新条目
    def test_update_item(self):
        self.login()
        # 测试更新页面
        response = self.client.get("/movies/edit/1")
        data = response.text
        self.assertIn("Edit item", data)
        self.assertIn("Test Movie Title", data)
        self.assertIn("2019", data)

        # 测试更新条目操作
        response = self.client.post(
            "/movies/edit/1",
            data=dict(title="New Movie Edited", year="2019"),
            follow_redirects=True,
        )
        data = response.text
        self.assertIn("Item updated.", data)
        self.assertIn("New Movie Edited", data)

        # 测试更新条目操作，但电影标题为空
        response = self.client.post(
            "/movies/edit/1", data=dict(title="", year="2019"), follow_redirects=True
        )
        data = response.text
        self.assertNotIn("Item updated.", data)
        self.assertIn("Invalid input.", data)

        # 测试更新条目操作，但电影年份为空
        response = self.client.post(
            "/movies/edit/1",
            data=dict(title="New Movie Edited Again", year=""),
            follow_redirects=True,
        )
        data = response.text
        self.assertNotIn("Item updated.", data)
        self.assertNotIn("New Movie Edited Again", data)
        self.assertIn("Invalid input.", data)

    # 测试删除条目
    def test_delete_item(self):
        self.login()
        response = self.client.post("/movies/drop/1", follow_redirects=True)
        data = response.text
        # self.assertIn("Item deleted.", data)
        self.assertNotIn("Test Movie Title", data)

    # 测试登录保护
    def test_login_protect(self):
        response = self.client.get("/")
        data = response.text
        self.assertNotIn("Logout", data)
        self.assertNotIn("Settings", data)
        self.assertNotIn('<form method="post">', data)
        self.assertNotIn("Delete", data)
        self.assertNotIn("Edit", data)

    # 测试登录
    def test_login(self):
        response = self.client.post(
            "/login",
            data=dict(username="test@123.com", password="123"),
            follow_redirects=True,
        )
        data = response.text
        # self.assertIn("Login success.", data)
        self.assertIn("Logout", data)
        self.assertIn("Settings", data)
        self.assertIn("Delete", data)
        self.assertIn("Edit", data)
        self.assertIn('<form method="post">', data)

        # 测试使用错误的密码登录
        response = self.client.post(
            "/login", data=dict(username="test", password="456"), follow_redirects=True
        )
        data = response.text
        self.assertNotIn("Login success.", data)
        self.assertIn("Invalid username or password.", data)

        # 测试使用错误的用户名登录
        response = self.client.post(
            "/login", data=dict(username="wrong", password="123"), follow_redirects=True
        )
        data = response.text
        self.assertNotIn("Login success.", data)
        self.assertIn("Invalid username or password.", data)

        # 测试使用空用户名登录
        response = self.client.post(
            "/login", data=dict(username="", password="123"), follow_redirects=True
        )
        data = response.text
        self.assertNotIn("Login success.", data)
        self.assertIn("field required", data)

        # 测试使用空密码登录
        response = self.client.post(
            "/login", data=dict(username="test", password=""), follow_redirects=True
        )
        data = response.text
        self.assertNotIn("Login success.", data)
        self.assertIn("field required", data)

    # 测试登出
    def test_logout(self):
        self.login()

        response = self.client.get("/logout", follow_redirects=True)
        data = response.text
        # self.assertIn("Goodbye.", data)
        self.assertNotIn("Logout", data)
        self.assertNotIn("Settings", data)
        self.assertNotIn("Delete", data)
        self.assertNotIn("Edit", data)
        self.assertNotIn('<form method="post">', data)

    # 测试设置
    def test_settings(self):
        self.login()

        # 测试设置页面
        response = self.client.get("/settings")
        data = response.text
        self.assertIn("Settings", data)
        self.assertIn("Your Name", data)

        # 测试更新设置
        response = self.client.post(
            "/settings", data=dict(name="Grey Li"), follow_redirects=True
        )
        data = response.text
        self.assertIn("Settings updated.", data)
        self.assertIn("Grey Li", data)

        # 测试更新设置，名称为空
        response = self.client.post(
            "/settings", data=dict(name=""), follow_redirects=True
        )
        data = response.text
        self.assertNotIn("Settings updated.", data)
        self.assertIn("Invalid input.", data)
