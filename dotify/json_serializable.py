import json
from abc import ABCMeta
from pathlib import Path
from re import fullmatch

from python_jsonschema_objects import ObjectBuilder
from python_jsonschema_objects.classbuilder import LiteralValue, ProtocolBase
from python_jsonschema_objects.validators import ValidationError
from python_jsonschema_objects.wrapper_types import ArrayWrapper


class JsonSerializableMeta(ABCMeta):
    def __new__(cls, name, bases, attrs):
        if 'Json' not in attrs:
            return super().__new__(cls, name, bases, attrs)

        Json = attrs['Json']
        if hasattr(Json, 'schema'):
            path = Json.schema.absolute()
            with path.open() as file:
                json_schema = json.load(file)

                resolver = None
                if hasattr(Json, 'resolver'):
                    resolver = Json.resolver(f'{path}', json_schema)

                builder = ObjectBuilder(f'{path}', resolver=resolver)

                classes = builder.build_classes(
                    strict=True,
                    named_only=True,
                    standardize_names=False
                )

                json_schema = getattr(classes, name)

            return super().__new__(cls, name, (*bases, json_schema), attrs)

        return super().__new__(cls, name, bases, attrs)


class JsonSerializable(ProtocolBase, metaclass=JsonSerializableMeta):
    class Json:
        pass

    def __setattr__(self, name, val):
        try:
            super().__setattr__(name, val)
        except ValidationError:
            if hasattr(self, '__annotations__') and name in self.__annotations__:
                self.__dict__[name] = val
            else:
                raise

    def __getattribute__(self, name):
        obj = super().__getattribute__(name)

        if isinstance(obj, LiteralValue):
            return obj._value
        if isinstance(obj, ArrayWrapper):
            return obj.data
        if isinstance(obj, ProtocolBase):
            if hasattr(self.Json, 'dependencies'):
                name = obj.__class__.__name__
                for dependency in self.Json.dependencies:
                    _name = dependency.__name__
                    _name = f'{_name}.json'.lower()
                    if name == _name:
                        return dependency(**obj.as_dict())

            return obj

        return obj

    def __getattr__(self, name):
        if name in self.__prop_names__:
            return self._properties[name]
        if name in self._extended_properties:
            return self._extended_properties[name]

        return object.__getattribute__(self, name)