import logging
import tempfile
from pathlib import Path

from api.api import api
from api.error.errors import BadRequest, InternalServerError, NotFound
from flask import request, send_file
from api.provider import DEFAULT, Spotify, SpotifyException


@api.route("/track", methods=['POST', ])
def track():
    data = request.json

    if data is None or 'uri' not in data:
        raise BadRequest('No track uri')

    try:
        with tempfile.TemporaryDirectory() as tmp:
            with Spotify(output_file=f'{Path(tmp) / DEFAULT["output_file"]}') as spotify:
                path, metadata = spotify.download_track(data['uri'])

                artist, name = metadata["artist"]["name"], metadata["name"]

                attachment_filename = f"{artist} - {name}.mp3"

                logging.info(f'Sending MP3 file {attachment_filename}')

                return send_file(path, as_attachment=True, attachment_filename=attachment_filename)
    except SpotifyException:
        raise NotFound(f'No track corresponding to {data["uri"]}')
    except Exception as e:
        logging.exception(e)
        raise InternalServerError(str(e))