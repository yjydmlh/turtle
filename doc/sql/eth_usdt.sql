
-- 建表语句
create table eth_usdt
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

alter table eth_usdt
    owner to postgres;

create index idx_eth_usdt_timestamp
    on eth_usdt (timestamp);

create index idx_eth_usdt_open_time
    on eth_usdt (open_time desc);

-- 表注释
COMMENT ON TABLE eth_usdt IS 'eth/USDT 交易对 K线/行情数据表';

-- 字段注释
COMMENT ON COLUMN eth_usdt.id IS '主键ID';
COMMENT ON COLUMN eth_usdt.timestamp IS 'Unix时间戳(毫秒)也是开盘时间';
COMMENT ON COLUMN eth_usdt.open_time IS '开盘时间';
COMMENT ON COLUMN eth_usdt.close_time IS '收盘时间';
COMMENT ON COLUMN eth_usdt.open_price IS '开盘价';
COMMENT ON COLUMN eth_usdt.high_price IS '最高价';
COMMENT ON COLUMN eth_usdt.low_price IS '最低价';
COMMENT ON COLUMN eth_usdt.close_price IS '收盘价';
COMMENT ON COLUMN eth_usdt.volume IS '成交量(eth)';
COMMENT ON COLUMN eth_usdt.quote_volume IS '成交额(USDT)';
COMMENT ON COLUMN eth_usdt.trades_count IS '成交笔数';
COMMENT ON COLUMN eth_usdt.taker_buy_volume IS '主动买入成交量(Taker)';
COMMENT ON COLUMN eth_usdt.taker_buy_quote_volume IS '主动买入成交额(Taker)';
COMMENT ON COLUMN eth_usdt.created_at IS '数据入库时间';
COMMENT ON COLUMN eth_usdt.updated_at IS '数据更新时间';


-- TODO 创建超表语句