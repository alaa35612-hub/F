import importlib.util
import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

_YF_SPEC = importlib.util.find_spec("yfinance")
if _YF_SPEC is not None:
    import yfinance as yf
else:
    yf = None


CONFIG: Dict[str, object] = {
    'i_enableNeural': True,
    'i_hurstPeriod': 100,
    'i_minLookback': 5,
    'i_maxLookback': 20,
    'i_neuralSmoothing': 10,
    'i_ribbonMode': "Adaptive",
    'i_volatilityLookback': 50,
    'i_breathingIntensity': 0.5,
    'i_showExtendedEMAs': True,
    'i_enableWaveEngine': True,
    'i_waveSwingLookback': 8,
    'i_minWaveATR': 2.5,
    'i_minWaveBars': 3,
    'i_useHTFChannel': True,
    'i_channelHTF': "60",
    'i_useHTFWaveFilter': False,
    'i_showWaveLabels': True,
    'i_showProjections': True,
    'i_showWavePolyline': True,
    'i_showExhaustionLine': True,
    'i_exhaustionThreshold': 0.30,
    'i_showMomentumDecay': True,
    'i_angleSmoothing': 5,
    'i_enableMTFMapping': True,
    'i_macroTimeframe': "240",
    'i_requireMacroAlign': True,
    'i_microBreakBoost': True,
    'i_enableSMC': True,
    'i_showOB': True,
    'i_showFVG': True,
    'i_showStructure': True,
    'i_enableChoch': True,
    'i_labelOBFVG': True,
    'i_minDisplacement': 1.5,
    'i_fvgMinSize': 0.3,
    'i_structureLen': 50,
    'i_obMaxAge': 100,
    'i_fvgMaxAge': 50,
    'i_chochCooldown': 10,
    'i_obTransparency': 85,
    'i_enableBreakers': True,
    'i_showBreakers': True,
    'i_breakerExtend': 100,
    'i_breakerTransparency': 80,
    'i_breakerBoost': 4,
    'i_institutionalMode': False,
    'i_mpiPeriod': 17,
    'i_minGrade': "B",
    'i_minConfluence': 5,
    'i_tradeLockBars': 30,
    'i_requirePullback': True,
    'i_useWaveExhaustion': True,
    'i_useWaveEntryZones': True,
    'i_avoidWave5': True,
    'i_useChannelFilter': True,
    'i_signalSize': "Small",
    'i_signalMode': "Balanced",
    'i_enableChop': True,
    'i_adxPeriod': 14,
    'i_adxThreshold': 20,
    'i_choppinessPeriod': 14,
    'i_chopSensitivity': 1.1,
    'i_volumeChopWeight': 1.2,
    'i_chopThreshold': 45.0,
    'i_showChopZones': True,
    'i_enableHTF': True,
    'i_htfTimeframe': "60",
    'i_htfMethod': "Price vs EMA",
    'i_requireHTFAlign': True,
    'i_enableSession': False,
    'i_allowAsia': True,
    'i_allowLondon': True,
    'i_allowNY': True,
    'i_asiaStart': "1800-0300",
    'i_londonStart': "0300-1130",
    'i_nyStart': "0800-1700",
    'i_showTargetLines': True,
    'i_showTargetLabels': True,
    'i_stopATR': 1.5,
    'i_tp1Mult': 1.5,
    'i_tp2Mult': 2.5,
    'i_tp3Mult': 4.0,
    'i_useSwingSL': True,
    'i_useLTFResolution': True,
    'i_ltfTimeframe': "1",
    'i_usePercentile': True,
    'i_percentileLookback': 200,
    'i_percentileThreshold': 75,
    'i_maxConsecLosses': 3,
    'i_enableLossProtect': False,
    'i_exhaustLineWidth': 1,
    'i_exhaustTransparency': 70,
    'i_exhaustDotSize': "Tiny",
    'i_channelTransparency': 50,
    'i_bgOpacity': 95,
    'i_showWaveBarColors': False,
    'i_showWaveTrendlines': True,
    'i_showWaveProjections': True,
    'i_showCenterLine': True,
    'i_showDashboard': True,
    'i_showCombinedPanel': True,
    'i_showWavePanel': True,
    'i_dashboardTransp': 15,
    'i_dashboardBorderTransp': 50,
}


