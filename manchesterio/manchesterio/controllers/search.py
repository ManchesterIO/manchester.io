from flask import render_template


def search_results(lat, lon):
    return render_template('search-results.html',
                           startingLat=lat, startingLon=lon)
