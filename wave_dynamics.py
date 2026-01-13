import importlib.util
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

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
        n = len(values)
        if n < 20:
            return np.nan
        mean_val = np.mean(values)
        dev = values - mean_val
        cumulative = np.cumsum(dev)
        r = cumulative.max() - cumulative.min()
        s = np.std(values)
        if s == 0:
            return 0.5
        return math.log(r / s) / math.log(n)

    return series.rolling(window=period, min_periods=period).apply(
        lambda x: hurst_window(np.array(x)), raw=False
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

    def compute_neural_lookback(self, close: pd.Series) -> pd.Series:
        hurst = hurst_exponent(close, int(self.config['i_hurstPeriod']))
        hurst = hurst.fillna(0.5)
        normalized = normalize_between(hurst, self.config['i_minLookback'], self.config['i_maxLookback'])
        smoothing = int(self.config['i_neuralSmoothing'])
        return ema(normalized, smoothing).round().clip(lower=3)

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

    def compute_wave_points(self, df: pd.DataFrame, lookback: pd.Series) -> List[WavePoint]:
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
        return filtered

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

    def compute_dashboard(self, df: pd.DataFrame, hurst: float, trend_score: float) -> str:
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
            f"Confluence: {confluence}/10\n"
            f"Grade: {grade}"
        )

    def run(self, df: pd.DataFrame) -> Dict[str, object]:
        atr_series = atr(df['high'], df['low'], df['close'], 14)
        lookback = self.compute_neural_lookback(df['close'])
        wave_points = self.compute_wave_points(df, lookback)
        hurst_series = hurst_exponent(df['close'], int(self.config['i_hurstPeriod'])).fillna(0.5)
        hurst_latest = hurst_series.iloc[-1]
        ribbon = self.compute_ribbon(df['close'], atr_series)
        trend_score = ((df['close'].iloc[-1] - df['close'].iloc[-50]) / df['close'].iloc[-50]) if len(df) > 50 else 0
        order_blocks = self.detect_order_blocks(df, atr_series) if self.config['i_enableSMC'] else []
        fvgs = self.detect_fvg(df) if self.config['i_enableSMC'] else []
        dashboard = self.compute_dashboard(df, hurst_latest, trend_score)
        return {
            "atr": atr_series,
            "lookback": lookback,
            "wave_points": wave_points,
            "ribbon": ribbon,
            "order_blocks": order_blocks,
            "fvgs": fvgs,
            "dashboard": dashboard,
        }


def plot_indicator(df: pd.DataFrame, results: Dict[str, object]) -> None:
    fig, ax = plt.subplots(figsize=(14, 8))
    dates = mdates.date2num(df.index.to_pydatetime())
    width = 0.02 * (dates[-1] - dates[0]) / len(dates)
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
