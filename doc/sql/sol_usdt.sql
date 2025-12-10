
-- 建表语句
create table sol_usdt
(
    id                     serial,
    timestamp              bigint                  not null,
    open_time              timestamp               not null,
    close_time             timestamp               not null,
    open_price             numeric(30, 18)         not null,
    high_price             numeric(30, 18)         not null,
    low_price              numeric(30, 18)         not null,
    close_price            numeric(30, 18)         not null,
    volume                 numeric(30, 8)          not null,
    quote_volume           numeric(30, 8)          not null,
    trades_count           integer                 not null,
    taker_buy_volume       numeric(30, 8)          not null,
    taker_buy_quote_volume numeric(30, 8)          not null,
    created_at             timestamp default now() not null,
    updated_at             timestamp default now() not null,
    primary key (open_time, close_time, id)
);

alter table sol_usdt
    owner to postgres;

create index idx_sol_usdt_timestamp
    on sol_usdt (timestamp);

create index idx_sol_usdt_open_time
    on sol_usdt (open_time desc);

-- 表注释
COMMENT ON TABLE sol_usdt IS 'sol/USDT 交易对 K线/行情数据表';

-- 字段注释
COMMENT ON COLUMN sol_usdt.id IS '主键ID';
COMMENT ON COLUMN sol_usdt.timestamp IS 'Unix时间戳(毫秒)也是开盘时间';
COMMENT ON COLUMN sol_usdt.open_time IS '开盘时间';
COMMENT ON COLUMN sol_usdt.close_time IS '收盘时间';
COMMENT ON COLUMN sol_usdt.open_price IS '开盘价';
COMMENT ON COLUMN sol_usdt.high_price IS '最高价';
COMMENT ON COLUMN sol_usdt.low_price IS '最低价';
COMMENT ON COLUMN sol_usdt.close_price IS '收盘价';
COMMENT ON COLUMN sol_usdt.volume IS '成交量(sol)';
COMMENT ON COLUMN sol_usdt.quote_volume IS '成交额(USDT)';
COMMENT ON COLUMN sol_usdt.trades_count IS '成交笔数';
COMMENT ON COLUMN sol_usdt.taker_buy_volume IS '主动买入成交量(Taker)';
COMMENT ON COLUMN sol_usdt.taker_buy_quote_volume IS '主动买入成交额(Taker)';
COMMENT ON COLUMN sol_usdt.created_at IS '数据入库时间';
COMMENT ON COLUMN sol_usdt.updated_at IS '数据更新时间';

-- 创建超表语句
SELECT create_hypertable('sol_usdt', 'open_time', chunk_time_interval => INTERVAL '7 days');

-- 创建5分钟持续聚合视图
CREATE MATERIALIZED VIEW sol_usdt_5m
WITH (timescaledb.continuous) AS
SELECT time_bucket('5 minutes', open_time) AS bucket,
       EXTRACT(EPOCH FROM time_bucket('5 minutes', open_time))::bigint * 1000 AS id,
       FIRST(open_time, open_time) AS open_time,
       LAST(close_time, close_time) AS close_time,
       FIRST(open_price, open_time) AS open_price,
       LAST(close_price, close_time) AS close_price,
       MAX(high_price) AS high_price,
       MIN(low_price) AS low_price,
       SUM(volume) AS volume
FROM sol_usdt
GROUP BY time_bucket('5 minutes', open_time);
--为5分钟聚合视图添加刷新策略
SELECT add_continuous_aggregate_policy('sol_usdt_5m',
  start_offset => INTERVAL '2 hours',
  end_offset => INTERVAL '5 minutes',
  schedule_interval => INTERVAL '5 minutes');


-- 创建15分钟持续聚合视图
CREATE MATERIALIZED VIEW sol_usdt_15m
WITH (timescaledb.continuous) AS
SELECT time_bucket('15 minutes', open_time) AS bucket,
       EXTRACT(EPOCH FROM time_bucket('15 minutes', open_time))::bigint * 1000 AS id,
       FIRST(open_time, open_time) AS open_time,
       LAST(close_time, close_time) AS close_time,
       FIRST(open_price, open_time) AS open_price,
       LAST(close_price, close_time) AS close_price,
       MAX(high_price) AS high_price,
       MIN(low_price) AS low_price,
       SUM(volume) AS volume
FROM sol_usdt
GROUP BY time_bucket('15 minutes', open_time);
-- 为15分钟聚合视图添加刷新策略
SELECT add_continuous_aggregate_policy('sol_usdt_15m',
  start_offset => INTERVAL '3 hours',
  end_offset => INTERVAL '15 minutes',
  schedule_interval => INTERVAL '5 minutes');


-- 创建一个30分钟持续聚合视图
CREATE MATERIALIZED VIEW sol_usdt_30m
WITH (timescaledb.continuous) AS
SELECT time_bucket('30 minutes', open_time) AS bucket,
       EXTRACT(EPOCH FROM time_bucket('30 minutes', open_time))::bigint * 1000 AS id,
       FIRST(open_time, open_time) AS open_time,
       LAST(close_time, close_time) AS close_time,
       FIRST(open_price, open_time) AS open_price,
       LAST(close_price, close_time) AS close_price,
       MAX(high_price) AS high_price,
       MIN(low_price) AS low_price,
       SUM(volume) AS volume
