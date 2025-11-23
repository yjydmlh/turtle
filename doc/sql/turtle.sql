-- 查询品种每天的k线数据，用于验证数据是否准确
SELECT DATE(close_time) as date, COUNT(*) as count
FROM btc_usdt
GROUP BY DATE(close_time)
ORDER BY date desc
;

