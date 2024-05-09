import time

start = time.time()
import contextlib
end = time.time()
print('20', end-start)
start = end
import logging
end = time.time()
print('21', end-start)
start = end
from functools import wraps
end = time.time()
print('22', end-start)
start = end
from http import HTTPStatus
end = time.time()
print('23', end-start)
start = end
from importlib import import_module
end = time.time()
print('24', end-start)
start = end
from pathlib import Path
end = time.time()
print('25', end-start)
start = end
from re import match
end = time.time()
print('26', end-start)
start = end
from typing import Any, AnyStr, Callable, Iterator, Optional, cast
end = time.time()
print('27', end-start)
start = end

from spotipy.exceptions import SpotifyException
end = time.time()
print('28', end-start)
start = end

from dotify._decorators import cached_classproperty
end = time.time()
print('29', end-start)
start = end
from dotify._dotify import Dotify
end = time.time()
print('30', end-start)
start = end
from dotify._json_serializable import JsonSerializable, JsonSerializableMeta, logger
end = time.time()
print('31', end-start)
start = end

logger = logging.getLogger("{0}.{1}".format(logger.name, __name__))


class ModelMeta(JsonSerializableMeta):
    """A class handling any model metadata.

    A metaclass serving as an abstraction layer over
    the `JsonSerializableMeta` metaclass, that automatically
    resolves the path to the `Model`'s JSON schema, as well as
    builds the `dependency` dictionary
    """

    def __new__(cls, name, bases, attrs):  # noqa: D102
        try:
            json_meta = attrs["Json"]
        except KeyError:
            json_meta = type("Json", (object,), {})

        is_abstract = False
        with contextlib.suppress(AttributeError):
            is_abstract = json_meta.abstract

        if not is_abstract:
            json_meta.schema = cls._dependency_path(name)

            with contextlib.suppress(AttributeError):
                json_meta.dependencies = cls._dependencies_from(
                    json_meta.dependencies,
                )

        attrs["Json"] = json_meta

        return super().__new__(cls, name, bases, attrs)

    @classmethod
    def _dependency_basename(cls, model_name: str) -> str:
        """Given the name of a `Model` resolve the basename of the corresponding json schema.

        Args:
            model_name (str): the name of a `Model`

        Returns:
            str: the basename of the file containing the json schema
        """
        return "{0}.json".format(
            model_name.lower(),
        )

    @classmethod
    def _dependency_path(cls, model_name: str) -> Path:
        """Given the name of a `Model` resolve the path to the corresponding json schema.

        Args:
            model_name (str): the name of a `Model`

        Returns:
            Path: the path to the file containing the json schema
        """
        return Path(__file__).parent / "models" / "schema" / cls._dependency_basename(model_name)

    @classmethod
    def _dependencies_from(cls, dependency_names):
        @cached_classproperty
        def decorator(_):
            model_types = []
            for dependency_name in dependency_names:
                module, _, model_type = dependency_name.rpartition(".")

                module = import_module(module)
                model_type = getattr(module, model_type)

                model_types.append(model_type)

            return {
                cls._dependency_basename(model_type.__name__): model_type
                for model_type in model_types
            }

        return decorator


class Model(JsonSerializable, metaclass=ModelMeta):
    """The base class for every Spotify Web API entity."""

    class Json(object):
        abstract = True

    class UnexpectedError(Exception):
        """An exception indicating an unexpected error."""

    class InvalidURL(Exception):
        """An exception thrown if the provided URL does not correspond to a valid Spotify URL."""

    class NotFound(Exception):
        """An exception thrown if an operation fails to retrieve the necessary information."""

    def __repr__(self):
        return '<{0} "{1}">'.format(self.__class__.__name__, str(self))

    @cached_classproperty
    def context(cls) -> Optional[Dotify]:  # noqa: N805
        """Get the current `Dotify` context.

        Returns:
            Optional[Dotify]: the current `Dotify` context
        """
        return cast(Dotify, Dotify.context)

    @classmethod
    def view_name(cls) -> str:
        """Return the name of the Spotify view corresponding to the `Model`.

        Returns:
            str: the name of the Spotify view
        """
        return cls.__name__.lower()

    @classmethod
    def search(cls, query: AnyStr, limit: Optional[int] = 1) -> Iterator["Model"]:
        """Perform a Spotify search given a `query`.

        Args:
            query (AnyStr): the search `query`
            limit (Optional[int]): the number of items to return. Defaults to 1.

        Raises:
            NotFound: In case no results corresponding to the provided query are found

        Returns:
            Iterator["Model"]: the `Model` instances corresponding to the query
        """
        view_name = cls.view_name()

        results = cls.context.search(view_name, query, limit=limit)

        if not results:
            raise cls.NotFound

        return map(lambda kwargs: cls(**kwargs), results)

    @classmethod
    def validate_url(cls, method: Callable[..., Any]) -> Callable[..., Any]:
        """Validate the `URL` supplied to the decorated method.

        Args:
            method (Callable[..., Any]): the method being decorated

        Returns:
            Callable[..., Any]: the  decorated method
        """

        @wraps(method)
        def wrapper(model_type, url, *args, **kwargs):
            view_name = model_type.view_name()
            pattern = "https://open.spotify.com/{0}".format(
                view_name,
            )

            if match(pattern, url) is None:
                raise model_type.InvalidURL from None

            return method(model_type, url, *args, **kwargs)

        return wrapper

    @classmethod
    def http_safeguard(cls, method: Callable[..., Any]) -> Callable[..., Any]:
        """Convert HTTP exceptions thrown by the decorated method to `Model` level exceptions.

        Args:
            method (Callable[..., Any]): the method being decorated

        Returns:
            Callable[..., Any]: the decorated method
        """

        @wraps(method)
        def wrapper(model_type, *args, **kwargs):
            try:
                return method(model_type, *args, **kwargs)
            except SpotifyException as exception:
                if exception.http_status == HTTPStatus.NOT_FOUND.value:
                    raise model_type.NotFound from None
                elif exception.http_status == HTTPStatus.BAD_REQUEST.value:
                    raise model_type.InvalidURL from None

                raise model_type.UnexpectedError from None

        return wrapper
