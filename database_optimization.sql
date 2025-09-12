-- 数据库性能优化建议
-- 为K线数据表添加必要的索引以提升查询性能

-- BTC/USDT表索引优化
CREATE INDEX IF NOT EXISTS idx_btc_usdt_open_time ON btc_usdt(open_time DESC);
CREATE INDEX IF NOT EXISTS idx_btc_usdt_timestamp ON btc_usdt(timestamp);
CREATE INDEX IF NOT EXISTS idx_btc_usdt_time_range ON btc_usdt(open_time, close_time);

-- ETH/USDT表索引优化（如果使用）
CREATE INDEX IF NOT EXISTS idx_eth_usdt_open_time ON eth_usdt(open_time DESC);
CREATE INDEX IF NOT EXISTS idx_eth_usdt_timestamp ON eth_usdt(timestamp);
CREATE INDEX IF NOT EXISTS idx_eth_usdt_time_range ON eth_usdt(open_time, close_time);

-- 分析表统计信息以优化查询计划
ANALYZE btc_usdt;
ANALYZE eth_usdt;

-- 建议的数据库配置优化（postgresql.conf）
/*
# 连接和内存设置
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# 查询优化
random_page_cost = 1.1
effective_io_concurrency = 200

# WAL设置
wal_buffers = 16MB
checkpoint_completion_target = 0.9
*/

-- 定期维护任务
-- VACUUM ANALYZE btc_usdt;
-- REINDEX INDEX idx_btc_usdt_open_time;