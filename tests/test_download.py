from tests.base import DotifyBaseTestCase


class DotifyDownloadTestCase(DotifyBaseTestCase):
    def test_download_track(self):
        url = "https://open.spotify.com/track/5G9fgmdZOZFPmb0aEwm5uN"
        self.download("Track", url)

        # Date format is different
        url = "https://open.spotify.com/track/4feXcsElKIVsGwkbnTHAfV?si=0f5061d3d6194533"
        self.download("Track", url)

    def test_download_playlist(self):
        url = "https://open.spotify.com/playlist/1HkE7QDzcdtF3lQGVF744N"
        self.download("Playlist", url)

    def test_download_album(self):
        url = "https://open.spotify.com/album/5WEwObchJdvIzPcmm2e3Li"
        self.download("Album", url)
