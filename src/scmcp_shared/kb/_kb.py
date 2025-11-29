from agno.knowledge.chunking.agentic import AgenticChunking
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.models.deepseek import DeepSeek
from agno.vectordb.lancedb import LanceDb
from agno.knowledge.knowledge import Knowledge as AgentKnowledge
import os
import requests
import zipfile
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

embedder_id = os.getenv("EMBEDDER_MODEL")
embedder_api_key = os.getenv("EMBEDDER_API_KEY")
embedder_base_url = os.getenv("EMBEDDER_BASE_URL")
model_id = os.getenv("MODEL")
model_api_key = os.getenv("API_KEY")
model_base_url = os.getenv("BASE_URL")


def download_vector_db(source="huggingface"):
    """
    下载向量数据库文件

    Args:
        source: 下载源 ("huggingface" 或 "github")
    """

    local_dir = Path(__file__).parent
    local_dir.mkdir(exist_ok=True)

    # 检查是否已存在
    if (local_dir / "scmcp.lance").exists():
        logger.info("Vector database already exists locally")
        return str(local_dir)

    logger.info(f"Downloading vector database from {source}...")

    # 下载文件
    if source == "huggingface":
        url = "https://huggingface.co/datasets/huangshing/scmcp_vector_db/resolve/main/vector_db.zip"
    else:
        raise ValueError(f"Unsupported source: {source}")

    logger.info(f"Downloading from: {url}")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    # 下载到目标目录
    zip_path = local_dir / "vector_db.zip"
    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # 解压文件
    logger.info("Extracting downloaded archive...")
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(local_dir)

    # 删除zip文件
    zip_path.unlink()

    logger.info(f"Vector database downloaded and extracted to: {local_dir}")
    return str(local_dir)


def load_kb(software=None, auto_download=True, download_source="huggingface"):
    """
    加载知识库

    Args:
        software: 软件名称
        auto_download: 是否自动下载向量数据库
        download_source: 下载源 ("huggingface" 或 "github")
    """
    # 获取向量数据库路径
    vector_db_path = Path(__file__).parent / "vector_db"

    # 如果不存在且允许自动下载，则下载
    if not (vector_db_path / "scmcp.lance").exists():
        if auto_download:
            logger.info("Vector database not found, downloading...")
            download_vector_db(download_source)
        else:
            raise FileNotFoundError(
                "Vector database not found. Set auto_download=True to download automatically."
            )

    vector_db = LanceDb(
        table_name=software,
        uri=vector_db_path,
        embedder=OpenAIEmbedder(
            id=embedder_id,
            base_url=embedder_base_url,
            api_key=embedder_api_key,
        ),
    )
    model = DeepSeek(
        id=model_id,
        base_url=model_base_url,
        api_key=model_api_key,
    )
    knowledge_base = AgentKnowledge(
        chunking_strategy=AgenticChunking(model=model),
        vector_db=vector_db,
    )

    return knowledge_base


def ls_workflows():
    """list all workflows"""
    workflows_path = Path(__file__).parent / "docs" / "workflow"
    workflows = list(workflows_path.glob("*.md"))
    return [workflow.name for workflow in workflows]


def read_workflow(filename: str):
    """read a workflow"""
    workflows_path = Path(__file__).parent / "docs" / "workflow"
    print(workflows_path)
    workflow = workflows_path / f"{filename}"
    with open(workflow, "r") as f:
        return f.read()
