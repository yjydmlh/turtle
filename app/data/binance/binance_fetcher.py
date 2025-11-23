"""
Binance数据获取器 - 纯HTTP实现
直接调用Binance API，无第三方依赖
"""
import json
import ssl
from urllib import request, parse
from datetime import datetime, timedelta


class BinanceFetcher:
    """Binance数据获取器"""
    BASE_URL = "https://api.binance.com"


    def __init__(self):
        # 禁用SSL验证避免Windows证书问题
        self.ctx = ssl.create_default_context()
        self.ctx.check_hostname = False
        self.ctx.verify_mode = ssl.CERT_NONE
    
    def _request(self, endpoint, params=None):
        """发送HTTP请求"""
        url = f"{self.BASE_URL}{endpoint}"
        if params:
            url = f"{url}?{parse.urlencode(params)}"
        
        req = request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0')
        
        with request.urlopen(req, timeout=30, context=self.ctx) as resp:
            return json.loads(resp.read())
    
    def get_klines(self, symbol, interval='1h', limit=500):
        """
        获取K线数据
        symbol: 交易对，如 'BTCUSDT'
        interval: 周期，如 '1m','5m','1h','1d'
        limit: 数量，最大1000
        """
        params = {
            'symbol': symbol.upper().replace('/', ''),
            'interval': interval,
            'limit': min(limit, 1000)
        }
        return self._request('/api/v3/klines', params)
    
    def get_klines_range(self, symbol, interval, start_time, end_time):
        """
        获取时间范围内的所有K线数据
        start_time/end_time: datetime对象
        """
        start_ms = int(start_time.timestamp() * 1000)
        end_ms = int(end_time.timestamp() * 1000)
        
        all_data = []
        current = start_ms
        
        while current < end_ms:
            params = {
                'symbol': symbol.upper().replace('/', ''),
                'interval': interval,
                'startTime': current,
                'endTime': end_ms,
                'limit': 1000
            }
            
            klines = self._request('/api/v3/klines', params)
            if not klines:
                break
            
            all_data.extend(klines)
            current = klines[-1][6] + 1  # 最后一条的收盘时间+1
            
            if current >= end_ms:
                break
        
        return all_data
    
    def get_price(self, symbol):
        """获取最新价格"""
        params = {'symbol': symbol.upper().replace('/', '')}
        return self._request('/api/v3/ticker/price', params)
    
    def to_dataframe(self, klines):
        """转换为DataFrame格式（需要pandas）"""
        import pandas as pd
        df = pd.DataFrame(klines, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_vol',
            'taker_buy_quote_vol', 'ignore'
        ])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume']:
            df[col] = df[col].astype(float)
        return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
    def save_csv(self, klines, filename):
        """保存为CSV"""
        with open(filename, 'w') as f:
            f.write('time,open,high,low,close,volume\n')
            for k in klines:
                time_str = datetime.fromtimestamp(k[0]/1000).strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{time_str},{k[1]},{k[2]},{k[3]},{k[4]},{k[5]}\n")


# 命令行使用
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("用法: python binance_fetcher.py <交易对> <周期> [小时数]")
        print("示例: python binance_fetcher.py BTCUSDT 1h 24")
        sys.exit(1)
    
    symbol = sys.argv[1]
    interval = sys.argv[2]
    hours = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    
    fetcher = BinanceFetcher()
    
    # 获取数据
    end = datetime.now()
    start = end - timedelta(hours=hours)
    klines = fetcher.get_klines_range(symbol, interval, start, end)
    
    # 保存
    filename = f"{symbol}_{interval}_{hours}h.csv"
    fetcher.save_csv(klines, filename)
    
    print(f"✅ 获取 {len(klines)} 条数据，已保存到 {filename}")

