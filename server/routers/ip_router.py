"""
IP Router - IP角色管理路由模块

该模块提供IP角色相关的 API 路由端点，包括：
- IP热度排行榜
- IP详情查看
- IP交互记录（浏览、点赞等）
- IP分类管理
- IP搜索功能

主要端点：
- GET /api/ip/top - 获取热度排行榜
- GET /api/ip/{id} - 获取IP详情
- POST /api/ip/{id}/interaction - 记录IP交互
- GET /api/ip/categories - 获取IP分类
- GET /api/ip/search - 搜索IP

依赖模块：
- services.db_adapter - 数据库适配器服务
"""

from fastapi import APIRouter, HTTPException, Request, Query
from services.db_adapter import db_adapter
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# 创建IP相关的路由器，所有端点都以 /api/ip 为前缀
router = APIRouter(prefix="/api/ip")


class InteractionRequest(BaseModel):
    """IP交互请求模型"""
    interaction_type: str  # 'view', 'like', 'share', 'comment'
    user_identifier: Optional[str] = None


@router.get("/top")
async def get_top_ips(limit: int = Query(10, ge=1, le=50)):
    """
    获取IP热度排行榜
    
    Args:
        limit: 返回的IP数量，默认10个，最多50个
        
    Returns:
        list: IP热度排行榜数据
        
    Description:
        根据热度分数返回最热门的IP角色列表。
        热度分数基于浏览、点赞、分享、评论等交互计算。
    """
    try:
        ips = await db_adapter.get_top_ips(limit)
        return {
            "success": True,
            "data": ips,
            "count": len(ips)
        }
    except Exception as e:
        logger.error(f"Error getting top IPs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get top IPs")


@router.get("/{ip_id}")
async def get_ip_details(ip_id: int):
    """
    获取IP详细信息
    
    Args:
        ip_id: IP的唯一标识符
        
    Returns:
        dict: IP的详细信息
        
    Raises:
        HTTPException: 当IP不存在时返回404错误
        
    Description:
        获取指定IP的完整信息，包括名称、描述、图片、分类等。
        同时会记录一次浏览交互。
    """
    try:
        ip_data = await db_adapter.get_ip_by_id(ip_id)
        if not ip_data:
            raise HTTPException(status_code=404, detail="IP not found")
        
        # 记录浏览交互
        try:
            await db_adapter.record_ip_interaction(ip_id, 'view')
        except Exception as e:
            logger.warning(f"Failed to record view interaction for IP {ip_id}: {e}")
        
        return {
            "success": True,
            "data": ip_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting IP details for {ip_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get IP details")


@router.post("/{ip_id}/interaction")
async def record_ip_interaction(ip_id: int, request: InteractionRequest):
    """
    记录IP交互
    
    Args:
        ip_id: IP的唯一标识符
        request: 交互请求数据
        
    Returns:
        dict: 操作结果
        
    Description:
        记录用户与IP的交互行为，用于计算热度分数。
        支持的交互类型：view（浏览）、like（点赞）、share（分享）、comment（评论）
        
    Example:
        POST /api/ip/1/interaction
        {
            "interaction_type": "like",
            "user_identifier": "user123"
        }
    """
    try:
        # 验证交互类型
        valid_types = ['view', 'like', 'share', 'comment']
        if request.interaction_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid interaction type. Must be one of: {', '.join(valid_types)}"
            )
        
        # 检查IP是否存在
        ip_data = await db_adapter.get_ip_by_id(ip_id)
        if not ip_data:
            raise HTTPException(status_code=404, detail="IP not found")
        
        # 记录交互
        await db_adapter.record_ip_interaction(
            ip_id, 
            request.interaction_type, 
            request.user_identifier
        )
        
        return {
            "success": True,
            "message": f"Interaction '{request.interaction_type}' recorded successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording interaction for IP {ip_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to record interaction")


@router.get("/categories")
async def get_ip_categories():
    """
    获取IP分类列表
    
    Returns:
        dict: 包含所有IP分类的列表
        
    Description:
        获取所有可用的IP分类，用于筛选和组织IP内容。
    """
    try:
        categories = await db_adapter.get_ip_categories()
        return {
            "success": True,
            "data": categories,
            "count": len(categories)
        }
    except Exception as e:
        logger.error(f"Error getting IP categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to get IP categories")


@router.get("/search")
async def search_ips(
    q: Optional[str] = Query(None, description="搜索关键词"),
    category_id: Optional[int] = Query(None, description="分类ID筛选"),
    limit: int = Query(20, ge=1, le=100, description="返回结果数量")
):
    """
    搜索IP
    
    Args:
        q: 搜索关键词，会在IP名称和描述中搜索
        category_id: 分类ID，用于筛选特定分类的IP
        limit: 返回结果数量，默认20个，最多100个
        
    Returns:
        dict: 搜索结果列表
        
    Description:
        根据关键词和分类筛选条件搜索IP。
        结果按热度分数排序。
        
    Example:
        GET /api/ip/search?q=初音&category_id=3&limit=10
    """
    try:
        ips = await db_adapter.search_ips(q, category_id, limit)
        return {
            "success": True,
            "data": ips,
            "count": len(ips),
            "query": q,
            "category_id": category_id
        }
    except Exception as e:
        logger.error(f"Error searching IPs: {e}")
        raise HTTPException(status_code=500, detail="Failed to search IPs")


@router.get("/")
async def get_all_ips(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    获取所有IP（分页）
    
    Args:
        limit: 每页数量
        offset: 偏移量
        
    Returns:
        dict: IP列表
        
    Description:
        获取所有IP的分页列表，按热度排序。
    """
    try:
        # 使用搜索功能获取所有IP
        ips = await db_adapter.search_ips(limit=limit)
        
        # 简单的偏移处理（实际应该在数据库层面实现）
        if offset > 0:
            ips = ips[offset:] if offset < len(ips) else []
        
        return {
            "success": True,
            "data": ips,
            "count": len(ips),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error getting all IPs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get IPs")