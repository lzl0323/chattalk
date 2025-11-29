"""
RAG API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import uuid
import logging

from ..core.database import get_db
from ..core.auth import get_current_user
from ..models.db_models import User, KnowledgeBase, Document
from ..services.rag_service import rag_service
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/rag", tags=["RAG"])


class KnowledgeBaseCreate(BaseModel):
    """创建知识库请求"""
    name: str
    description: Optional[str] = None


class KnowledgeBaseResponse(BaseModel):
    """知识库响应"""
    id: str
    name: str
    description: Optional[str]
    document_count: int
    total_chunks: int
    is_active: bool
    created_at: str


class DocumentResponse(BaseModel):
    """文档响应"""
    id: str
    file_name: str
    file_type: Optional[str]
    chunk_count: int
    status: str
    created_at: str


@router.get("/knowledge-bases", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取用户的知识库列表"""
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.user_id == current_user.id)
    )
    kbs = result.scalars().all()
    
    return [
        KnowledgeBaseResponse(
            id=kb.id,
            name=kb.name,
            description=kb.description,
            document_count=kb.document_count,
            total_chunks=kb.total_chunks,
            is_active=kb.is_active,
            created_at=kb.created_at.isoformat()
        )
        for kb in kbs
    ]


@router.post("/knowledge-bases", response_model=dict)
async def create_knowledge_base(
    kb_data: KnowledgeBaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建知识库"""
    kb = KnowledgeBase(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        name=kb_data.name,
        description=kb_data.description
    )
    
    db.add(kb)
    await db.commit()
    await db.refresh(kb)
    
    logger.info(f"Created knowledge base {kb.id} for user {current_user.id}")
    
    return {
        "id": kb.id,
        "name": kb.name,
        "message": "知识库创建成功"
    }


@router.post("/knowledge-bases/{kb_id}/upload", response_model=DocumentResponse)
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """上传文档到知识库"""
    # 验证知识库
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        )
    )
    kb = result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    # 获取文件扩展名
    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    
    # 读取文件内容
    content = await file.read()
    
    # 根据文件类型提取文本
    text_content = ""
    
    if file_ext == 'pdf':
        # PDF 文件处理
        try:
            import PyPDF2
            import io
            
            pdf_file = io.BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # 提取所有页面的文本
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            if not text_content.strip():
                raise HTTPException(status_code=400, detail="PDF 文件内容为空或无法提取文本")
                
            logger.info(f"Extracted {len(text_content)} characters from PDF: {file.filename}")
            
        except ImportError:
            raise HTTPException(
                status_code=500, 
                detail="PDF 支持未安装，请运行: pip install PyPDF2"
            )
        except Exception as e:
            logger.error(f"Error reading PDF file: {e}")
            raise HTTPException(status_code=400, detail=f"PDF 文件读取失败: {str(e)}")
    
    elif file_ext in ['txt', 'md', 'markdown']:
        # 文本文件处理
        try:
            text_content = content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                text_content = content.decode('gbk')
            except:
                raise HTTPException(status_code=400, detail="文件编码不支持，请使用 UTF-8 或 GBK 编码")
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="文件内容为空")
    
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"不支持的文件格式：{file_ext}。支持的格式：TXT, MD, PDF"
        )
    
    # 创建文档记录
    doc_id = str(uuid.uuid4())
    doc = Document(
        id=doc_id,
        knowledge_base_id=kb_id,
        user_id=current_user.id,
        file_name=file.filename,
        file_type=file.filename.split('.')[-1] if '.' in file.filename else 'txt',
        file_size=len(content),
        content=text_content,
        status="processing"
    )
    
    db.add(doc)
    await db.commit()
    
    try:
        # 添加到向量库
        logger.info(f"Adding document {doc_id} to vector store")
        await rag_service.add_document(
            doc_id=doc_id,
            text=text_content,
            knowledge_base_id=kb_id,
            metadata={"file_name": file.filename, "user_id": current_user.id}
        )
        
        # 更新文档状态
        doc.status = "completed"
        doc.chunk_count = len(rag_service._chunk_text(text_content))
        
        # 更新知识库统计
        kb.document_count += 1
        kb.total_chunks += doc.chunk_count
        
        await db.commit()
        await db.refresh(doc)
        
        logger.info(f"Document {doc_id} processed successfully, chunks: {doc.chunk_count}")
        
        return DocumentResponse(
            id=doc.id,
            file_name=doc.file_name,
            file_type=doc.file_type,
            chunk_count=doc.chunk_count,
            status=doc.status,
            created_at=doc.created_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error processing document {doc_id}: {e}")
        doc.status = "failed"
        doc.error_message = str(e)
        await db.commit()
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")


@router.get("/knowledge-bases/{kb_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取知识库的文档列表"""
    # 验证知识库权限
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        )
    )
    kb = result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    # 获取文档列表
    result = await db.execute(
        select(Document).where(Document.knowledge_base_id == kb_id)
    )
    docs = result.scalars().all()
    
    return [
        DocumentResponse(
            id=doc.id,
            file_name=doc.file_name,
            file_type=doc.file_type,
            chunk_count=doc.chunk_count,
            status=doc.status,
            created_at=doc.created_at.isoformat()
        )
        for doc in docs
    ]


