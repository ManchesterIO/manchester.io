from flask import render_template
import requests


class SearchResults(object):

    def __init__(self, app):
        self._app = app

    def init(self):
        self._app.add_url_rule('/search/rail-stations/near/<float:lat>,<float:lon>', 'rail-search', self.render)

    def render(self, lat, lon):
        stations = self._fetch_results(lat, lon)
        return render_template('search-results.html',
                               stations=map(self._station_to_template, stations),
                               starting_lat=lat, starting_lon=lon)

    def _fetch_results(self, lat, lon):
        url = 'http://{base_url}/search/rail-stations/near/{lat},{lon}'.format(
            base_url=self._app.config['API_BASE_URL'],
            lat=lat,
            lon=lon
        )
        return requests.get(url, timeout=5).json()

    def _station_to_template(self, station):
        return {}
