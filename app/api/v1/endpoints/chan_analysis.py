from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.api.deps import get_db
from app.services.kline_aggregator import kline_aggregator
from app.services.chan_adapter import chan_adapter
from app.core.exceptions import create_success_response
from app.core.logger import app_logger

router = APIRouter()


@router.get("/info")
def get_chan_module_info():
    """获取Chan模块信息和状态"""
    try:
        info = chan_adapter.get_chan_info()

        return create_success_response(data={
            "chan_module": info,
            "system_info": {
                "integration_status": "ready" if info["is_available"] else "needs_setup",
                "data_flow": [
                    "1. 获取K线数据 (kline_aggregator)",
                    "2. 调用Chan模块分析 (chan_adapter)",
                    "3. 标准化结果格式",
                    "4. 返回缠论分析结果"
                ],
                "supported_analysis": [
                    "分型识别 (顶分型、底分型)",
                    "笔的构建 (上涨笔、下跌笔)",
                    "线段分析",
                    "买卖点识别",
                    "趋势方向判断"
                ]
            }
        })
    except Exception as e:
        app_logger.error(f"❌ 获取Chan模块信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取模块信息失败")


@router.get("/analyze")
def analyze_chan_theory(
        timeframe: str = Query("1h", description="时间周期"),
        limit: int = Query(200, ge=50, le=500, description="分析的K线数量"),
        db: Session = Depends(get_db)
):
    """
    缠论技术分析 - 使用集成的Chan模块

    功能特点:
    - 自动识别分型（顶分型🔺、底分型🔻）
    - 构建笔的结构（上涨笔、下跌笔）
    - 分析线段
    - 识别买卖点
    - 生成交易建议

    参数:
    - timeframe: 时间周期 (1m, 5m, 15m, 30m, 1h, 4h, 1d)
    - limit: 分析的K线数量 (50-500，建议200以上获得更好效果)
    """
    try:
        app_logger.info(f"🔍 开始缠论分析 - 周期: {timeframe}, 数据量: {limit}")

        # 检查Chan模块状态
        if not chan_adapter.is_available:
            app_logger.warning("⚠️ Chan模块不可用，使用简化分析")

        # 获取K线数据
        klines = kline_aggregator.aggregate_klines(
            db=db,
            timeframe=timeframe,
            limit=limit
        )

        if not klines:
            raise HTTPException(status_code=404, detail="没有找到K线数据，请先调用 /api/v1/simple/fetch-data 获取数据")

        # 使用Chan模块进行分析
        analysis_result = chan_adapter.analyze_klines(klines)

        # 统计分析结果
        fenxings_count = len(analysis_result.get('fenxings', []))
        bis_count = len(analysis_result.get('bis', []))
        xianduan_count = len(analysis_result.get('xianduan', []))
        buy_sell_points_count = len(analysis_result.get('buy_sell_points', []))

        if "error" in analysis_result:
            app_logger.warning(f"⚠️ 分析中遇到问题: {analysis_result['error']}")

        app_logger.info(
            f"✅ 缠论分析完成 - 分型: {fenxings_count}, 笔: {bis_count}, 线段: {xianduan_count}, 买卖点: {buy_sell_points_count}")

        return create_success_response(data={
            "analysis": analysis_result,
            "metadata": {
                "klines_analyzed": len(klines),
                "timeframe": timeframe,
                "analysis_time": klines[-1]["close_time"] if klines else None,
                "latest_price": klines[-1]["close_price"] if klines else None,
                "chan_module_available": chan_adapter.is_available,
                "data_source": analysis_result.get('analysis_summary', {}).get('data_source', 'unknown'),
                "statistics": {
                    "fenxings": fenxings_count,
                    "bis": bis_count,
                    "xianduan": xianduan_count,
                    "buy_sell_points": buy_sell_points_count
                }
            },
            "usage_tips": {
                "fenxings": "🔺红色标记为顶分型，🔻绿色标记为底分型",
                "bis": "连接相邻分型形成的笔，显示价格运动方向",
                "trend": "基于最近几笔的方向和强度判断趋势",
                "suggestion": "根据缠论理论生成的操作建议，仅供参考"
            }
        })

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ 缠论分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail="分析服务暂时不可用")