FROM sol_usdt
GROUP BY time_bucket('30 minutes', open_time);
-- 为30分钟聚合视图添加刷新策略
SELECT add_continuous_aggregate_policy('sol_usdt_30m',
  start_offset => INTERVAL '6 hours',
  end_offset => INTERVAL '30 minutes',
  schedule_interval => INTERVAL '15 minutes');


-- 创建一个1小时持续聚合视图
CREATE MATERIALIZED VIEW sol_usdt_1h
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 hour', open_time) AS bucket,
       EXTRACT(EPOCH FROM time_bucket('1 hour', open_time))::bigint * 1000 AS id,
       FIRST(open_time, open_time) AS open_time,
       LAST(close_time, close_time) AS close_time,
       FIRST(open_price, open_time) AS open_price,
       LAST(close_price, close_time) AS close_price,
       MAX(high_price) AS high_price,
       MIN(low_price) AS low_price,
       SUM(volume) AS volume
FROM sol_usdt
GROUP BY time_bucket('1 hour', open_time);
-- 为1小时聚合视图添加刷新策略
SELECT add_continuous_aggregate_policy('sol_usdt_1h',
  start_offset => INTERVAL '24 hours',
  end_offset => INTERVAL '1 hour',
  schedule_interval => INTERVAL '1 hour');


-- 创建一个4小时持续聚合视图
CREATE MATERIALIZED VIEW sol_usdt_4h
WITH (timescaledb.continuous) AS
SELECT time_bucket('4 hour', open_time) AS bucket,
       EXTRACT(EPOCH FROM time_bucket('4 hour', open_time))::bigint * 1000 AS id,
       FIRST(open_time, open_time) AS open_time,
       LAST(close_time, close_time) AS close_time,
       FIRST(open_price, open_time) AS open_price,
       LAST(close_price, close_time) AS close_price,
       MAX(high_price) AS high_price,
       MIN(low_price) AS low_price,
       SUM(volume) AS volume
FROM sol_usdt
GROUP BY time_bucket('4 hour', open_time);
-- 为4小时聚合视图添加刷新策略
SELECT add_continuous_aggregate_policy('sol_usdt_4h',
  start_offset => INTERVAL '24 hours',
  end_offset => INTERVAL '4 hours',
  schedule_interval => INTERVAL '10 minutes');


-- 创建一个1天持续聚合视图
CREATE MATERIALIZED VIEW sol_usdt_1d
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 day', open_time) AS bucket,
       EXTRACT(EPOCH FROM time_bucket('1 day', open_time))::bigint * 1000 AS id,
       FIRST(open_time, open_time) AS open_time,
       LAST(close_time, close_time) AS close_time,
       FIRST(open_price, open_time) AS open_price,
       LAST(close_price, close_time) AS close_price,
       MAX(high_price) AS high_price,
       MIN(low_price) AS low_price,
       SUM(volume) AS volume
FROM sol_usdt
GROUP BY time_bucket('1 day', open_time);

-- 为1天聚合视图添加刷新策略
SELECT add_continuous_aggregate_policy('sol_usdt_1d',
  start_offset => INTERVAL '7 days',
  end_offset => INTERVAL '1 day',
  schedule_interval => INTERVAL '1 hour');


-- 创建一个1周持续聚合视图
CREATE MATERIALIZED VIEW sol_usdt_1w
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 week', open_time) AS bucket,
       EXTRACT(EPOCH FROM time_bucket('1 week', open_time))::bigint * 1000 AS id,
       FIRST(open_time, open_time) AS open_time,
       LAST(close_time, close_time) AS close_time,
       FIRST(open_price, open_time) AS open_price,
       LAST(close_price, close_time) AS close_price,
       MAX(high_price) AS high_price,
       MIN(low_price) AS low_price,
       SUM(volume) AS volume
FROM sol_usdt
GROUP BY time_bucket('1 week', open_time);

-- 为1周聚合视图添加刷新策略
SELECT add_continuous_aggregate_policy('sol_usdt_1w',
  start_offset => INTERVAL '4 weeks',
  end_offset => INTERVAL '1 week',
  schedule_interval => INTERVAL '6 hours');

-- 创建一个1个月持续聚合视图
CREATE MATERIALIZED VIEW sol_usdt_1mo
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 month', open_time) AS bucket,
       EXTRACT(EPOCH FROM time_bucket('1 month', open_time))::bigint * 1000 AS id,
       FIRST(open_time, open_time) AS open_time,
       LAST(close_time, close_time) AS close_time,
       FIRST(open_price, open_time) AS open_price,
       LAST(close_price, close_time) AS close_price,
       MAX(high_price) AS high_price,
       MIN(low_price) AS low_price,
       SUM(volume) AS volume
FROM sol_usdt
GROUP BY time_bucket('1 month', open_time);

-- 为1个月聚合视图添加刷新策略
SELECT add_continuous_aggregate_policy('sol_usdt_1mo',
  start_offset => INTERVAL '12 months',
  end_offset => INTERVAL '1 month',
  schedule_interval => INTERVAL '1 day');