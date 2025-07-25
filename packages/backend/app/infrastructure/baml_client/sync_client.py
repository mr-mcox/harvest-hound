# ----------------------------------------------------------------------------
#
#  Welcome to Baml! To use this generated code, please run the following:
#
#  $ pip install baml
#
# ----------------------------------------------------------------------------

# This file was generated by BAML: please do not edit it. Instead, edit the
# BAML files and re-generate this code using: baml-cli generate
# baml-cli is available with the baml package.

import typing

import baml_py

from . import stream_types, type_builder, types
from .globals import (
    DO_NOT_USE_DIRECTLY_UNLESS_YOU_KNOW_WHAT_YOURE_DOING_RUNTIME as __runtime__,
)
from .parser import LlmResponseParser, LlmStreamParser
from .runtime import BamlCallOptions, DoNotUseDirectlyCallManager


class BamlSyncClient:
    __options: DoNotUseDirectlyCallManager
    __stream_client: "BamlStreamClient"
    __http_request: "BamlHttpRequestClient"
    __http_stream_request: "BamlHttpStreamRequestClient"
    __llm_response_parser: LlmResponseParser
    __llm_stream_parser: LlmStreamParser

    def __init__(self, options: DoNotUseDirectlyCallManager):
        self.__options = options
        self.__stream_client = BamlStreamClient(options)
        self.__http_request = BamlHttpRequestClient(options)
        self.__http_stream_request = BamlHttpStreamRequestClient(options)
        self.__llm_response_parser = LlmResponseParser(options)
        self.__llm_stream_parser = LlmStreamParser(options)

    def __getstate__(self):
        # Return state needed for pickling
        return {"options": self.__options}

    def __setstate__(self, state):
        # Restore state from pickling
        self.__options = state["options"]
        self.__stream_client = BamlStreamClient(self.__options)
        self.__http_request = BamlHttpRequestClient(self.__options)
        self.__http_stream_request = BamlHttpStreamRequestClient(self.__options)
        self.__llm_response_parser = LlmResponseParser(self.__options)
        self.__llm_stream_parser = LlmStreamParser(self.__options)

    def with_options(
        self,
        tb: typing.Optional[type_builder.TypeBuilder] = None,
        client_registry: typing.Optional[baml_py.baml_py.ClientRegistry] = None,
        collector: typing.Optional[
            typing.Union[
                baml_py.baml_py.Collector, typing.List[baml_py.baml_py.Collector]
            ]
        ] = None,
        env: typing.Optional[typing.Dict[str, typing.Optional[str]]] = None,
    ) -> "BamlSyncClient":
        options: BamlCallOptions = {}
        if tb is not None:
            options["tb"] = tb
        if client_registry is not None:
            options["client_registry"] = client_registry
        if collector is not None:
            options["collector"] = collector
        if env is not None:
            options["env"] = env
        return BamlSyncClient(self.__options.merge_options(options))

    @property
    def stream(self):
        return self.__stream_client

    @property
    def request(self):
        return self.__http_request

    @property
    def stream_request(self):
        return self.__http_stream_request

    @property
    def parse(self):
        return self.__llm_response_parser

    @property
    def parse_stream(self):
        return self.__llm_stream_parser

    def ExtractIngredients(
        self,
        text: str,
        baml_options: BamlCallOptions = {},
    ) -> typing.List["types.Ingredient"]:
        result = self.__options.merge_options(baml_options).call_function_sync(
            function_name="ExtractIngredients",
            args={
                "text": text,
            },
        )
        return typing.cast(
            typing.List["types.Ingredient"],
            result.cast_to(types, types, stream_types, False, __runtime__),
        )


class BamlStreamClient:
    __options: DoNotUseDirectlyCallManager

    def __init__(self, options: DoNotUseDirectlyCallManager):
        self.__options = options

    def ExtractIngredients(
        self,
        text: str,
        baml_options: BamlCallOptions = {},
    ) -> baml_py.BamlSyncStream[
        typing.List["stream_types.Ingredient"], typing.List["types.Ingredient"]
    ]:
        ctx, result = self.__options.merge_options(baml_options).create_sync_stream(
            function_name="ExtractIngredients",
            args={
                "text": text,
            },
        )
        return baml_py.BamlSyncStream[
            typing.List["stream_types.Ingredient"], typing.List["types.Ingredient"]
        ](
            result,
            lambda x: typing.cast(
                typing.List["stream_types.Ingredient"],
                x.cast_to(types, types, stream_types, True, __runtime__),
            ),
            lambda x: typing.cast(
                typing.List["types.Ingredient"],
                x.cast_to(types, types, stream_types, False, __runtime__),
            ),
            ctx,
        )


class BamlHttpRequestClient:
    __options: DoNotUseDirectlyCallManager

    def __init__(self, options: DoNotUseDirectlyCallManager):
        self.__options = options

    def ExtractIngredients(
        self,
        text: str,
        baml_options: BamlCallOptions = {},
    ) -> baml_py.baml_py.HTTPRequest:
        result = self.__options.merge_options(baml_options).create_http_request_sync(
            function_name="ExtractIngredients",
            args={
                "text": text,
            },
            mode="request",
        )
        return result


class BamlHttpStreamRequestClient:
    __options: DoNotUseDirectlyCallManager

    def __init__(self, options: DoNotUseDirectlyCallManager):
        self.__options = options

    def ExtractIngredients(
        self,
        text: str,
        baml_options: BamlCallOptions = {},
    ) -> baml_py.baml_py.HTTPRequest:
        result = self.__options.merge_options(baml_options).create_http_request_sync(
            function_name="ExtractIngredients",
            args={
                "text": text,
            },
            mode="stream",
        )
        return result


b = BamlSyncClient(DoNotUseDirectlyCallManager({}))