DATA_SETTINGS = {
    "symbol": "BTC-USD",
    "interval": "1h",
    "period": "6mo",
    "bars": 500,
}


@dataclass
class WavePoint:
    index: int
    price: float
    is_high: bool


@dataclass
class ZoneBox:
    start_index: int
    end_index: int
    low: float
    high: float
    label: str
    color: str
    alpha: float


def ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()


def sma(series: pd.Series, length: int) -> pd.Series:
    return series.rolling(window=length, min_periods=length).mean()


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    return pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs(),
    ], axis=1).max(axis=1)


def atr(high: pd.Series, low: pd.Series, close: pd.Series, length: int) -> pd.Series:
    return true_range(high, low, close).rolling(window=length, min_periods=length).mean()


def hurst_exponent(series: pd.Series, period: int) -> pd.Series:
    def hurst_window(values: np.ndarray) -> float:
        if len(values) < period:
            return np.nan
        mean_val = np.mean(values)
        sum_dev = 0.0
        max_dev = 0.0
        min_dev = 0.0
        for val in values[::-1]:
            deviation = val - mean_val
            sum_dev += deviation
            max_dev = max(max_dev, sum_dev)
            min_dev = min(min_dev, sum_dev)
        range_rs = max_dev - min_dev
        std_dev = np.std(values, ddof=0)
        rs_ratio = range_rs / std_dev if std_dev > 0 else 1.0
        hurst = math.log(rs_ratio) / math.log(period) if rs_ratio > 0 else 0.5
        return max(0.2, min(0.8, hurst))

    return series.rolling(window=period, min_periods=period).apply(
        lambda x: hurst_window(np.array(x)), raw=True
    )


def resample_ohlc(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    if timeframe.isdigit():
        rule = f"{int(timeframe)}T"
    else:
        rule = timeframe
    resampled = df.resample(rule).agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    })
    return resampled.dropna()


def pivot_points(series: pd.Series, left: int, right: int, is_high: bool) -> pd.Series:
    window = left + right + 1
    if is_high:
        rolling = series.rolling(window=window, center=True)
        pivots = rolling.max()
        return series.where(series == pivots)
    rolling = series.rolling(window=window, center=True)
    pivots = rolling.min()
    return series.where(series == pivots)


def normalize_between(value: pd.Series, min_val: float, max_val: float) -> pd.Series:
    scaled = (value - value.min()) / (value.max() - value.min())
    return min_val + scaled * (max_val - min_val)


def dmi(high: pd.Series, low: pd.Series, close: pd.Series, length: int) -> Tuple[pd.Series, pd.Series, pd.Series]:
    up_move = high.diff()
    down_move = low.shift(1) - low
    plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0.0)
    minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0.0)
    tr = true_range(high, low, close)
    atr_series = tr.rolling(window=length, min_periods=length).mean()
    plus_di = 100 * (plus_dm.rolling(window=length, min_periods=length).mean() / atr_series)
    minus_di = 100 * (minus_dm.rolling(window=length, min_periods=length).mean() / atr_series)
    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di)).replace([np.inf, -np.inf], 0.0)
    adx = dx.rolling(window=length, min_periods=length).mean()
    return plus_di.fillna(0.0), minus_di.fillna(0.0), adx.fillna(0.0)


def choppiness_index(high: pd.Series, low: pd.Series, close: pd.Series, length: int) -> pd.Series:
    tr = true_range(high, low, close)
    sum_tr = tr.rolling(window=length, min_periods=length).sum()
    highest_high = high.rolling(window=length, min_periods=length).max()
    lowest_low = low.rolling(window=length, min_periods=length).min()
    range_ = (highest_high - lowest_low).replace(0, np.nan)
    return 100 * np.log10(sum_tr / range_) / np.log10(length)


