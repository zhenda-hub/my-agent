"""FastAPI 服务模块"""
from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import shutil
from pathlib import Path
from src.config import config
from src.chains.qa_chain import QAChain
from src.retriever.base import Retriever
from src.loaders import get_loader
from src.vector_store import get_vector_store


app = FastAPI(
    title="企业级知识库问答 API",
    description="基于 RAG 的企业知识库问答系统",
    version="1.0.0",
)


# 请求/响应模型
class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = None


class SourceInfo(BaseModel):
    content: str
    source: str
    metadata: dict


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]


class HealthResponse(BaseModel):
    status: str
    message: str


# 全局实例
qa_chain = QAChain()


@app.get("/", response_model=dict)
async def root():
    """根路径"""
    return {
        "message": "企业级知识库问答 API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "query": "/api/v1/query",
            "upload": "/api/v1/upload",
        },
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """健康检查"""
    return HealthResponse(
        status="ok",
        message="服务正常运行",
    )


@app.post("/api/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    问答接口

    Args:
        request: 查询请求

    Returns:
        问答结果（包含答案和来源）
    """
    try:
        if not request.query.strip():
            raise HTTPException(status_code=400, detail="查询不能为空")

        # 创建检索器（可自定义 top_k）
        retriever = Retriever(top_k=request.top_k)
        chain = QAChain(retriever=retriever)

        # 执行问答
        result = chain.run(request.query)

        # 格式化来源
        sources = [
            SourceInfo(
                content=src["content"],
                source=src["source"],
                metadata=src["metadata"],
            )
            for src in result.sources
        ]

        return QueryResponse(
            answer=result.answer,
            sources=sources,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败: {str(e)}")


async def process_uploaded_file(file_path: str, clear_source: bool = False):
    """
    处理上传的文件（后台任务）

    Args:
        file_path: 文件路径
        clear_source: 是否清除旧数据
    """
    try:
        from src.scripts.ingest import ingest_file

        vector_store = get_vector_store()
        ingest_file(file_path, vector_store, clear_source=clear_source)
    except Exception as e:
        print(f"处理文件失败: {e}")


@app.post("/api/v1/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    clear: bool = False,
):
    """
    上传文档接口

    Args:
        file: 上传的文件
        clear: 是否清除该来源的旧数据

    Returns:
        上传结果
    """
    try:
        # 检查文件扩展名
        allowed_extensions = {".pdf", ".docx", ".doc", ".md", ".markdown"}
        file_ext = Path(file.filename).suffix.lower()

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的文件格式。支持的格式: {', '.join(allowed_extensions)}",
            )

        # 保存文件
        file_path = config.DOCUMENTS_DIR / file.filename

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 后台处理文件
        background_tasks.add_task(
            process_uploaded_file,
            str(file_path),
            clear,
        )

        return JSONResponse(
            status_code=202,
            content={
                "message": "文件上传成功，正在处理中...",
                "filename": file.filename,
                "path": str(file_path),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")


@app.get("/api/v1/stats")
async def get_stats():
    """
    获取知识库统计信息

    Returns:
        统计信息
    """
    try:
        vector_store = get_vector_store()
        collection = vector_store.collection

        count = collection.count()

        return {
            "total_documents": count,
            "collection_name": vector_store.collection_name,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True,
    )
