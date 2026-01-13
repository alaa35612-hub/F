"""Wave Dynamics - Neural Adaptive Engine (Python port).

Standalone script for Android/Pydroid environments using only pandas, numpy,
matplotlib, math, and optional yfinance for data.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle


# =============================
# CONFIG (Inputs / Defaults)
# =============================
@dataclass
class WaveDynamicsConfig:
    # 🧠 NEURAL ADAPTIVE ENGINE
    enable_neural: bool = True
    hurst_period: int = 100
    min_lookback: int = 5
    max_lookback: int = 20
    neural_smoothing: int = 10

    # 🌊 ADAPTIVE EQUILIBRIUM RIBBON
    ribbon_mode: str = "Adaptive"  # Static, Adaptive, Aggressive
    volatility_lookback: int = 50
    breathing_intensity: float = 0.5
    show_extended_emas: bool = True

    # 〰️ WAVE CHANNEL & STRUCTURE
    enable_wave_engine: bool = True
    wave_swing_lookback: int = 8
    min_wave_atr: float = 2.5
    min_wave_bars: int = 3
    use_htf_channel: bool = True
    channel_htf: str = "60"  # minutes
    use_htf_wave_filter: bool = False
    show_wave_labels: bool = True
    show_projections: bool = True
    show_wave_polyline: bool = True
    show_exhaustion_line: bool = True
    exhaustion_threshold: float = 0.30
    show_momentum_decay: bool = True
    angle_smoothing: int = 5

    # 🔗 MTF STRUCTURE MAPPING
    enable_mtf_mapping: bool = True
    macro_timeframe: str = "240"  # minutes
    require_macro_align: bool = True
    micro_break_boost: bool = True

    # 🏦 SMART MONEY CONCEPTS
    enable_smc: bool = True
    show_ob: bool = True
    show_fvg: bool = True
    show_structure: bool = True
    enable_choch: bool = True
    label_ob_fvg: bool = True
    min_displacement: float = 1.5
    fvg_min_size: float = 0.3
    structure_len: int = 50
    ob_max_age: int = 100
    fvg_max_age: int = 50
    choch_cooldown: int = 10
    ob_transparency: int = 85

    # 💥 BREAKER BLOCKS
    enable_breakers: bool = True
    show_breakers: bool = True
    breaker_extend: int = 100
    breaker_transparency: int = 80
    breaker_boost: int = 4
    color_breaker: str = "#9C27B0"

    # General
    symbol: str = "BTC-USD"
    interval: str = "1h"
    lookback: str = "90d"
    seed: int = 7


# =============================
# Helper Functions (Pine replacements)
# =============================

def ema(series: pd.Series, length: int) -> pd.Series:
    return series.ewm(span=length, adjust=False).mean()


def true_range(df: pd.DataFrame) -> pd.Series:
    prev_close = df["Close"].shift(1)
    ranges = pd.concat(
        [
            df["High"] - df["Low"],
            (df["High"] - prev_close).abs(),
            (df["Low"] - prev_close).abs(),
        ],
        axis=1,
    )
    return ranges.max(axis=1)


def atr(df: pd.DataFrame, length: int = 14) -> pd.Series:
    return true_range(df).rolling(length).mean()


def hurst_exponent(series: pd.Series, window: int) -> pd.Series:
    """Rolling Hurst exponent using rescaled range approximation."""
    hurst_vals = []
    values = series.values
    for i in range(len(series)):
        if i < window:
            hurst_vals.append(np.nan)
            continue
        window_vals = values[i - window : i]
        mean_adj = window_vals - window_vals.mean()
        cumulative = np.cumsum(mean_adj)
        r = cumulative.max() - cumulative.min()
        s = window_vals.std()
        if s == 0:
            hurst_vals.append(0.5)
        else:
            hurst_vals.append(math.log(r / s) / math.log(window))
    return pd.Series(hurst_vals, index=series.index)


def dynamic_lookback(base: int, hurst: pd.Series, cfg: WaveDynamicsConfig) -> pd.Series:
    """Scale base lookback based on hurst exponent."""
    normalized = (hurst - 0.5).clip(-0.25, 0.25) / 0.25
    scale = 1 - normalized
    scaled = base * scale
    scaled = scaled.clip(cfg.min_lookback, cfg.max_lookback)
    return scaled.rolling(cfg.neural_smoothing).mean().round().fillna(base)


def pivots(series: pd.Series, left: int, right: int, is_high: bool) -> pd.Series:
    vals = series.values
    pivot_flags = np.full(len(series), False)
    for i in range(left, len(series) - right):
        window = vals[i - left : i + right + 1]
        center = vals[i]
        if is_high and center == window.max():
            pivot_flags[i] = True
        if not is_high and center == window.min():
            pivot_flags[i] = True
    return pd.Series(pivot_flags, index=series.index)


def resample_ohlc(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    minutes = int(timeframe)
    rule = f"{minutes}T"
    resampled = df.resample(rule).agg(
        {
            "Open": "first",
            "High": "max",
            "Low": "min",
            "Close": "last",
            "Volume": "sum",
        }
    )
    return resampled.dropna()


def generate_mock_data(rows: int, seed: int = 7) -> pd.DataFrame:
    random.seed(seed)
    np.random.seed(seed)
    prices = [20000]
    for _ in range(rows - 1):
        prices.append(prices[-1] * (1 + np.random.normal(0, 0.002)))
    prices = np.array(prices)
    highs = prices * (1 + np.random.uniform(0.0005, 0.01, size=rows))
    lows = prices * (1 - np.random.uniform(0.0005, 0.01, size=rows))
    opens = prices * (1 + np.random.uniform(-0.002, 0.002, size=rows))
    closes = prices
    volume = np.random.randint(100, 1000, size=rows)
    idx = pd.date_range(end=pd.Timestamp.utcnow(), periods=rows, freq="H")
    return pd.DataFrame(
        {
            "Open": opens,
            "High": highs,
            "Low": lows,
            "Close": closes,
            "Volume": volume,
        },
        index=idx,
    )


# =============================
# Indicator Engine
# =============================
class WaveDynamicsIndicator:
    def __init__(self, cfg: WaveDynamicsConfig):
        self.cfg = cfg

    def _adaptive_ema_lengths(self, base_lengths: List[int], atr_series: pd.Series, price: pd.Series) -> List[int]:
        if self.cfg.ribbon_mode == "Static":
            return base_lengths
        vol = atr_series / price
        vol = vol.fillna(vol.mean())
        multiplier = 1 + (vol - vol.mean()) * self.cfg.breathing_intensity
        if self.cfg.ribbon_mode == "Aggressive":
            multiplier *= 0.8
        adjusted = [max(2, int(length * multiplier.iloc[-1])) for length in base_lengths]
        return adjusted

    def compute(self, df: pd.DataFrame) -> Dict[str, pd.Series]:
        close = df["Close"]
        atr14 = atr(df, 14)

        # Neural engine
        hurst = hurst_exponent(close, self.cfg.hurst_period)
        swing_lookback = (
            dynamic_lookback(self.cfg.wave_swing_lookback, hurst, self.cfg)
            if self.cfg.enable_neural
            else pd.Series(self.cfg.wave_swing_lookback, index=df.index)
        )

        # Ribbon
        base_lengths = [8, 13, 21, 34, 55]
        if self.cfg.show_extended_emas:
            base_lengths += [89, 144, 233]
        ema_lengths = self._adaptive_ema_lengths(base_lengths, atr14, close)
        emas = {f"ema_{length}": ema(close, length) for length in ema_lengths}

        # Multi-timeframe data (channel + macro structure)
        htf_bias = pd.Series(0, index=df.index)
        channel_high = pd.Series(np.nan, index=df.index)
        channel_low = pd.Series(np.nan, index=df.index)
        channel_mid = pd.Series(np.nan, index=df.index)
        if self.cfg.use_htf_channel:
            htf_df = resample_ohlc(df, self.cfg.channel_htf)
            if not htf_df.empty:
                htf_high = htf_df["High"].rolling(self.cfg.wave_swing_lookback).max()
                htf_low = htf_df["Low"].rolling(self.cfg.wave_swing_lookback).min()
                htf_mid = (htf_high + htf_low) / 2
                channel_high = htf_high.reindex(df.index, method="ffill")
                channel_low = htf_low.reindex(df.index, method="ffill")
                channel_mid = htf_mid.reindex(df.index, method="ffill")

        if self.cfg.enable_mtf_mapping:
            macro_df = resample_ohlc(df, self.cfg.macro_timeframe)
            if not macro_df.empty:
                macro_high = pivots(macro_df["High"], 2, 2, True)
                macro_low = pivots(macro_df["Low"], 2, 2, False)
                macro_bias = pd.Series(0, index=macro_df.index)
                last_high = np.nan
                last_low = np.nan
                for idx in macro_df.index:
                    if macro_high.loc[idx]:
                        last_high = macro_df.loc[idx, "High"]
                    if macro_low.loc[idx]:
                        last_low = macro_df.loc[idx, "Low"]
                    if not np.isnan(last_high) and not np.isnan(last_low):
                        if macro_df.loc[idx, "Close"] > last_high:
                            macro_bias.loc[idx] = 1
                        elif macro_df.loc[idx, "Close"] < last_low:
                            macro_bias.loc[idx] = -1
                        else:
                            macro_bias.loc[idx] = macro_bias.shift(1).loc[idx]
                htf_bias = macro_bias.reindex(df.index, method="ffill").fillna(0)

        # Wave pivots
        lookback = int(swing_lookback.iloc[-1]) if len(swing_lookback) else self.cfg.wave_swing_lookback
        pivot_high = pivots(df["High"], lookback, lookback, True)
        pivot_low = pivots(df["Low"], lookback, lookback, False)

        # Build wave points
        wave_points: List[Tuple[pd.Timestamp, float]] = []
        direction = 0
        for idx in df.index:
            if pivot_high.loc[idx]:
                if direction >= 0:
                    wave_points.append((idx, df.loc[idx, "High"]))
                    direction = -1
            if pivot_low.loc[idx]:
                if direction <= 0:
                    wave_points.append((idx, df.loc[idx, "Low"]))
                    direction = 1
        wave_points = wave_points[-6:]

        # Momentum/exhaustion
        momentum = close.diff().rolling(self.cfg.angle_smoothing).mean()
        momentum_decay = momentum / momentum.abs().rolling(10).max()
        exhaustion = momentum_decay.abs() < self.cfg.exhaustion_threshold

        # SMC - simple OB/FVG proxies
        ob_zones = []
        if self.cfg.enable_smc:
            for i in range(2, len(df)):
                body = abs(df["Close"].iloc[i - 1] - df["Open"].iloc[i - 1])
                displacement = body / atr14.iloc[i - 1] if atr14.iloc[i - 1] else 0
                if displacement >= self.cfg.min_displacement:
                    ob_zones.append((df.index[i - 1], df["Open"].iloc[i - 1], df["Close"].iloc[i - 1]))

        ob_zones = [
            zone for zone in ob_zones if (df.index[-1] - zone[0]).days * 24 <= self.cfg.ob_max_age
        ]

        fvg_zones = []
        if self.cfg.enable_smc:
            for i in range(2, len(df)):
                gap = df["Low"].iloc[i] - df["High"].iloc[i - 2]
                gap_size = abs(gap) / atr14.iloc[i] if atr14.iloc[i] else 0
                if gap_size >= self.cfg.fvg_min_size:
                    fvg_zones.append((df.index[i], df["High"].iloc[i - 2], df["Low"].iloc[i]))

        fvg_zones = [
            zone for zone in fvg_zones if (df.index[-1] - zone[0]).days * 24 <= self.cfg.fvg_max_age
        ]

        return {
            "atr": atr14,
            "hurst": hurst,
            "swing_lookback": swing_lookback,
            "pivot_high": pivot_high,
            "pivot_low": pivot_low,
            "momentum_decay": momentum_decay,
            "exhaustion": exhaustion,
            "wave_points": wave_points,
            "ob_zones": ob_zones,
            "fvg_zones": fvg_zones,
            "channel_high": channel_high,
            "channel_low": channel_low,
            "channel_mid": channel_mid,
            "htf_bias": htf_bias,
            **emas,
        }

    def plot(self, df: pd.DataFrame, outputs: Dict[str, pd.Series]) -> None:
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.set_title("Wave Dynamics - Neural Adaptive Engine")

        # Candles
        dates = mdates.date2num(df.index)
        candle_width = 0.02 * (dates[-1] - dates[0]) / len(dates)
        for idx, (date, row) in enumerate(df.iterrows()):
            color = "#26A69A" if row["Close"] >= row["Open"] else "#EF5350"
            ax.plot([dates[idx], dates[idx]], [row["Low"], row["High"]], color=color, linewidth=1)
            rect = Rectangle(
                (dates[idx] - candle_width / 2, min(row["Open"], row["Close"])),
                candle_width,
                abs(row["Close"] - row["Open"]),
                facecolor=color,
                edgecolor=color,
                alpha=0.8,
            )
            ax.add_patch(rect)

        # Ribbon EMAs
        for key, series in outputs.items():
            if key.startswith("ema_"):
                ax.plot(df.index, series, linewidth=1, alpha=0.7)

        # HTF channel
        if self.cfg.use_htf_channel:
            ax.plot(df.index, outputs["channel_high"], color="#5E81AC", linewidth=1, alpha=0.6)
            ax.plot(df.index, outputs["channel_low"], color="#5E81AC", linewidth=1, alpha=0.6)
            ax.plot(df.index, outputs["channel_mid"], color="#81A1C1", linewidth=1, alpha=0.6)

        # Wave polyline
        if self.cfg.enable_wave_engine and outputs["wave_points"]:
            points = outputs["wave_points"]
            x_vals = [p[0] for p in points]
            y_vals = [p[1] for p in points]
            if self.cfg.show_wave_polyline:
                ax.plot(x_vals, y_vals, color="#FFD700", linewidth=2)
            if self.cfg.show_wave_labels:
                for i, (x_val, y_val) in enumerate(points, start=1):
                    ax.text(x_val, y_val, str(i), color="#FFD700", fontsize=9)

        # SMC zones
        for idx, low, high in outputs["ob_zones"]:
            ax.axhspan(min(low, high), max(low, high), color="#4CAF50", alpha=0.15)
        for idx, high, low in outputs["fvg_zones"]:
            ax.axhspan(min(low, high), max(low, high), color="#2196F3", alpha=0.12)

        # Dashboard
        latest_hurst = outputs["hurst"].iloc[-1]
        dashboard = (
            f"Hurst: {latest_hurst:.2f}\n"
            f"ATR: {outputs['atr'].iloc[-1]:.2f}\n"
            f"Swing Lookback: {int(outputs['swing_lookback'].iloc[-1])}\n"
            f"HTF Bias: {int(outputs['htf_bias'].iloc[-1])}"
        )
        ax.text(
            0.02,
            0.98,
            dashboard,
            transform=ax.transAxes,
            fontsize=10,
            va="top",
            bbox=dict(boxstyle="round", facecolor="#111827", alpha=0.6),
            color="white",
        )

        ax.xaxis_date()
        ax.grid(True, alpha=0.2)
        fig.autofmt_xdate()
        plt.tight_layout()
        plt.show()


# =============================
# Execution
# =============================

def fetch_data(cfg: WaveDynamicsConfig) -> pd.DataFrame:
    try:
        import yfinance as yf  # type: ignore

        data = yf.download(cfg.symbol, interval=cfg.interval, period=cfg.lookback, progress=False)
        if data.empty:
            raise ValueError("Empty data returned")
        data = data.rename(
            columns={
                "Open": "Open",
                "High": "High",
                "Low": "Low",
                "Close": "Close",
                "Volume": "Volume",
            }
        )
        return data[["Open", "High", "Low", "Close", "Volume"]]
    except Exception:
        return generate_mock_data(300, cfg.seed)


def main() -> None:
    cfg = WaveDynamicsConfig()
    df = fetch_data(cfg)
    indicator = WaveDynamicsIndicator(cfg)
    outputs = indicator.compute(df)
    indicator.plot(df, outputs)


if __name__ == "__main__":
    main()