@router.get("/knowledge-bases/{kb_id}/stats")
async def get_knowledge_base_stats(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取知识库统计信息"""
    # 验证知识库权限
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        )
    )
    kb = result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    # 获取向量库统计
    vector_stats = rag_service.get_knowledge_base_stats(kb_id)
    
    return {
        "knowledge_base": {
            "id": kb.id,
            "name": kb.name,
            "document_count": kb.document_count,
            "total_chunks": kb.total_chunks
        },
        "vector_store": vector_stats
    }


@router.delete("/knowledge-bases/{kb_id}/documents/{doc_id}")
async def delete_document(
    kb_id: str,
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除文档"""
    # 验证文档
    result = await db.execute(
        select(Document).where(
            Document.id == doc_id,
            Document.knowledge_base_id == kb_id,
            Document.user_id == current_user.id
        )
    )
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    # 从向量库删除
    try:
        rag_service.delete_document(doc_id, kb_id)
    except Exception as e:
        logger.error(f"Error deleting document from vector store: {e}")
    
    # 从数据库删除
    await db.delete(doc)
    
    # 更新知识库统计
    result = await db.execute(
        select(KnowledgeBase).where(KnowledgeBase.id == kb_id)
    )
    kb = result.scalar_one_or_none()
    if kb:
        kb.document_count = max(0, kb.document_count - 1)
        kb.total_chunks = max(0, kb.total_chunks - doc.chunk_count)
    
    await db.commit()
    
    return {"message": "文档删除成功"}


@router.delete("/knowledge-bases/{kb_id}")
async def delete_knowledge_base(
    kb_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除知识库（包括所有文档和向量数据）"""
    from sqlalchemy import select, delete
    
    # 验证知识库权限
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.id == kb_id,
            KnowledgeBase.user_id == current_user.id
        )
    )
    kb = result.scalar_one_or_none()
    
    if not kb:
        raise HTTPException(status_code=404, detail="知识库不存在")
    
    try:
        # 1. 删除向量存储
        from ..services.rag_service import rag_service
        try:
            vector_store = rag_service.get_vector_store(kb_id)
            vector_store.clear()
            logger.info(f"Cleared vector store for knowledge base {kb_id}")
        except Exception as e:
            logger.warning(f"Failed to clear vector store: {e}")
        
        # 2. 删除数据库中的所有文档（级联删除会自动处理）
        await db.execute(
            delete(Document).where(Document.knowledge_base_id == kb_id)
        )
        
        # 3. 删除知识库
        await db.delete(kb)
        await db.commit()
        
        logger.info(f"Deleted knowledge base {kb_id} (name: {kb.name})")
        
        return {"message": f"知识库「{kb.name}」已删除"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting knowledge base {kb_id}: {e}")
        raise HTTPException(status_code=500, detail=f"删除知识库失败: {str(e)}")


@router.get("/check")
async def check_rag_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """检查 RAG 功能状态"""
    # 检查用户是否有知识库
    result = await db.execute(
        select(KnowledgeBase).where(
            KnowledgeBase.user_id == current_user.id,
            KnowledgeBase.is_active == True
        )
    )
    kbs = result.scalars().all()
    
    has_knowledge_base = len(kbs) > 0
    total_documents = sum(kb.document_count for kb in kbs)
    
    return {
        "enabled": has_knowledge_base and total_documents > 0,
        "has_knowledge_base": has_knowledge_base,
        "total_documents": total_documents,
        "knowledge_bases": [
            {
                "id": kb.id,
                "name": kb.name,
                "document_count": kb.document_count
            }
            for kb in kbs
        ]
    }
