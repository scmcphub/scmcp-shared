from pydantic import Field, field_validator, model_validator, BaseModel
from typing import Optional, Literal


class ReadParam(BaseModel):
    """Input schema for the read tool."""

    filename: str = Field(..., description="Path to the file to read.")

    backed: Literal["r", "r+"] = Field(
        default=None,
        description="If 'r', load AnnData in 'backed' mode instead of fully loading it into memory ('memory' mode). If you want to modify backed attributes of the AnnData object, you need to choose 'r+'.",
    )
    sheet: str = Field(
        default=None, description="Name of sheet/table in hdf5 or Excel file."
    )
    delimiter: str = Field(
        default=None,
        description="Delimiter that separates data within text file. If None, will split at arbitrary number of white spaces, which is different from enforcing splitting at any single white space.",
    )
    first_column_names: bool = Field(
        default=False,
        description="Assume the first column stores row names. This is only necessary if these are not strings: strings in the first column are automatically assumed to be row names.",
    )
    transpose: bool = Field(
        default=False, description="If True, the data will be transposed."
    )
    backup_url: str = Field(
        default=None,
        description="Retrieve the file from an URL if not present on disk.",
    )
    cache: bool = Field(
        default=False,
        description="If False, read from source, if True, read from fast 'h5ad' cache.",
    )
    cache_compression: Literal["gzip", "lzf"] = Field(
        default=None,
        description="See the h5py dataset_compression. (Default: settings.cache_compression)",
    )
    var_names: str = Field(
        default="gene_symbols",
        description="The variables index for 10x mtx format. Either 'gene_symbols' or 'gene_ids'.",
    )
    make_unique: bool = Field(
        default=True,
        description="Whether to make the variables index unique by appending '-1', '-2' etc. or not. Used for 10x mtx format.",
    )
    gex_only: bool = Field(
        default=True,
        description="Only keep 'Gene Expression' data and ignore other feature types, e.g. 'Antibody Capture', 'CRISPR Guide Capture', or 'Custom'. Used for 10x formats.",
    )
    prefix: str = Field(
        default=None,
        description="Any prefix before matrix.mtx, genes.tsv and barcodes.tsv. For instance, if the files are named patientA_matrix.mtx, patientA_genes.tsv and patientA_barcodes.tsv the prefix is patientA_. Used for 10x mtx format.",
    )

    @field_validator("backed")
    def validate_backed(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["r", "r+"]:
            raise ValueError("If backed is provided, it must be either 'r' or 'r+'")
        return v

    @field_validator("cache_compression")
    def validate_cache_compression(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["gzip", "lzf"]:
            raise ValueError("cache_compression must be either 'gzip', 'lzf', or None")
        return v

    @field_validator("var_names")
    def validate_var_names(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ["gene_symbols", "gene_ids"]:
            raise ValueError("var_names must be either 'gene_symbols' or 'gene_ids'")
        return v

    @model_validator(mode="before")
    def validate_input(cls, data: dict) -> dict:
        if isinstance(data, str):
            raise ValueError(
                f"Don't send a string, the request input is a json object, the schema of request is: {cls.model_json_schema()}"
            )
        return data


class WriteParam(BaseModel):
    """Input schema for the write tool."""

    filename: str = Field(
        description="Path to save the file. If no extension is provided, the default format will be used."
    )
    ext: Literal["h5", "csv", "txt", "npz"] = Field(
        default=None,
        description="File extension to infer file format. If None, defaults to scanpy's settings.file_format_data.",
    )
    compression: Literal["gzip", "lzf"] = Field(
        default="gzip", description="Compression format for h5 files."
    )
    compression_opts: int = Field(
        default=None, description="Compression options for h5 files."
    )

    @model_validator(mode="after")
    def validate_extension_compression(self) -> "WriteParam":
        # If ext is provided and not h5, compression should be None
        if self.ext is not None and self.ext != "h5" and self.compression is not None:
            raise ValueError("Compression can only be used with h5 files")
        return self

    @model_validator(mode="before")
    def validate_input(cls, data: dict) -> dict:
        if isinstance(data, str):
            raise ValueError(
                f"Don't send a string, the request input is a json object, the schema of request is: {cls.model_json_schema()}"
            )
        return data