def session_mask(index: pd.DatetimeIndex, session: str) -> pd.Series:
    if not session:
        return pd.Series(True, index=index)
    start, end = session.split('-')
    start_hour = int(start[:2])
    start_min = int(start[2:])
    end_hour = int(end[:2])
    end_min = int(end[2:])
    start_time = pd.to_datetime(index.date) + pd.Timedelta(hours=start_hour, minutes=start_min)
    end_time = pd.to_datetime(index.date) + pd.Timedelta(hours=end_hour, minutes=end_min)
    mask = (index >= start_time) & (index <= end_time)
    if end_time[0] < start_time[0]:
        mask = (index >= start_time) | (index <= end_time)
    return pd.Series(mask, index=index)


def get_mock_data(bars: int) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    base = np.cumsum(rng.normal(0, 1, bars)) + 30000
    high = base + rng.uniform(10, 120, bars)
    low = base - rng.uniform(10, 120, bars)
    open_ = base + rng.uniform(-50, 50, bars)
    close = base + rng.uniform(-50, 50, bars)
    volume = rng.integers(1000, 5000, bars)
    index = pd.date_range(end=pd.Timestamp.utcnow(), periods=bars, freq="H")
    return pd.DataFrame({
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    }, index=index)


def fetch_data() -> pd.DataFrame:
    if yf is None:
        return get_mock_data(DATA_SETTINGS["bars"])
    data = pd.DataFrame()
    try:
        data = yf.download(
            DATA_SETTINGS["symbol"],
            interval=DATA_SETTINGS["interval"],
            period=DATA_SETTINGS["period"],
            progress=False,
        )
    except Exception:
        data = pd.DataFrame()
    if data.empty:
        return get_mock_data(DATA_SETTINGS["bars"])
    data = data.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume",
    })
    return data[["open", "high", "low", "close", "volume"]].dropna()