@router.get("/chart-data")
def get_chart_data(
        timeframe: str = Query("1h", description="时间周期"),
        limit: int = Query(100, ge=20, le=300, description="图表数据量"),
        include_analysis: bool = Query(True, description="是否包含分析结果"),
        db: Session = Depends(get_db)
):
    """
    获取图表数据 - 包含K线和缠论分析，适合前端图表显示

    返回专门为前端图表优化的数据格式:
    - 标准的K线数据格式 [timestamp, open, high, low, close, volume]
    - 缠论分型标记点
    - 笔的连线数据
    - 买卖点标记
    """
    try:
        # 获取K线数据
        klines = kline_aggregator.aggregate_klines(
            db=db,
            timeframe=timeframe,
            limit=limit
        )

        if not klines:
            raise HTTPException(status_code=404, detail="没有找到K线数据")

        # 准备图表数据格式 - 适配前端图表库
        chart_data = {
            "klines": [],  # [timestamp, open, high, low, close]
            "volume": [],  # [timestamp, volume]
            "timestamps": []  # 时间标签数组
        }

        for kline in klines:
            # K线数据 - 标准OHLC格式
            chart_data["klines"].append([
                kline["timestamp"],
                float(kline["open_price"]),
                float(kline["high_price"]),
                float(kline["low_price"]),
                float(kline["close_price"])
            ])

            # 成交量数据
            chart_data["volume"].append([
                kline["timestamp"],
                float(kline["volume"])
            ])

            # 时间标签
            chart_data["timestamps"].append(kline["timestamp"])

        result = {
            "chart_data": chart_data,
            "metadata": {
                "timeframe": timeframe,
                "data_count": len(klines),
                "price_range": {
                    "high": max(float(k["high_price"]) for k in klines),
                    "low": min(float(k["low_price"]) for k in klines)
                },
                "time_range": {
                    "start": klines[0]["open_time"],
                    "end": klines[-1]["close_time"]
                }
            }
        }

        # 如果需要包含分析结果
        if include_analysis and len(klines) >= 20:
            app_logger.info("📊 执行缠论分析并添加图表标记")

            analysis = chan_adapter.analyze_klines(klines)
            if "error" not in analysis:
                result["analysis"] = analysis

                # 为图表准备分型标记数据
                fenxings_markers = []
                for fx in analysis.get("fenxings", []):
                    fenxings_markers.append({
                        "timestamp": fx["timestamp"],
                        "price": fx["price"],
                        "type": fx["type"],
                        "strength": fx.get("strength", 1.0),
                        "symbol": "🔺" if fx["type"] == "top" else "🔻",
                        "color": "#ef4444" if fx["type"] == "top" else "#22c55e"
                    })

                # 为图表准备笔的连线数据
                bis_lines = []
                for bi in analysis.get("bis", []):
                    if bi.get("start") and bi.get("end"):
                        bis_lines.append({
                            "start": {
                                "timestamp": bi["start"]["timestamp"],
                                "price": bi["start"]["price"]
                            },
                            "end": {
                                "timestamp": bi["end"]["timestamp"],
                                "price": bi["end"]["price"]
                            },
                            "direction": bi["direction"],
                            "color": "#22c55e" if bi["direction"] == "up" else "#ef4444",
                            "width": 2
                        })

                # 买卖点标记
                buy_sell_markers = []
                for point in analysis.get("buy_sell_points", []):
                    buy_sell_markers.append({
                        "timestamp": point["timestamp"],
                        "price": point["price"],
                        "type": point["type"],
                        "confidence": point.get("confidence", 0.5),
                        "symbol": "B" if "买" in point["type"] else "S",
                        "color": "#16a34a" if "买" in point["type"] else "#dc2626"
                    })

                result["chart_markers"] = {
                    "fenxings": fenxings_markers,
                    "bis_lines": bis_lines,
                    "buy_sell_points": buy_sell_markers
                }

                result["metadata"]["analysis_included"] = True
                result["metadata"]["chan_module_status"] = chan_adapter.is_available

        return create_success_response(data=result)

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ 获取图表数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取图表数据失败")


