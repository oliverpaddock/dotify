import html
from pprint import pprint
from re import sub

import click
from cli.types import URL
from cli.ui import echo_dictionary
from cli.views.root import root
from dotify import Album


@root.group()
@click.pass_context
def album(ctx):
    """Actions on Albums"""


@album.command()
@click.argument('query', type=click.STRING)
@click.option(
    '-l', '--limit',
    default=1, show_default=True,
    type=click.INT, help='search result limit'
)
@click.option(
    '-r', '--raw',
    default=False, show_default=True,
    is_flag=True, help='output a dictionary'
)
@click.pass_obj
def search(client, query, limit, raw):
    """Search for an Album"""

    results = client.Album.search(query, limit=limit)

    for result in results:
        result = {
            "url": result.url,
            "name": html.unescape(result.name.strip()),
            "artist": {
                "name": html.unescape(result.artist.name).strip(),
                "url": result.artist.url,
            },
            "images": result.images
        }

        echo_dictionary(result) if not raw else pprint(result, indent=4)


@album.command()
@click.argument('url', type=URL)
@click.pass_obj
def download(client, url):
    """Download an Album"""

    album = client.Album.from_url(url)

    artist, name = album.artist.name, album.name
    artist, name = artist.strip(), name.strip()
    artist, name = sub(r'\s+', ' ', artist), sub(r'\s+', ' ', name)

    album.download(f'{artist} - {name}')