class WaveDynamicsIndicator:
    def __init__(self, config: Dict[str, object]):
        self.config = config

    def compute_neural_lookback(self, close: pd.Series) -> Tuple[pd.Series, pd.Series]:
        raw_hurst = hurst_exponent(close, int(self.config['i_hurstPeriod'])).fillna(0.5)
        smoothed_hurst = sma(raw_hurst, int(self.config['i_neuralSmoothing'])).fillna(0.5)
        return raw_hurst, smoothed_hurst

    def compute_dynamic_lookback(self, smoothed_hurst: pd.Series) -> pd.Series:
        if not self.config['i_enableNeural']:
            return pd.Series(self.config['i_waveSwingLookback'], index=smoothed_hurst.index)
        hurst_factor = 1.5 - smoothed_hurst
        hurst_factor = hurst_factor.clip(lower=0.5, upper=2.0)
        raw_lookback = self.config['i_waveSwingLookback'] * hurst_factor
        lookback = raw_lookback.round().clip(lower=self.config['i_minLookback'], upper=self.config['i_maxLookback'])
        return lookback.astype(int)

    def compute_ribbon(self, close: pd.Series, atr_series: pd.Series) -> Dict[str, pd.Series]:
        base_lengths = [8, 13, 21, 34, 55, 89, 144, 233]
        ribbon = {}
        for length in base_lengths:
            if self.config['i_ribbonMode'] == "Static":
                adj_length = length
            else:
                scale = atr_series / atr_series.rolling(self.config['i_volatilityLookback']).mean()
                scale = scale.fillna(1.0)
                intensity = self.config['i_breathingIntensity']
                if self.config['i_ribbonMode'] == "Aggressive":
                    intensity *= 1.5
                adj_length = max(2, int(length / (scale.iloc[-1] ** intensity)))
            ribbon[length] = ema(close, adj_length)
        return ribbon

    def compute_wave_points(self, df: pd.DataFrame, lookback: pd.Series, atr_series: pd.Series) -> List[WavePoint]:
        points: List[WavePoint] = []
        for idx in range(len(df)):
            lb = int(lookback.iloc[idx])
            if lb < 2:
                continue
            if idx - lb < 0 or idx + lb >= len(df):
                continue
            window_high = df['high'].iloc[idx - lb: idx + lb + 1]
            window_low = df['low'].iloc[idx - lb: idx + lb + 1]
            if df['high'].iloc[idx] == window_high.max():
                points.append(WavePoint(idx, df['high'].iloc[idx], True))
            if df['low'].iloc[idx] == window_low.min():
                points.append(WavePoint(idx, df['low'].iloc[idx], False))
        points = sorted(points, key=lambda p: p.index)
        filtered: List[WavePoint] = []
        for point in points:
            if not filtered or point.is_high != filtered[-1].is_high:
                filtered.append(point)
            elif point.is_high and point.price > filtered[-1].price:
                filtered[-1] = point
            elif not point.is_high and point.price < filtered[-1].price:
                filtered[-1] = point
        min_wave_bars = int(self.config['i_minWaveBars'])
        min_wave_atr = float(self.config['i_minWaveATR'])
        pruned: List[WavePoint] = []
        for point in filtered:
            if not pruned:
                pruned.append(point)
                continue
            prev = pruned[-1]
            bar_distance = point.index - prev.index
            atr_val = atr_series.iloc[point.index] if point.index < len(atr_series) else np.nan
            wave_size_ok = abs(point.price - prev.price) >= (atr_val * min_wave_atr) if not np.isnan(atr_val) else True
            if bar_distance >= min_wave_bars and wave_size_ok:
                pruned.append(point)
        return pruned

    def detect_order_blocks(self, df: pd.DataFrame, atr_series: pd.Series) -> List[ZoneBox]:
        zones: List[ZoneBox] = []
        displacement = self.config['i_minDisplacement']
        for i in range(2, len(df)):
            body = abs(df['close'].iloc[i - 1] - df['open'].iloc[i - 1])
            atr_val = atr_series.iloc[i - 1]
            if np.isnan(atr_val) or atr_val == 0:
                continue
            if body < atr_val * 0.2:
                continue
            move = abs(df['close'].iloc[i] - df['close'].iloc[i - 1])
            if move < atr_val * displacement:
                continue
            bullish_ob = df['close'].iloc[i - 1] < df['open'].iloc[i - 1] and df['close'].iloc[i] > df['open'].iloc[i]
            bearish_ob = df['close'].iloc[i - 1] > df['open'].iloc[i - 1] and df['close'].iloc[i] < df['open'].iloc[i]
            if bullish_ob:
                zones.append(ZoneBox(i - 1, i + int(self.config['i_obMaxAge']), df['low'].iloc[i - 1], df['open'].iloc[i - 1], "Bullish OB", "green", 0.2))
            if bearish_ob:
                zones.append(ZoneBox(i - 1, i + int(self.config['i_obMaxAge']), df['open'].iloc[i - 1], df['high'].iloc[i - 1], "Bearish OB", "red", 0.2))
        return zones

    def detect_fvg(self, df: pd.DataFrame) -> List[ZoneBox]:
        zones: List[ZoneBox] = []
        min_size = self.config['i_fvgMinSize']
        for i in range(2, len(df)):
            if df['low'].iloc[i] > df['high'].iloc[i - 2]:
                gap = df['low'].iloc[i] - df['high'].iloc[i - 2]
                if gap >= min_size:
                    zones.append(ZoneBox(i - 2, i + int(self.config['i_fvgMaxAge']), df['high'].iloc[i - 2], df['low'].iloc[i], "Bullish FVG", "cyan", 0.15))
            if df['high'].iloc[i] < df['low'].iloc[i - 2]:
                gap = df['low'].iloc[i - 2] - df['high'].iloc[i]
                if gap >= min_size:
                    zones.append(ZoneBox(i - 2, i + int(self.config['i_fvgMaxAge']), df['high'].iloc[i], df['low'].iloc[i - 2], "Bearish FVG", "orange", 0.15))
        return zones

    def compute_dashboard(self, df: pd.DataFrame, hurst: float, trend_score: float, regime: str, htf_bias: str) -> str:
        grade_map = {"A": 3, "B": 2, "C": 1}
        min_grade = grade_map.get(self.config['i_minGrade'], 2)
        confluence = int(trend_score * 10)
        grade = "A" if confluence >= 8 else "B" if confluence >= 5 else "C"
        if grade_map[grade] < min_grade:
            grade = self.config['i_minGrade']
        return (
            f"Wave Dynamics\n"
            f"Hurst: {hurst:.2f}\n"
            f"Trend Score: {trend_score:.2f}\n"
            f"Regime: {regime}\n"
            f"HTF Bias: {htf_bias}\n"
            f"Confluence: {confluence}/10\n"
            f"Grade: {grade}"
        )

    def compute_wave_projections(self, wave_points: List[WavePoint]) -> List[Tuple[int, float]]:
        if len(wave_points) < 2:
            return []
        last = wave_points[-1]
        prev = wave_points[-2]
        move = last.price - prev.price
        projections = []
        for ratio in (0.618, 1.0, 1.618):
            projections.append((last.index, last.price + move * ratio))
        return projections

    def compute_chop_intensity(self, df: pd.DataFrame, atr_series: pd.Series) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        plus_di, minus_di, adx_val = dmi(df['high'], df['low'], df['close'], int(self.config['i_adxPeriod']))
        choppiness = choppiness_index(df['high'], df['low'], df['close'], int(self.config['i_choppinessPeriod']))
        range_high = df['high'].rolling(window=20, min_periods=20).max()
        range_low = df['low'].rolling(window=20, min_periods=20).min()
        current_range = range_high - range_low
        avg_range = (df['high'].rolling(window=20, min_periods=20).max() - df['low'].rolling(window=20, min_periods=20).min()).rolling(window=50, min_periods=50).mean()
        range_compression = (current_range / avg_range).fillna(1.0)
        channel_position = ((df['close'] - range_low) / (range_high - range_low)).fillna(0.5)

        adx_chop_score = pd.Series(0.0, index=df.index)
        adx_ranging = adx_val < self.config['i_adxThreshold']
        adx_chop_score = np.where(
            adx_ranging,
            30.0 * (1.0 - (adx_val / self.config['i_adxThreshold'])),
            adx_chop_score,
        )
        adx_chop_score = np.where(
            (adx_val >= self.config['i_adxThreshold']) & (adx_val < 25),
            15.0 * (1.0 - ((adx_val - self.config['i_adxThreshold']) / 10.0)),
            adx_chop_score,
        )
        adx_chop_score = np.clip(adx_chop_score * self.config['i_chopSensitivity'], 0.0, 30.0)

        chop_idx_score = pd.Series(0.0, index=df.index)
        chop_idx_score = np.where(
            choppiness > 61.8,
            25.0 * ((choppiness - 61.8) / (100.0 - 61.8)),
            chop_idx_score,
        )
        chop_idx_score = np.where(
            (choppiness > 50) & (choppiness <= 61.8),
            12.0 * ((choppiness - 50.0) / 11.8),
            chop_idx_score,
        )
        chop_idx_score = np.clip(chop_idx_score * self.config['i_chopSensitivity'], 0.0, 25.0)

        range_chop_score = pd.Series(0.0, index=df.index)
        is_range_compressed = range_compression < 0.6
        range_chop_score = np.where(
            is_range_compressed,
            20.0 * (1.0 - range_compression),
            range_chop_score,
        )
        range_chop_score = np.where(
            (range_compression >= 0.6) & (range_compression < 0.8),
            10.0 * (0.8 - range_compression) / 0.2,
            range_chop_score,
        )
        range_chop_score = np.clip(range_chop_score * self.config['i_chopSensitivity'], 0.0, 20.0)

        dist_from_center = (channel_position - 0.5).abs()
        channel_chop_score = pd.Series(0.0, index=df.index)
        channel_chop_score = np.where(
            dist_from_center < 0.2,
            15.0 * (1.0 - (dist_from_center / 0.2)),
            channel_chop_score,
        )
        channel_chop_score = np.where(
            (dist_from_center >= 0.2) & (dist_from_center < 0.35),
            8.0 * (0.35 - dist_from_center) / 0.15,
            channel_chop_score,
        )
        channel_chop_score = np.clip(channel_chop_score, 0.0, 15.0)

        avg_volume = df['volume'].rolling(window=20, min_periods=20).mean()
        relative_volume = (df['volume'] / avg_volume).fillna(1.0)
        volume_score = np.where(relative_volume < 0.5, 10.0, 0.0)
        volume_score = np.where((relative_volume >= 0.5) & (relative_volume < 0.7), 7.0, volume_score)
        volume_score = np.where((relative_volume >= 0.7) & (relative_volume < 0.9), 4.0, volume_score)
        volume_score = np.where((relative_volume >= 0.9) & (relative_volume < 1.1), 2.0, volume_score)
        volume_score = volume_score * self.config['i_volumeChopWeight']

        chop_intensity = adx_chop_score + chop_idx_score + range_chop_score + channel_chop_score + volume_score
        chop_intensity = np.clip(chop_intensity, 0.0, 100.0)
        return pd.Series(chop_intensity, index=df.index), adx_val, choppiness, range_compression

    def compute_htf_bias(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series, pd.Series]:
        htf = resample_ohlc(df, str(self.config['i_htfTimeframe']))
        htf_ema8 = ema(htf['close'], 8)
        htf_ema21 = ema(htf['close'], 21)
        htf_ema55 = ema(htf['close'], 55)
        _, _, htf_adx = dmi(htf['high'], htf['low'], htf['close'], 14)
        htf_bias = pd.Series(0, index=htf.index)
        if self.config['i_htfMethod'] == "EMA Stack":
            htf_bias = np.where(htf_ema8 > htf_ema21, 1, htf_bias)
            htf_bias = np.where(htf_ema8 < htf_ema21, -1, htf_bias)
        elif self.config['i_htfMethod'] == "Price vs EMA":
            htf_bias = np.where(htf['close'] > htf_ema21, 1, htf_bias)
            htf_bias = np.where(htf['close'] < htf_ema21, -1, htf_bias)
        else:
            htf_bias = np.where(htf_adx > 20, np.where(htf['close'] > htf_ema21, 1, -1), htf_bias)

        htf_bias = pd.Series(htf_bias, index=htf.index).reindex(df.index, method='ffill').fillna(0)
        return (
            htf_ema8.reindex(df.index, method='ffill'),
            htf_ema21.reindex(df.index, method='ffill'),
            htf_ema55.reindex(df.index, method='ffill'),
            htf['close'].reindex(df.index, method='ffill'),
            htf_adx.reindex(df.index, method='ffill'),
            htf_bias,
        )

    def run(self, df: pd.DataFrame) -> Dict[str, object]:
        atr_series = atr(df['high'], df['low'], df['close'], 14)
        raw_hurst, smoothed_hurst = self.compute_neural_lookback(df['close'])
        lookback = self.compute_dynamic_lookback(smoothed_hurst)
        wave_points = self.compute_wave_points(df, lookback, atr_series) if self.config['i_enableWaveEngine'] else []
        hurst_latest = smoothed_hurst.iloc[-1]
        ribbon = self.compute_ribbon(df['close'], atr_series)
        trend_score = ((df['close'].iloc[-1] - df['close'].iloc[-50]) / df['close'].iloc[-50]) if len(df) > 50 else 0
        order_blocks = self.detect_order_blocks(df, atr_series) if self.config['i_enableSMC'] else []
        fvgs = self.detect_fvg(df) if self.config['i_enableSMC'] else []
        chop_intensity, adx_val, choppiness, range_compression = self.compute_chop_intensity(df, atr_series)
        market_regime = "WEAK_TREND"
        if (adx_val.iloc[-1] >= 30) and (choppiness.iloc[-1] <= 61.8):
            market_regime = "STRONG_TREND"
        elif (adx_val.iloc[-1] >= self.config['i_adxThreshold']) and (chop_intensity.iloc[-1] < 40):
            market_regime = "TRENDING"
        elif (chop_intensity.iloc[-1] >= 60) and (range_compression.iloc[-1] < 0.6):
            market_regime = "COMPRESSION"
        elif chop_intensity.iloc[-1] >= 50:
            market_regime = "RANGING"
        elif chop_intensity.iloc[-1] >= 35:
            market_regime = "TRANSITIONING"

        if self.config['i_enableHTF']:
            htf_ema8, htf_ema21, htf_ema55, htf_close, htf_adx, htf_bias = self.compute_htf_bias(df)
            htf_bias_text = "BULLISH" if htf_bias.iloc[-1] > 0 else "BEARISH" if htf_bias.iloc[-1] < 0 else "NEUTRAL"
        else:
            htf_bias = pd.Series(0, index=df.index)
            htf_bias_text = "NEUTRAL"
        dashboard = self.compute_dashboard(df, hurst_latest, trend_score, market_regime, htf_bias_text)
        projections = self.compute_wave_projections(wave_points) if self.config['i_showProjections'] else []
        return {
            "atr": atr_series,
            "lookback": lookback,
            "wave_points": wave_points,
            "projections": projections,
            "ribbon": ribbon,
            "order_blocks": order_blocks,
            "fvgs": fvgs,
            "chop_intensity": chop_intensity,
            "market_regime": market_regime,
            "htf_bias": htf_bias,
            "dashboard": dashboard,
        }


