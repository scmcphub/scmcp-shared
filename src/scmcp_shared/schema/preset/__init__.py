from __future__ import annotations

from pydantic import Field, BaseModel, ConfigDict, model_validator


class AdataInfo(BaseModel):
    """Input schema for the adata tool."""

    sampleid: str | None = Field(default=None, description="adata sampleid")
    adtype: str = Field(
        default="exp",
        description="The input adata.X data type for preprocess/analysis/plotting",
    )

    model_config = ConfigDict(extra="ignore")

    @model_validator(mode="before")
    def validate_input(cls, data: dict) -> dict:
        if isinstance(data, str):
            raise ValueError(
                f"Don't send a string, the request input is a json object, the schema of request is: {cls.model_json_schema()}"
            )
        return data
