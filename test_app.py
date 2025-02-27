import unittest
from app import app, load_tracks

class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        load_tracks()

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MP3 Streamer', response.data)

    def test_get_tracks(self):
        response = self.app.get('/tracks')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        self.assertIsInstance(response.json, list)

    def test_stream(self):
        response = self.app.get('/stream/test.mp3')
        self.assertEqual(response.status_code, 404)  # Assuming 'test.mp3' does not exist

    def test_cover(self):
        response = self.app.get('/cover/test.mp3')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'image/jpeg')

    def test_shuffle_tracks(self):
        response = self.app.post('/shuffle')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json)
        self.assertIsInstance(response.json, list)

if __name__ == '__main__':
    unittest.main()