@router.get("/summary")
def get_analysis_summary(
        timeframe: str = Query("1h", description="时间周期"),
        db: Session = Depends(get_db)
):
    """获取简化的分析摘要 - 适合快速查看市场状态"""
    try:
        # 获取最近100根K线进行快速分析
        klines = kline_aggregator.aggregate_klines(
            db=db,
            timeframe=timeframe,
            limit=100
        )

        if not klines:
            return create_success_response(data={
                "summary": "暂无数据",
                "status": "no_data",
                "recommendation": "请先调用 /api/v1/simple/fetch-data 获取数据"
            })

        analysis = chan_adapter.analyze_klines(klines)

        if "error" in analysis:
            return create_success_response(data={
                "summary": f"分析失败: {analysis['error']}",
                "status": "error",
                "chan_module_available": chan_adapter.is_available
            })

        summary = analysis.get("analysis_summary", {})
        trend = analysis.get("trend", {})
        latest_price = float(klines[-1]["close_price"])

        # 构建简化摘要
        quick_summary = {
            "market_status": {
                "current_price": latest_price,
                "trend_direction": trend.get("direction", "neutral"),
                "trend_strength": trend.get("strength", 0),
                "trend_description": {
                    "up": "📈 上涨趋势",
                    "down": "📉 下跌趋势",
                    "neutral": "➡️ 震荡整理"
                }.get(trend.get("direction", "neutral"), "➡️ 震荡整理")
            },
            "chan_analysis": {
                "fenxings_count": summary.get("total_fenxings", 0),
                "bis_count": summary.get("total_bis", 0),
                "analysis_quality": summary.get("analysis_quality", "unknown"),
                "data_source": summary.get("data_source", "unknown")
            },
            "trading_suggestion": {
                "suggestion": summary.get("suggestion", "等待更多数据"),
                "confidence": "high" if summary.get("analysis_quality") == "good" else "low",
                "risk_level": "medium"  # 根据趋势强度和质量计算
            },
            "metadata": {
                "timeframe": timeframe,
                "last_update": klines[-1]["close_time"],
                "data_points": len(klines),
                "chan_module_available": chan_adapter.is_available
            }
        }

        # 计算风险等级
        strength = trend.get("strength", 0)
        quality = summary.get("analysis_quality", "unknown")

        if quality == "good" and strength > 0.7:
            quick_summary["trading_suggestion"]["risk_level"] = "low"
        elif quality == "limited" or strength < 0.3:
            quick_summary["trading_suggestion"]["risk_level"] = "high"

        return create_success_response(data=quick_summary)

    except Exception as e:
        app_logger.error(f"❌ 获取分析摘要失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取摘要失败")


@router.get("/fenxings")
def get_fenxings_only(
        timeframe: str = Query("1h", description="时间周期"),
        limit: int = Query(200, ge=50, le=500, description="分析的K线数量"),
        db: Session = Depends(get_db)
):
    """仅获取分型识别结果 - 轻量级分析接口"""
    try:
        klines = kline_aggregator.aggregate_klines(db=db, timeframe=timeframe, limit=limit)

        if not klines:
            raise HTTPException(status_code=404, detail="没有找到K线数据")

        analysis = chan_adapter.analyze_klines(klines)
        fenxings = analysis.get("fenxings", [])

        # 分类分型
        top_fenxings = [fx for fx in fenxings if fx["type"] == "top"]
        bottom_fenxings = [fx for fx in fenxings if fx["type"] == "bottom"]

        return create_success_response(data={
            "fenxings": {
                "all": fenxings,
                "tops": top_fenxings,
                "bottoms": bottom_fenxings
            },
            "statistics": {
                "total": len(fenxings),
                "tops_count": len(top_fenxings),
                "bottoms_count": len(bottom_fenxings),
                "average_strength": sum(fx.get("strength", 0) for fx in fenxings) / len(fenxings) if fenxings else 0
            },
            "metadata": {
                "timeframe": timeframe,
                "klines_analyzed": len(klines),
                "analysis_type": "fenxings_only"
            }
        })

    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"❌ 获取分型数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取分型数据失败")


@router.get("/health")
def chan_health_check():
    """缠论分析模块健康检查"""
    try:
        chan_info = chan_adapter.get_chan_info()

        health_status = {
            "status": "healthy" if chan_info["is_available"] else "degraded",
            "components": {
                "chan_adapter": "ready",
                "chan_module": "loaded" if chan_info["module_loaded"] else "missing",
                "analysis_capability": "full" if chan_info["is_available"] else "fallback"
            },
            "features": {
                "fenxing_recognition": True,
                "bi_construction": chan_info["is_available"],
                "xianduan_analysis": chan_info["is_available"],
                "buy_sell_points": chan_info["is_available"]
            },
            "performance": {
                "analysis_mode": "chan_module" if chan_info["is_available"] else "fallback",
                "recommended_data_size": "200+ K线获得最佳效果",
                "supported_timeframes": kline_aggregator.get_available_timeframes()
            }
        }

        return create_success_response(data=health_status)

    except Exception as e:
        app_logger.error(f"❌ 缠论模块健康检查失败: {str(e)}")
        raise HTTPException(status_code=500, detail="健康检查失败")