def plot_indicator(df: pd.DataFrame, results: Dict[str, object]) -> None:
    fig, ax = plt.subplots(figsize=(14, 8))
    dates = mdates.date2num(df.index.to_pydatetime())
    width = 0.02 * (dates[-1] - dates[0]) / len(dates)
    if CONFIG['i_enableChop'] and CONFIG['i_showChopZones']:
        chop_intensity = results.get('chop_intensity')
        if chop_intensity is not None:
            dead_zone = chop_intensity >= CONFIG['i_chopThreshold']
            for i, is_dead in enumerate(dead_zone):
                if is_dead:
                    ax.axvspan(dates[i] - width / 2, dates[i] + width / 2, color='gray', alpha=0.1)
    for i, (date, row) in enumerate(df.iterrows()):
        color = "green" if row['close'] >= row['open'] else "red"
        ax.plot([dates[i], dates[i]], [row['low'], row['high']], color=color, linewidth=1)
        ax.add_patch(plt.Rectangle(
            (dates[i] - width / 2, min(row['open'], row['close'])),
            width,
            abs(row['close'] - row['open']),
            color=color,
            alpha=0.8,
        ))

    for length, series in results['ribbon'].items():
        if length > 55 and not CONFIG['i_showExtendedEMAs']:
            continue
        ax.plot(dates, series, linewidth=0.8, alpha=0.7, label=f"EMA {length}")

    wave_points: List[WavePoint] = results['wave_points']
    if CONFIG['i_showWavePolyline'] and wave_points:
        ax.plot(
            [dates[p.index] for p in wave_points],
            [p.price for p in wave_points],
            color="purple",
            linewidth=1.5,
        )
    if CONFIG['i_showWaveLabels']:
        wave_number = 1
        for point in wave_points:
            ax.text(dates[point.index], point.price, str(wave_number), color="purple", fontsize=8)
            wave_number = wave_number + 1 if wave_number < 5 else 1
    if CONFIG['i_showProjections']:
        for idx, price in results.get('projections', []):
            ax.hlines(price, dates[max(idx - 5, 0)], dates[min(idx + 20, len(dates) - 1)], colors="blue", linestyles="dashed", linewidth=1)

    for zone in results['order_blocks'] + results['fvgs']:
        start = dates[zone.start_index]
        end = dates[min(zone.end_index, len(dates) - 1)]
        ax.add_patch(plt.Rectangle(
            (start, zone.low),
            end - start,
            zone.high - zone.low,
            color=zone.color,
            alpha=zone.alpha,
        ))
        if CONFIG['i_labelOBFVG']:
            ax.text(start, zone.high, zone.label, color=zone.color, fontsize=7)

    ax.text(
        0.02,
        0.98,
        results['dashboard'],
        transform=ax.transAxes,
        verticalalignment='top',
        bbox=dict(facecolor='black', alpha=0.6, boxstyle='round'),
        color='white',
        fontsize=9,
    )

    ax.set_title("Wave Dynamics - Neural Adaptive Engine")
    ax.xaxis_date()
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=8)
    plt.tight_layout()
    plt.show()


def main() -> None:
    df = fetch_data()
    indicator = WaveDynamicsIndicator(CONFIG)
    results = indicator.run(df)
    plot_indicator(df, results)


if __name__ == "__main__":
    main()
