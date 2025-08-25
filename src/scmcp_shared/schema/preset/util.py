from pydantic import Field, BaseModel, model_validator
from typing import Optional, List, Dict, Any, Literal


class MarkVarParam(BaseModel):
    """Determine or mark if each gene meets specific conditions and store results in adata.var as boolean values"""

    var_name: str = Field(
        default=None,
        description="Column name that will be added to adata.var, do not set if user does not ask",
    )
    pattern_type: Optional[Literal["startswith", "endswith", "contains"]] = Field(
        default=None,
        description="Pattern matching type (startswith/endswith/contains), it should be None when gene_class is not None",
    )
    patterns: Optional[str] = Field(
        default=None,
        description="gene pattern to match, must be a string, it should be None when gene_class is not None",
    )

    gene_class: Optional[Literal["mitochondrion", "ribosomal", "hemoglobin"]] = Field(
        default=None, description="Gene class type (Mitochondrion/Ribosomal/Hemoglobin)"
    )

    @model_validator(mode="before")
    def validate_input(cls, data: dict) -> dict:
        if isinstance(data, str):
            raise ValueError(
                f"Don't send a string, the request input is a json object, the schema of request is: {cls.model_json_schema()}"
            )
        return data


class ListVarParam(BaseModel):
    """ListVarModel"""

    pass


class ListObsParam(BaseModel):
    """ListObsModel"""

    pass


class VarNamesParam(BaseModel):
    """ListObsModel"""

    var_names: List[str] = Field(default=None, description="gene names.")

    @model_validator(mode="before")
    def validate_input(cls, data: dict) -> dict:
        if isinstance(data, str):
            raise ValueError(
                f"Don't send a string, the request input is a json object, the schema of request is: {cls.model_json_schema()}"
            )
        return data


class ConcatBaseParam(BaseModel):
    """Model for concatenating AnnData objects"""

    axis: Literal["obs", 0, "var", 1] = Field(
        default="obs",
        description="Which axis to concatenate along. 'obs' or 0 for observations, 'var' or 1 for variables.",
    )
    join: Literal["inner", "outer"] = Field(
        default="inner",
        description="How to align values when concatenating. If 'outer', the union of the other axis is taken. If 'inner', the intersection.",
    )
    merge: Optional[Literal["same", "unique", "first", "only"]] = Field(
        default=None,
        description="How elements not aligned to the axis being concatenated along are selected.",
    )
    uns_merge: Optional[Literal["same", "unique", "first", "only"]] = Field(
        default=None,
        description="How the elements of .uns are selected. Uses the same set of strategies as the merge argument, except applied recursively.",
    )
    label: Optional[str] = Field(
        default=None,
        description="label different adata, Column in axis annotation (i.e. .obs or .var) to place batch information in. ",
    )
    keys: Optional[List[str]] = Field(
        default=None,
        description="Names for each object being added. These values are used for column values for label or appended to the index if index_unique is not None.",
    )
    index_unique: Optional[str] = Field(
        default=None,
        description="Whether to make the index unique by using the keys. If provided, this is the delimiter between '{orig_idx}{index_unique}{key}'.",
    )
    fill_value: Optional[Any] = Field(
        default=None,
        description="When join='outer', this is the value that will be used to fill the introduced indices.",
    )
    pairwise: bool = Field(
        default=False,
        description="Whether pairwise elements along the concatenated dimension should be included.",
    )

    @model_validator(mode="before")
    def validate_input(cls, data: dict) -> dict:
        if isinstance(data, str):
            raise ValueError(
                f"Don't send a string, the request input is a json object, the schema of request is: {cls.model_json_schema()}"
            )
        return data


class DPTIROOTParam(BaseModel):
    """Input schema for setting the root cell for diffusion pseudotime."""

    diffmap_key: str = Field(
        default="X_diffmap",
        description="Key for diffusion map coordinates stored in adata.obsm.",
    )
    dimension: int = Field(
        description="Dimension index to use for finding the root cell."
    )
    direction: Literal["min", "max"] = Field(
        description="use the minimum or maximum value along the selected dimension to identify the root cell."
    )

    @model_validator(mode="before")
    def validate_input(cls, data: dict) -> dict:
        if isinstance(data, str):
            raise ValueError(
                f"Don't send a string, the request input is a json object, the schema of request is: {cls.model_json_schema()}"
            )
        return data


class CelltypeMapCellTypeParam(BaseModel):
    """Input schema for mapping cluster IDs to cell type names."""

    cluster_key: str = Field(description="Key in adata.obs containing cluster IDs.")
    added_key: str = Field(description="Key to add to adata.obs for cell type names.")
    mapping: Dict[str, str] = Field(
        default=None,
        description="Mapping Dictionary from cluster IDs to cell type names.",
    )
    new_names: Optional[List[str]] = Field(
        default=None, description="a list of new cell type names."
    )

    @model_validator(mode="before")
    def validate_input(cls, data: dict) -> dict:
        if isinstance(data, str):
            raise ValueError(
                f"Don't send a string, the request input is a json object, the schema of request is: {cls.model_json_schema()}"
            )
        return data


class AddLayerParam(BaseModel):
    """Input schema for adding a layer to AnnData object."""

    layer_name: str = Field(description="Name of the layer to add to adata.layers.")

    @model_validator(mode="before")
    def validate_input(cls, data: dict) -> dict:
        if isinstance(data, str):
            raise ValueError(
                f"Don't send a string, the request input is a json object, the schema of request is: {cls.model_json_schema()}"
            )
        return data


class QueryOpLogParam(BaseModel):
    """QueryOpLogModel"""

    n: int = Field(default=10, description="Number of operations to return.")

    @model_validator(mode="before")
    def validate_input(cls, data: dict) -> dict:
        if isinstance(data, str):
            raise ValueError(
                f"Don't send a string, the request input is a json object, the schema of request is: {cls.model_json_schema()}"
            )
        return data
