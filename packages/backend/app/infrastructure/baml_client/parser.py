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

from . import stream_types, types
from .runtime import BamlCallOptions, DoNotUseDirectlyCallManager


class LlmResponseParser:
    __options: DoNotUseDirectlyCallManager

    def __init__(self, options: DoNotUseDirectlyCallManager):
        self.__options = options

    def ExtractIngredients(
        self,
        llm_response: str,
        baml_options: BamlCallOptions = {},
    ) -> typing.List["types.Ingredient"]:
        result = self.__options.merge_options(baml_options).parse_response(
            function_name="ExtractIngredients",
            llm_response=llm_response,
            mode="request",
        )
        return typing.cast(typing.List["types.Ingredient"], result)


class LlmStreamParser:
    __options: DoNotUseDirectlyCallManager

    def __init__(self, options: DoNotUseDirectlyCallManager):
        self.__options = options

    def ExtractIngredients(
        self,
        llm_response: str,
        baml_options: BamlCallOptions = {},
    ) -> typing.List["stream_types.Ingredient"]:
        result = self.__options.merge_options(baml_options).parse_response(
            function_name="ExtractIngredients", llm_response=llm_response, mode="stream"
        )
        return typing.cast(typing.List["stream_types.Ingredient"], result)
