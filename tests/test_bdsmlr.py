import unittest
import requests

class TestFunctionality(unittest.TestCase):
    def setUp(self):
        self.url = "http://172.19.0.2:8888"

    def test_add_blog(self):
        resp = requests.post(
            "%s/add-blog" % self.url,
            data={"blog" : "https://dankp0rn.bdsmlr.com/"}
        )
        self.assertTrue(resp.status_code == 200)

    def test_delete_blog(self):
        pass
    
    def test_get_blogs(self):
        pass

    def test_get_env(self):
        pass

    def test_ping(self):
        pass

if __name__ == "__main__":
    unittest.main()
