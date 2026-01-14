import ccxt
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional, Dict, Tuple, Set

# ============================================================
# SETTINGS (Scanner/Timeframe/Bars/Signal Age/Grades/Inputs)
# ============================================================
# Scanner settings
SCAN_ENABLED = True
MAX_SYMBOLS = 0  # 0 = all symbols
SYMBOL_WHITELIST: List[str] = []
SYMBOL_BLACKLIST: List[str] = []

# Timeframe & bars (Pine uses chart timeframe; set explicitly here)
TIMEFRAME = "15m"  # Assumption: Pine uses chart timeframe; default to 15m for scanning.
N_BARS = 1000  # Matches input: maxHistoryBars default

# --- Pine match mode ---
MATCH_PINE_MODE = True

# Pine does NOT have a fixed warmup "continue" like this
WARMUP_BARS = 0
EXTRA_BARS_MARGIN = 50

# Signal age filter
MAX_SIGNAL_AGE_BARS = 10**9 if MATCH_PINE_MODE else 3
MAX_SIGNAL_AGE_MINUTES: Optional[int] = None

# Grade thresholds (classification only)
GRADE_HIGH_THRESHOLD = 80.0
GRADE_MED_THRESHOLD = 60.0

# Pine Inputs (verbatim defaults)
minDisplacementCandles = 2
mitigationMethod = "Cross"  # options: ["Cross", "Close"]
minElementSize = 0.5
maxHistoryBars = 300
brokenAgeThreshold = 50
pendingTimeout = 10
minQualityThreshold = 30

internalPivotLookback = 3
externalPivotLookback = 10
majorSwingLookback = 20
requireVolumeConfirm = True
requireCandleConfirm = True

maxElementsToDisplay = 10
showIdentificationBoxes = True
showPatternLines = True
showOriginLine = True
showMitigationLevels = True
showElementLines = True
showTradeScore = True

boxStyle = "Solid"  # options: ["Solid", "Dashed", "Dotted"]
type1BoxColor = "#2962FF"
type2BoxColor = "#FF6B00"
type3BoxColor = "#00E676"
fvgBoxColor = "#9C27B0"
boxTransparency = 85

originLineWidth = 3
mitigationLineWidth = 2
patternLineWidth = 2
labelPosition = 5

colorScheme = "Professional"  # options: ["Professional", "Vibrant", "Dark", "Custom"]
customOriginColor = "#FFD700"
customMitigationColor = "#00BCD4"

showDashboard = True
dashboardSize = "Large"  # options: ["Small", "Medium", "Large"]
dashboardPosition = "Bottom Right"
dashboardTransparency = 20

showNarrativeDashboard = True
narrativeDashboardPosition = "Bottom Left"
narrativeTransparency = 20

showHTF = True
htfTimeframe = "60"  # options: ["15", "30", "60", "240", "D"]
htfAlignmentRequired = True

showLiquidity = True
liquidityLookback = 20
showSweptLiquidity = True

showPremiumDiscount = True
pdLookback = 50

showSessions = True
showKillzones = True

showIPDA = True

# Assumptions
# - request.security(..., lookahead=barmerge.lookahead_on): implemented as full HTF bar values
#   mapped to all lower timeframe bars within the HTF bucket.


# ============================================================
# Pine Compatibility Helpers
# ============================================================
def nz(value: Optional[float], fallback: float = 0.0) -> float:
    return fallback if value is None else value


def sma(series: List[float], length: int) -> List[Optional[float]]:
    result: List[Optional[float]] = [None] * len(series)
    if length <= 0:
        return result
    window_sum = 0.0
    for i, val in enumerate(series):
        window_sum += val
        if i >= length:
            window_sum -= series[i - length]
        if i >= length - 1:
            result[i] = window_sum / length
    return result


def rma(series: List[Optional[float]], length: int) -> List[Optional[float]]:
    result: List[Optional[float]] = [None] * len(series)
    if length <= 0 or not series:
        return result
    valid_start_idx = 0
    while valid_start_idx < len(series) and series[valid_start_idx] is None:
        valid_start_idx += 1
    if len(series) - valid_start_idx < length:
        return result
    first_chunk = series[valid_start_idx : valid_start_idx + length]
    if any(value is None for value in first_chunk):
        return result
    alpha = 1 / length
    current_val = sum(first_chunk) / length
    result[valid_start_idx + length - 1] = current_val
    for i in range(valid_start_idx + length, len(series)):
        if series[i] is None:
            continue
        current_val = alpha * series[i] + (1 - alpha) * current_val
        result[i] = current_val
    return result


def atr(high: List[float], low: List[float], close: List[float], length: int) -> List[Optional[float]]:
    tr: List[float] = []
    for i in range(len(close)):
        if i == 0:
            tr.append(high[i] - low[i])
        else:
            tr.append(max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1])))
    return rma(tr, length)


def rsi(series: List[float], length: int) -> List[Optional[float]]:
    if not series:
        return []
    gains = [0.0]
    losses = [0.0]
    for i in range(1, len(series)):
        change = series[i] - series[i - 1]
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))
    avg_gain = rma(gains, length)
    avg_loss = rma(losses, length)
    result: List[Optional[float]] = [None] * len(series)
    for i in range(len(series)):
        ag = avg_gain[i]
        al = avg_loss[i]
        if ag is None or al is None:
            result[i] = None
            continue
        if al == 0 and ag == 0:
            result[i] = 50.0
            continue
        if al == 0:
            result[i] = 100.0
            continue
        rs = ag / al
        result[i] = 100 - (100 / (1 + rs))
    return result


def pivot_high(series: List[float], left: int, right: int) -> List[Optional[float]]:
    n = len(series)
    result: List[Optional[float]] = [None] * n
    for i in range(n):
        if i < left + right:
            continue
        pivot_idx = i - right
        window = series[pivot_idx - left:pivot_idx + right + 1]
        if series[pivot_idx] == max(window):
            result[i] = series[pivot_idx]
    return result


def pivot_low(series: List[float], left: int, right: int) -> List[Optional[float]]:
    n = len(series)
    result: List[Optional[float]] = [None] * n
    for i in range(n):
        if i < left + right:
            continue
        pivot_idx = i - right
        window = series[pivot_idx - left:pivot_idx + right + 1]
        if series[pivot_idx] == min(window):
            result[i] = series[pivot_idx]
    return result


def highest(series: List[float], length: int) -> List[Optional[float]]:
    result: List[Optional[float]] = [None] * len(series)
    for i in range(len(series)):
        if i >= length - 1:
            result[i] = max(series[i - length + 1:i + 1])
    return result


def lowest(series: List[float], length: int) -> List[Optional[float]]:
    result: List[Optional[float]] = [None] * len(series)
    for i in range(len(series)):
        if i >= length - 1:
            result[i] = min(series[i - length + 1:i + 1])
    return result


def in_time_range(dt: datetime, time_range: str) -> bool:
    start, end = time_range.split("-")
    start_h, start_m = int(start[:2]), int(start[2:])
    end_h, end_m = int(end[:2]), int(end[2:])
    start_dt = dt.replace(hour=start_h, minute=start_m, second=0, microsecond=0)
    end_dt = dt.replace(hour=end_h, minute=end_m, second=0, microsecond=0)
    return start_dt <= dt < end_dt


def tv_to_ccxt_timeframe(tf: str) -> str:
    mapping = {
        "15": "15m",
        "30": "30m",
        "60": "1h",
        "240": "4h",
        "D": "1d",
    }
    return mapping.get(tf, tf)


def timeframe_to_minutes(tf: str) -> int:
    if tf.endswith("m"):
        return int(tf[:-1])
    if tf.endswith("h"):
        return int(tf[:-1]) * 60
    if tf.endswith("d"):
        return int(tf[:-1]) * 1440
    return int(tf)


# ============================================================
# Data Structures
# ============================================================
@dataclass
class ICTElement:
    high: Optional[float] = None
    low: Optional[float] = None
    startBar: Optional[int] = None
    endBar: Optional[int] = None
    mitigated: bool = False
    mitigationBar: Optional[int] = None
    elementType: str = "Pending"
    timeframe: str = ""
    isOrigin: bool = False
    isMitigation: bool = False
    strength: float = 0.5
    insideKillzone: bool = False
    nearLiquidity: bool = False
    qualityScore: float = 0.0
    causedBOS: bool = False
    inLogicalArea: bool = False
    hasHighVolumeFVG: bool = False
    narrativeRole: str = ""
    mitigationDirection: Optional[str] = None


@dataclass
class MarketStructure:
    bullishBOS: bool = False
    bearishBOS: bool = False
    choch: bool = False
    lastBOSBar: Optional[int] = None
    lastBOSPrice: Optional[float] = None
    internalBullishBOS: bool = False
    internalBearishBOS: bool = False
    externalBullishBOS: bool = False
    externalBearishBOS: bool = False
    lastInternalHigh: Optional[float] = None
    lastInternalLow: Optional[float] = None
    lastExternalHigh: Optional[float] = None
    lastExternalLow: Optional[float] = None
    primaryTrend: str = "NEUTRAL"
    orderFlow: str = "NEUTRAL"


@dataclass
class FVGPattern:
    detected: bool = False
    isBullish: bool = False
    high: Optional[float] = None
    low: Optional[float] = None
    startBar: Optional[int] = None


@dataclass
class TradeScore:
    momentum: float = 0.0
    structure: float = 0.0
    liquidity: float = 0.0
    confluence: float = 0.0
    total: float = 0.0
    grade: str = ""


@dataclass
class TradeSuggestion:
    action: str = ""
    entryPrice: float = 0.0
    stopLoss: float = 0.0
    takeProfit1: float = 0.0
    takeProfit2: float = 0.0
    riskReward: float = 0.0


@dataclass
class SmartMoneyFlow:
    buyVolume: float = 0.0
    sellVolume: float = 0.0
    netFlow: float = 0.0
    bias: str = "NEUTRAL"


@dataclass
class MarketNarrative:
    currentPhase: str = ""
    lastEvent: str = "No recent structural change"
    nextExpectation: str = ""
    causalSequence: str = ""
    sequenceStartBar: int = 0
    keyLevel: Optional[float] = None
    keySetup: str = ""


@dataclass
class ICTPattern:
    name: str = ""
    detected: bool = False
    detectionBar: Optional[int] = None
    strength: float = 0.0


# ============================================================
# Indicator Core
# ============================================================
def calculate_trade_score(
    element: ICTElement,
    ms: MarketStructure,
    bsl_swept: bool,
    ssl_swept: bool,
    htf_bias: str,
) -> TradeScore:
    score = TradeScore()
    if element is None:
        return score
    score.momentum = element.strength * 25
    if element.causedBOS:
        score.structure = 25
    elif ms.externalBullishBOS and element.elementType == "Order Block":
        score.structure = 20
    elif element.elementType == "Trap Zone" and element.nearLiquidity:
        score.structure = 15
    elif element.inLogicalArea:
        score.structure = 10
    else:
        score.structure = 5
    if element.nearLiquidity and (bsl_swept or ssl_swept):
        score.liquidity = 25
    elif element.nearLiquidity:
        score.liquidity = 15
    else:
        score.liquidity = 5
    confluence_factors = 0
    if element.insideKillzone:
        confluence_factors += 2
    if element.inLogicalArea:
        confluence_factors += 2
    if htf_bias == ms.orderFlow:
        confluence_factors += 3
    score.confluence = min(confluence_factors * 3.5, 25)
    score.total = score.momentum + score.structure + score.liquidity + score.confluence
    if score.total >= 80:
        score.grade = "A+"
    elif score.total >= 65:
        score.grade = "A"
    elif score.total >= 50:
        score.grade = "B"
    elif score.total >= 40:
        score.grade = "C"
    else:
        score.grade = "D"
    return score


def assess_quality(
    element: ICTElement,
    ms: MarketStructure,
    is_london_session: bool,
    is_ny_session: bool,
    is_discount: bool,
    is_premium: bool,
    is_equilibrium: bool,
    volume_series: List[float],
    volume_sma20: Optional[float],
    atr14: Optional[float],
    high: List[float],
    low: List[float],
    htf_bias: str,
    index: int,
) -> float:
    if element is None:
        return 0.0
    score = 0.0
    if element.insideKillzone:
        score += 20
    elif is_london_session or is_ny_session:
        score += 10
    if (ms.orderFlow == "BULLISH" and is_discount) or (ms.orderFlow == "BEARISH" and is_premium):
        score += 25
        element.inLogicalArea = True
    elif is_equilibrium:
        score += 10
    current_volume = volume_series[index]
    if volume_sma20 is not None and current_volume > volume_sma20 * 1.5:
        score += 20
    if atr14 is not None and index >= 2:
        fvg_present = abs(high[index - 1] - low[index - 2]) > atr14 * 0.5 or abs(
            low[index - 1] - high[index - 2]
        ) > atr14 * 0.5
        prior_volume = volume_series[index - 1]
        if fvg_present and volume_sma20 is not None and prior_volume > 0:
            if prior_volume > volume_sma20 * 1.3:
                score += 20
                element.hasHighVolumeFVG = True
    if htf_bias == ms.orderFlow:
        score += 15
    return min(score, 100.0)


def calculate_smart_money_flow(
    open_: float,
    high: float,
    low: float,
    close: float,
    volume: float,
    volume_sma20: Optional[float],
) -> SmartMoneyFlow:
    flow = SmartMoneyFlow()
    if volume > 0:
        price_range = max(high - low, 0.00001)
        if close > open_:
            flow.buyVolume = volume * (close - low) / price_range
            flow.sellVolume = volume - flow.buyVolume
        else:
            flow.sellVolume = volume * (high - close) / price_range
            flow.buyVolume = volume - flow.sellVolume
        flow.netFlow = flow.buyVolume - flow.sellVolume
        if volume_sma20 is not None and flow.netFlow > volume_sma20 * 0.2:
            flow.bias = "STRONG BULLISH FLOW"
        elif flow.netFlow > 0:
            flow.bias = "BULLISH FLOW"
        elif volume_sma20 is not None and flow.netFlow < -volume_sma20 * 0.2:
            flow.bias = "STRONG BEARISH FLOW"
        elif flow.netFlow < 0:
            flow.bias = "BEARISH FLOW"
        else:
            flow.bias = "NEUTRAL"
    return flow


def generate_narrative_trade_suggestion(
    element: ICTElement,
    ms: MarketStructure,
    is_discount: bool,
    is_premium: bool,
    atr14: Optional[float],
    bsl: Optional[float],
    ssl: Optional[float],
    close: float,
    score: TradeScore,
) -> TradeSuggestion:
    suggestion = TradeSuggestion()
    if element is None or element.mitigated:
        return suggestion
    if score.total >= 55 and element.narrativeRole != "":
        if ms.orderFlow == "BULLISH" and element.elementType == "Type 1" and is_discount:
            suggestion.action = f"LONG - {element.narrativeRole}"
            suggestion.entryPrice = close
            if atr14 is not None:
                suggestion.stopLoss = element.low - atr14 * 0.2
                suggestion.takeProfit1 = close + (close - suggestion.stopLoss) * 1.5
                suggestion.takeProfit2 = close + (close - suggestion.stopLoss) * 3
            if element.nearLiquidity and bsl is not None:
                suggestion.takeProfit1 = bsl
        elif ms.orderFlow == "BEARISH" and element.elementType == "Type 1" and is_premium:
            suggestion.action = f"SHORT - {element.narrativeRole}"
            suggestion.entryPrice = close
            if atr14 is not None:
                suggestion.stopLoss = element.high + atr14 * 0.2
                suggestion.takeProfit1 = close - (suggestion.stopLoss - close) * 1.5
                suggestion.takeProfit2 = close - (suggestion.stopLoss - close) * 3
            if element.nearLiquidity and ssl is not None:
                suggestion.takeProfit1 = ssl
    if suggestion.action != "" and suggestion.entryPrice != suggestion.stopLoss:
        suggestion.riskReward = abs(suggestion.takeProfit1 - suggestion.entryPrice) / abs(
            suggestion.entryPrice - suggestion.stopLoss
        )
    return suggestion


def detect_advanced_ict_patterns(
    elements: List[ICTElement],
    bar_index: int,
    narrative: MarketNarrative,
) -> List[ICTPattern]:
    patterns: List[ICTPattern] = []
    breaker_block = ICTPattern(name="Breaker Block", detected=False)
    if len(elements) >= 2:
        last_element = elements[-1]
        prev_element = elements[-2]
        if last_element is not None and prev_element is not None:
            if last_element.mitigated and prev_element.mitigated:
                if last_element.elementType == "Type 1" and prev_element.elementType == "Type 2":
                    breaker_block.detected = True
                    breaker_block.detectionBar = bar_index
                    breaker_block.strength = (last_element.strength + prev_element.strength) / 2
                    narrative.lastEvent = "Breaker Block formed"
    patterns.append(breaker_block)

    mitigation_block = ICTPattern(name="Mitigation Block", detected=False)
    if len(elements) >= 1:
        last_element = elements[-1]
        if last_element is not None and last_element.mitigated and last_element.causedBOS:
            mitigation_block.detected = True
            mitigation_block.detectionBar = bar_index
            mitigation_block.strength = last_element.strength
    patterns.append(mitigation_block)
    return patterns


def build_market_narrative(
    narrative: MarketNarrative,
    ms: MarketStructure,
    elements: List[ICTElement],
    in_killzone: bool,
    is_london_kz: bool,
    is_nyam_kz: bool,
    is_nypm_kz: bool,
    is_asian_session: bool,
    is_london_session: bool,
    is_ny_session: bool,
    bsl_swept: bool,
    ssl_swept: bool,
    bsl: Optional[float],
    ssl: Optional[float],
    close: float,
    equilibrium: Optional[float],
    atr14: Optional[float],
    volume_sma20: Optional[float],
    is_premium: bool,
    is_discount: bool,
    is_equilibrium: bool,
    bar_index: int,
) -> None:
    if in_killzone:
        if is_london_kz:
            narrative.currentPhase = "London KZ - Expect directional move"
        elif is_nyam_kz:
            narrative.currentPhase = "NY AM KZ - Peak volatility window"
        elif is_nypm_kz:
            narrative.currentPhase = "NY PM KZ - Position squaring"
    elif is_asian_session:
        narrative.currentPhase = "Asian Range - Accumulation phase"
    elif is_london_session:
        narrative.currentPhase = "London Session - Expansion expected"
    elif is_ny_session:
        narrative.currentPhase = "NY Session - Continuation/Reversal"
    else:
        narrative.currentPhase = "Inter-session - Low probability"

    sequence = ""
    recent_liquidity_sweep = bsl_swept or ssl_swept
    recent_bos = ms.lastBOSBar is not None and bar_index - ms.lastBOSBar < 10
    has_unmitigated_ob = False
    nearest_ob_level = 0.0
    strongest_element = ICTElement()
    if elements:
        for e in elements[-10:]:
            if e is not None and not e.mitigated and e.elementType != "Pending":
                if e.qualityScore > 60:
                    has_unmitigated_ob = True
                    nearest_ob_level = (e.high + e.low) / 2
                    if e.qualityScore > strongest_element.qualityScore:
                        strongest_element = e
    if recent_liquidity_sweep:
        sequence += f"💧 {'Buy-side' if bsl_swept else 'Sell-side'} liquidity swept → "
        narrative.keyLevel = bsl if bsl_swept else ssl
    if ms.choch:
        sequence += f"⚡ CHoCH confirmed → Bias shift to {ms.orderFlow} → "
    if recent_bos:
        bos_type = "Bullish" if ms.externalBullishBOS else "Bearish" if ms.externalBearishBOS else "Internal"
        sequence += f"📊 {bos_type} BOS → "
    if has_unmitigated_ob:
        sequence += f"🎯 Active {strongest_element.elementType} at {nearest_ob_level:.4f} → "

    expectation = ""
    if recent_liquidity_sweep and not recent_bos:
        if bsl_swept and bsl is not None:
            expectation = f"🔻 Reversal likely after BSL sweep. Watch for bearish OB formation near {bsl:.4f}"
        elif ssl is not None:
            expectation = f"🔺 Reversal likely after SSL sweep. Watch for bullish OB formation near {ssl:.4f}"
    elif recent_bos and has_unmitigated_ob:
        if ms.orderFlow == "BULLISH":
            if close > nearest_ob_level:
                expectation = f"📉 Pullback expected to bullish OB at {nearest_ob_level:.4f} before continuation up"
            else:
                expectation = f"🚀 Price approaching bullish OB. Long entry opportunity near {nearest_ob_level:.4f}"
        else:
            if close < nearest_ob_level:
                expectation = f"📈 Retracement expected to bearish OB at {nearest_ob_level:.4f} before continuation down"
            else:
                expectation = f"💥 Price approaching bearish OB. Short entry opportunity near {nearest_ob_level:.4f}"
    elif ms.choch:
        expectation = (
            "🔄 Character change! Old "
            + ("resistance" if ms.orderFlow == "BULLISH" else "support")
            + " becomes "
            + ("support" if ms.orderFlow == "BULLISH" else "resistance")
            + ". First retest pending"
        )
    elif is_premium and ms.orderFlow == "BEARISH" and equilibrium is not None:
        expectation = f"📍 In premium zone + bearish bias. Seeking sell setups. Target: {equilibrium:.4f}"
    elif is_discount and ms.orderFlow == "BULLISH" and equilibrium is not None:
        expectation = f"📍 In discount zone + bullish bias. Seeking buy setups. Target: {equilibrium:.4f}"
    elif in_killzone:
        if is_london_kz and bsl is not None and ssl is not None:
            expectation = f"⏰ London KZ active. Expect sweep of Asian high/low at {bsl:.4f}/{ssl:.4f}"
        elif is_nyam_kz:
            if ms.orderFlow == "NEUTRAL" and bsl is not None and ssl is not None:
                expectation = f"⏰ NY AM KZ: Awaiting directional commitment. Monitor {bsl:.4f} and {ssl:.4f}"
            else:
                expectation = f"⏰ NY AM KZ + {ms.orderFlow} bias. Expect acceleration {'higher' if ms.orderFlow == 'BULLISH' else 'lower'}"
        elif is_nypm_kz:
            expectation = "⏰ NY PM KZ: Position squaring time. Fade moves without strong volume"
    elif is_equilibrium and equilibrium is not None and atr14 is not None and bsl is not None and ssl is not None:
        near_bsl = abs(close - bsl) < atr14 * 2
        near_ssl = abs(close - ssl) < atr14 * 2
        if near_bsl:
            expectation = (
                f"⚖️ At equilibrium near BSL. Rejection = Short, Break = Long targeting {bsl + atr14 * 2:.4f}"
            )
        elif near_ssl:
            expectation = (
                f"⚖️ At equilibrium near SSL. Rejection = Long, Break = Short targeting {ssl - atr14 * 2:.4f}"
            )
        else:
            volume_target = int(round(volume_sma20 * 1.5)) if volume_sma20 is not None else 0
            expectation = f"⚖️ At equilibrium. Wait for directional break with volume > {volume_target}"
    else:
        if not elements:
            expectation = "🔍 No quality setups detected. Wait for clear structure break or liquidity sweep"
        elif bsl is not None and ssl is not None and equilibrium is not None:
            next_level = f"{bsl:.4f} (BSL)" if close > equilibrium else f"{ssl:.4f} (SSL)"
            expectation = f"📊 Monitoring {len(elements)} elements. Next key level: {next_level}"

    narrative.nextExpectation = expectation
    narrative.causalSequence = sequence


def get_enhanced_market_narrative(
    narrative: MarketNarrative,
    ms: MarketStructure,
    elements: List[ICTElement],
    htf_bias: str,
    is_premium: bool,
    is_discount: bool,
    is_equilibrium: bool,
    close: float,
    equilibrium: Optional[float],
    atr14: Optional[float],
    bsl: Optional[float],
    ssl: Optional[float],
    score: Optional[TradeScore],
) -> str:
    full = f"📍 {narrative.currentPhase}\n"
    full += f"🎯 Bias: {ms.orderFlow}"
    if htf_bias == ms.orderFlow and ms.orderFlow != "NEUTRAL":
        full += " ✅ HTF Aligned"
    elif htf_bias != "NEUTRAL" and ms.orderFlow != "NEUTRAL" and htf_bias != ms.orderFlow:
        full += " ⚠️ HTF Conflict"
    full += "\n"
    market_position = "Premium" if is_premium else "Discount" if is_discount else "Equilibrium"
    full += f"📊 Zone: {market_position}"
    if (is_premium or is_discount) and equilibrium is not None and atr14 is not None:
        full += f" ({round(abs(close - equilibrium) / atr14)} ATR from EQ)"
    full += "\n"
    if narrative.causalSequence != "":
        full += f"🔗 Events: {narrative.causalSequence}\n"
    full += f"🎯 {narrative.nextExpectation}\n"
    if elements:
        last_e = elements[-1]
        if last_e is not None and not last_e.mitigated and score is not None:
            if score.total >= 60:
                suggestion = generate_narrative_trade_suggestion(
                    last_e,
                    ms,
                    is_discount,
                    is_premium,
                    atr14,
                    bsl,
                    ssl,
                    close,
                    score,
                )
                if suggestion.action != "":
                    full += f"⚡ Setup Ready: {suggestion.action} RR:{suggestion.riskReward:.1f}"
    return full


def classify_element(
    element: ICTElement,
    elements: List[ICTElement],
    ms: MarketStructure,
    bsl_swept: bool,
    ssl_swept: bool,
    max_history_bars: int,
    volume_series: List[float],
    volume_sma20: List[Optional[float]],
    bar_index: int,
) -> ICTElement:
    if element is None or element.endBar is None:
        return element
    age = bar_index - element.endBar
    caused_bullish_bos = (
        ms.bullishBOS
        and ms.lastBOSBar is not None
        and ms.lastBOSBar > element.endBar
        and (ms.lastBOSBar - element.endBar) <= 10
    )
    caused_bearish_bos = (
        ms.bearishBOS
        and ms.lastBOSBar is not None
        and ms.lastBOSBar > element.endBar
        and (ms.lastBOSBar - element.endBar) <= 10
    )

    if caused_bullish_bos or caused_bearish_bos:
        element.causedBOS = True

    liquidity_sweep = (bsl_swept or ssl_swept) and (bar_index - element.endBar) <= 5

    high_volume = False
    if element.endBar >= bar_index - max_history_bars:
        elem_i = element.endBar
        if 0 <= elem_i < len(volume_series):
            v = volume_series[elem_i]
            vma = volume_sma20[elem_i]
            if vma is not None and v > vma * 1.5:
                high_volume = True

    if caused_bullish_bos or caused_bearish_bos:
        element.elementType = "Order Block"
        element.narrativeRole = "Bullish OB (caused BOS)" if caused_bullish_bos else "Bearish OB (caused BOS)"
        element.strength = 0.9
    elif liquidity_sweep:
        element.elementType = "Trap Zone"
        element.narrativeRole = "Liquidity Trap"
        element.strength = 0.8
    elif high_volume and element.inLogicalArea:
        element.elementType = "Order Block"
        element.narrativeRole = f"{ms.orderFlow} OB (high volume)"
        element.strength = 0.7
    elif age > 5:
        element.elementType = "S/R Zone"
        element.narrativeRole = "Support/Resistance"
        element.strength = 0.5
    return element


def determine_advanced_ict_type(
    element: ICTElement,
    break_direction: str,
    ms: MarketStructure,
    open_series: List[float],
    close_series: List[float],
    atr14: Optional[float],
    volume_series: List[float],
    volume_sma20: Optional[float],
    bsl_swept: bool,
    ssl_swept: bool,
    internal_high: Optional[float],
    internal_low: Optional[float],
    rsi14: Optional[float],
    elements: List[ICTElement],
    bar_index: int,
) -> Tuple[str, float, str]:
    ict_type = "Pending"
    strength = 0.5
    narrative_role = ""
    if element is None or element.endBar is None:
        return ict_type, strength, narrative_role
    bars_since_element = bar_index - element.endBar
    if bars_since_element < 2:
        return ict_type, strength, narrative_role
    is_strong_move = atr14 is not None and abs(close_series[bar_index] - close_series[bar_index - 2]) > atr14 * 1.5
    has_volume = volume_sma20 is not None and volume_series[bar_index] > volume_sma20 * 1.3 and volume_series[bar_index - 1] > volume_sma20 * 1.2
    has_external_bos = ms.externalBullishBOS or ms.externalBearishBOS
    has_liquidity_sweep = bsl_swept or ssl_swept
    is_pivot = internal_high is not None or internal_low is not None
    if elements:
        for elem in elements[-5:]:
            if elem is not None and elem.endBar is not None and ms.lastBOSBar is not None:
                if elem.endBar >= ms.lastBOSBar - 5 and elem.endBar <= ms.lastBOSBar:
                    elem.causedBOS = True
                    break
    if break_direction == "up":
        if has_external_bos and has_volume and is_strong_move and element.insideKillzone:
            ict_type = "Type 1"
            strength = min(volume_series[bar_index] / volume_sma20 * 0.7, 1.0) if volume_sma20 else 0.5
            narrative_role = "Momentum continuation after external BOS"
        elif has_liquidity_sweep and close_series[bar_index] < open_series[bar_index]:
            ict_type = "Type 2"
            strength = 0.8
            narrative_role = "Liquidity grab and reversal"
        elif is_pivot or (rsi14 is not None and rsi14 > 70 and not has_volume):
            ict_type = "Type 3"
            strength = 0.6
            narrative_role = "Potential reversal pivot"
        else:
            ict_type = "Type 3"
            strength = 0.5
            narrative_role = "Minor structure"
    else:
        if has_external_bos and has_volume and is_strong_move and element.insideKillzone:
            ict_type = "Type 1"
            strength = min(volume_series[bar_index] / volume_sma20 * 0.7, 1.0) if volume_sma20 else 0.5
            narrative_role = "Momentum continuation after external BOS"
        elif has_liquidity_sweep and close_series[bar_index] > open_series[bar_index]:
            ict_type = "Type 2"
            strength = 0.8
            narrative_role = "Liquidity grab and reversal"
        elif is_pivot or (rsi14 is not None and rsi14 < 30 and not has_volume):
            ict_type = "Type 3"
            strength = 0.6
            narrative_role = "Potential reversal pivot"
        else:
            ict_type = "Type 3"
            strength = 0.5
            narrative_role = "Minor structure"
    return ict_type, min(strength, 1.0), narrative_role


def detect_fvg(
    high: List[float],
    low: List[float],
    close: List[float],
    open_: List[float],
    volume: List[float],
    volume_sma20: List[Optional[float]],
    atr14: List[Optional[float]],
    index: int,
) -> FVGPattern:
    fvg = FVGPattern()
    if atr14[index] is None or index < 2 or volume_sma20[index] is None:
        return fvg
    min_gap_size = atr14[index] * 0.5
    bullish_gap = low[index] > high[index - 2]
    if bullish_gap:
        gap_size = low[index] - high[index - 2]
        if gap_size > min_gap_size and close[index] > open_[index] and volume[index] > volume_sma20[index] * 1.2:
            fvg.detected = True
            fvg.isBullish = True
            fvg.high = low[index]
            fvg.low = high[index - 2]
            fvg.startBar = index - 2
    bearish_gap = high[index] < low[index - 2]
    if bearish_gap:
        gap_size = low[index - 2] - high[index]
        if gap_size > min_gap_size and close[index] < open_[index] and volume[index] > volume_sma20[index] * 1.2:
            fvg.detected = True
            fvg.isBullish = False
            fvg.high = low[index - 2]
            fvg.low = high[index]
            fvg.startBar = index - 2
    return fvg


# ============================================================
# Scanner Engine
# ============================================================
def build_htf_series(
    timestamps: List[int],
    open_: List[float],
    high: List[float],
    low: List[float],
    close: List[float],
    volume: List[float],
    htf_minutes: int,
) -> Tuple[Dict[str, List[Optional[float]]], List[int], List[int], List[float]]:
    bucket_ms = htf_minutes * 60 * 1000
    buckets: Dict[int, Dict[str, float]] = {}
    bucket_order: List[int] = []
    for i, ts in enumerate(timestamps):
        bucket = (ts // bucket_ms) * bucket_ms
        if bucket not in buckets:
            buckets[bucket] = {
                "open": open_[i],
                "high": high[i],
                "low": low[i],
                "close": close[i],
                "volume": volume[i],
            }
            bucket_order.append(bucket)
        else:
            buckets[bucket]["high"] = max(buckets[bucket]["high"], high[i])
            buckets[bucket]["low"] = min(buckets[bucket]["low"], low[i])
            buckets[bucket]["close"] = close[i]
            buckets[bucket]["volume"] += volume[i]

    bucket_close_list: List[float] = [buckets[b]["close"] for b in bucket_order]

    htf_open: List[Optional[float]] = [None] * len(timestamps)
    htf_high: List[Optional[float]] = [None] * len(timestamps)
    htf_low: List[Optional[float]] = [None] * len(timestamps)
    htf_close: List[Optional[float]] = [None] * len(timestamps)
    htf_volume: List[Optional[float]] = [None] * len(timestamps)
    bucket_index_map: List[int] = [0] * len(timestamps)
    bucket_index_lookup = {bucket: idx for idx, bucket in enumerate(bucket_order)}

    for i, ts in enumerate(timestamps):
        bucket = (ts // bucket_ms) * bucket_ms
        data = buckets.get(bucket)
        bucket_index_map[i] = bucket_index_lookup.get(bucket, 0)
        if data:
            # Use final bucket values to match Pine lookahead_on behavior.
            htf_open[i] = data["open"]
            htf_high[i] = data["high"]
            htf_low[i] = data["low"]
            htf_close[i] = data["close"]
            htf_volume[i] = data["volume"]
    return (
        {
            "open": htf_open,
            "high": htf_high,
            "low": htf_low,
            "close": htf_close,
            "volume": htf_volume,
            "bucket_order": bucket_order,
        },
        bucket_index_map,
        bucket_order,
        bucket_close_list,
    )


def classify_grade_level(grade_pct: float) -> Tuple[str, str]:
    if grade_pct >= GRADE_HIGH_THRESHOLD:
        return "HIGH", "High probability / Top grade"
    if grade_pct >= GRADE_MED_THRESHOLD:
        return "MED", "Moderate quality / Medium grade"
    return "LOW", "Low quality / Low grade"


def evaluate_symbol(symbol: str, ohlcv: List[List[float]]) -> List[str]:
    timestamps = [int(row[0]) for row in ohlcv]
    open_ = [float(row[1]) for row in ohlcv]
    high = [float(row[2]) for row in ohlcv]
    low = [float(row[3]) for row in ohlcv]
    close = [float(row[4]) for row in ohlcv]
    volume = [float(row[5]) for row in ohlcv]

    volume_sma20 = sma(volume, 20)
    volume_sma10 = sma(volume, 10)
    atr14 = atr(high, low, close, 14)
    rsi14 = rsi(close, 14)
    avg_range20 = sma([h - l for h, l in zip(high, low)], 20)
    trend_sma = sma(close, 50)

    internal_high = pivot_high(high, internalPivotLookback, internalPivotLookback)
    internal_low = pivot_low(low, internalPivotLookback, internalPivotLookback)
    external_high = pivot_high(high, externalPivotLookback, externalPivotLookback)
    external_low = pivot_low(low, externalPivotLookback, externalPivotLookback)
    major_high = pivot_high(high, majorSwingLookback, majorSwingLookback)
    major_low = pivot_low(low, majorSwingLookback, majorSwingLookback)

    bsl = highest(high, liquidityLookback)
    ssl = lowest(low, liquidityLookback)
    pd_high = highest(high, pdLookback)
    pd_low = lowest(low, pdLookback)

    htf_ccxt = tv_to_ccxt_timeframe(htfTimeframe)
    htf_minutes = timeframe_to_minutes(htf_ccxt)
    htf_series, htf_bucket_index, htf_bucket_order, htf_close_by_bucket = build_htf_series(
        timestamps, open_, high, low, close, volume, htf_minutes
    )
    htf_close = htf_series["close"]
    htf_high = htf_series["high"]
    htf_low = htf_series["low"]
    htf_sma20_by_bucket = sma(htf_close_by_bucket, 20)
    htf_sma20_full: List[Optional[float]] = [None] * len(close)
    for i in range(len(close)):
        bucket_idx = htf_bucket_index[i]
        if 0 <= bucket_idx < len(htf_sma20_by_bucket):
            htf_sma20_full[i] = htf_sma20_by_bucket[bucket_idx]
        else:
            htf_sma20_full[i] = None

    ms = MarketStructure()
    elements: List[ICTElement] = []
    fvg_patterns: List[FVGPattern] = []
    mitigation_levels: List[ICTElement] = []
    current_origin: Optional[ICTElement] = None
    narrative = MarketNarrative()
    last_detection_bar = 0

    signals: List[str] = []
    signal_dedup: Set[Tuple[str, str, int, str]] = set()
    last_index = len(close) - 1

    for i in range(len(close)):
        dt = datetime.fromtimestamp(timestamps[i] / 1000, tz=timezone.utc)
        is_asian_session = in_time_range(dt, "0000-0800")
        is_london_session = in_time_range(dt, "0800-1200")
        is_ny_session = in_time_range(dt, "1200-1600")
        is_london_kz = in_time_range(dt, "0800-0900")
        is_nyam_kz = in_time_range(dt, "1330-1430")
        is_nypm_kz = in_time_range(dt, "1500-1600")
        in_killzone = is_london_kz or is_nyam_kz or is_nypm_kz

        if trend_sma[i] is not None:
            if close[i] > trend_sma[i]:
                ms.primaryTrend = "BULLISH"
            elif close[i] < trend_sma[i]:
                ms.primaryTrend = "BEARISH"
            else:
                ms.primaryTrend = "NEUTRAL"

        if internal_high[i] is not None:
            ms.lastInternalHigh = internal_high[i]
        if internal_low[i] is not None:
            ms.lastInternalLow = internal_low[i]
        if external_high[i] is not None:
            ms.lastExternalHigh = external_high[i]
        if external_low[i] is not None:
            ms.lastExternalLow = external_low[i]

        ms.internalBullishBOS = ms.lastInternalHigh is not None and high[i] > ms.lastInternalHigh
        ms.internalBearishBOS = ms.lastInternalLow is not None and low[i] < ms.lastInternalLow

        volume_confirm = not requireVolumeConfirm or (
            volume_sma20[i] is not None and volume[i] > volume_sma20[i] * 1.2
        )
        bullish_candle_confirm = not requireCandleConfirm or (
            close[i] > open_[i] and i > 0 and close[i - 1] > open_[i - 1]
        )
        bearish_candle_confirm = not requireCandleConfirm or (
            close[i] < open_[i] and i > 0 and close[i - 1] < open_[i - 1]
        )

        ms.externalBullishBOS = False
        ms.externalBearishBOS = False
        if ms.lastExternalHigh is not None and high[i] > ms.lastExternalHigh and volume_confirm and bullish_candle_confirm:
            ms.externalBullishBOS = True
            ms.bullishBOS = True
            ms.bearishBOS = False
            ms.lastBOSBar = i
            ms.lastBOSPrice = high[i]
            ms.orderFlow = "BULLISH"
        if ms.lastExternalLow is not None and low[i] < ms.lastExternalLow and volume_confirm and bearish_candle_confirm:
            ms.externalBearishBOS = True
            ms.bearishBOS = True
            ms.bullishBOS = False
            ms.lastBOSBar = i
            ms.lastBOSPrice = low[i]
            ms.orderFlow = "BEARISH"

        ms.choch = False
        if ms.orderFlow == "BULLISH" and ms.externalBearishBOS:
            ms.choch = True
        if ms.orderFlow == "BEARISH" and ms.externalBullishBOS:
            ms.choch = True

        htf_c = htf_close[i]
        htf_sma_val = htf_sma20_full[i]
        if htf_c is None or htf_sma_val is None:
            htf_trend = "NEUTRAL"
        else:
            if htf_c > htf_sma_val:
                htf_trend = "BULLISH"
            elif htf_c < htf_sma_val:
                htf_trend = "BEARISH"
            else:
                htf_trend = "NEUTRAL"

        if i > 0 and htf_close[i] is not None and htf_high[i - 1] is not None and htf_low[i - 1] is not None:
            if htf_close[i] > htf_high[i - 1]:
                htf_bias = "BULLISH"
            elif htf_close[i] < htf_low[i - 1]:
                htf_bias = "BEARISH"
            else:
                htf_bias = "NEUTRAL"
        else:
            htf_bias = "NEUTRAL"

        if i < WARMUP_BARS:
            continue

        bsl_swept = False
        ssl_swept = False
        if i > 0 and bsl[i - 1] is not None and ssl[i - 1] is not None:
            bsl_swept = high[i] > bsl[i - 1] and close[i] < bsl[i - 1]
            ssl_swept = low[i] < ssl[i - 1] and close[i] > ssl[i - 1]

        equilibrium = None
        is_premium = False
        is_discount = False
        is_equilibrium = False
        if pd_high[i] is not None and pd_low[i] is not None:
            equilibrium = (pd_high[i] + pd_low[i]) / 2
            is_premium = close[i] > equilibrium + (pd_high[i] - equilibrium) * 0.5
            is_discount = close[i] < equilibrium - (equilibrium - pd_low[i]) * 0.5
            is_equilibrium = not is_premium and not is_discount

        # Validation
        is_valid_element = False
        if i > minDisplacementCandles and i - last_detection_bar >= 5:
            parent_high = high[i - minDisplacementCandles]
            parent_low = low[i - minDisplacementCandles]
            all_inside = True
            for j in range(minDisplacementCandles):
                if high[i - j] > parent_high or low[i - j] < parent_low:
                    all_inside = False
                    break
            fvg_gap = False
            if atr14[i] is not None:
                fvg_gap = abs(high[i - 1] - low[i - minDisplacementCandles]) > atr14[i] * 0.3 or abs(
                    low[i - 1] - high[i - minDisplacementCandles]
                ) > atr14[i] * 0.3
            range_quality = False
            if avg_range20[i] is not None and atr14[i] is not None:
                element_range = parent_high - parent_low
                range_quality = element_range > avg_range20[i] * minElementSize and element_range > atr14[i] * minElementSize
            volume_quality = volume_sma10[i] is not None and volume[i - minDisplacementCandles] > volume_sma10[i] * 0.8
            recent_elements = 0
            for e in elements[-5:]:
                if e.endBar is not None and i - e.endBar < 20:
                    recent_elements += 1
            not_too_many = recent_elements < 3
            htf_valid = not htfAlignmentRequired or htf_bias != "NEUTRAL"
            is_valid_element = (all_inside or fvg_gap) and range_quality and volume_quality and not_too_many and htf_valid

        if is_valid_element:
            new_element = ICTElement()
            new_element.high = high[i - minDisplacementCandles]
            new_element.low = low[i - minDisplacementCandles]
            new_element.startBar = i - minDisplacementCandles
            new_element.endBar = i
            new_element.mitigated = False
            new_element.timeframe = TIMEFRAME
            new_element.insideKillzone = in_killzone
            if atr14[i] is not None and bsl[i] is not None and ssl[i] is not None:
                new_element.nearLiquidity = abs(new_element.high - bsl[i]) < atr14[i] * 0.5 or abs(
                    new_element.low - ssl[i]
                ) < atr14[i] * 0.5
            new_element.elementType = "Pending"
            new_element.narrativeRole = "Awaiting classification"
            new_element.qualityScore = assess_quality(
                new_element,
                ms,
                is_london_session,
                is_ny_session,
                is_discount,
                is_premium,
                is_equilibrium,
                volume,
                volume_sma20[i],
                atr14[i],
                high,
                low,
                htf_bias,
                i,
            )
            if len(elements) < maxElementsToDisplay * 3:
                elements.append(new_element)
                last_detection_bar = i

        current_fvg = detect_fvg(high, low, close, open_, volume, volume_sma20, atr14, i)
        if current_fvg.detected and len(fvg_patterns) < 20:
            fvg_patterns.append(current_fvg)

        # Cleanup and mitigation
        if fvg_patterns:
            fvg_patterns = [f for f in fvg_patterns if f.startBar is None or i - f.startBar <= 50]

        to_remove = []
        for idx, e in enumerate(elements[:50]):
            age = i - e.startBar if e.startBar is not None else 0
            if e.elementType == "Pending" and age >= 2 and age < pendingTimeout:
                classify_element(
                    e,
                    elements,
                    ms,
                    bsl_swept,
                    ssl_swept,
                    maxHistoryBars,
                    volume,
                    volume_sma20,
                    i,
                )
            if age > brokenAgeThreshold or (e.elementType == "Pending" and age > pendingTimeout):
                to_remove.append(idx)
        for idx in reversed(to_remove):
            if idx < len(elements):
                elements.pop(idx)

        for e in elements[-20:]:
            if not e.mitigated:
                mitigated = False
                break_direction = ""
                if mitigationMethod == "Cross":
                    if e.high is not None and high[i] > e.high:
                        mitigated = True
                        break_direction = "up"
                    elif e.low is not None and low[i] < e.low:
                        mitigated = True
                        break_direction = "down"
                else:
                    if e.high is not None and close[i] > e.high:
                        mitigated = True
                        break_direction = "up"
                    elif e.low is not None and close[i] < e.low:
                        mitigated = True
                        break_direction = "down"
                if mitigated:
                    e.mitigated = True
                    e.mitigationBar = i
                    e.mitigationDirection = break_direction
                    if e.elementType == "Pending":
                        if (break_direction == "up" and ms.orderFlow == "BEARISH") or (
                            break_direction == "down" and ms.orderFlow == "BULLISH"
                        ):
                            e.elementType = "Reversal Zone"
                            e.narrativeRole = "Counter-trend mitigation"
                        else:
                            e.elementType = "S/R Zone"
                            e.narrativeRole = "Support/Resistance break"
                    if (break_direction == "up" and ms.bullishBOS) or (break_direction == "down" and ms.bearishBOS):
                        if current_origin is not None and current_origin.isOrigin:
                            current_origin.isOrigin = False
                        e.isOrigin = True
                        current_origin = e
                    if len(mitigation_levels) >= 3:
                        mitigation_levels.pop(0)
                    mit_level = ICTElement()
                    mit_level.high = e.high if break_direction == "up" else e.low
                    mit_level.low = mit_level.high
                    mit_level.startBar = i
                    mit_level.isMitigation = True
                    mit_level.strength = e.strength
                    mitigation_levels.append(mit_level)
                    determine_advanced_ict_type(
                        e,
                        break_direction,
                        ms,
                        open_,
                        close,
                        atr14[i],
                        volume,
                        volume_sma20[i],
                        bsl_swept,
                        ssl_swept,
                        internal_high[i],
                        internal_low[i],
                        rsi14[i],
                        elements,
                        i,
                    )

        # Alerts (entry signals)
        for e in elements[-5:]:
            if e.mitigated and e.mitigationBar == i:
                score = calculate_trade_score(e, ms, bsl_swept, ssl_swept, htf_bias)
                if score.total >= 70:
                    if e.mitigationDirection == "up":
                        signal_type = "LONG"
                    elif e.mitigationDirection == "down":
                        signal_type = "SHORT"
                    else:
                        signal_type = "LONG" if ms.orderFlow == "BULLISH" else "SHORT"
                    key = (symbol, TIMEFRAME, timestamps[i], signal_type)
                    if key in signal_dedup:
                        continue
                    age_bars = last_index - i
                    if age_bars > MAX_SIGNAL_AGE_BARS:
                        continue
                    if MAX_SIGNAL_AGE_MINUTES is not None:
                        age_minutes = (timestamps[last_index] - timestamps[i]) / 60000
                        if age_minutes > MAX_SIGNAL_AGE_MINUTES:
                            continue
                    grade_pct = score.total
                    grade_level, grade_text = classify_grade_level(grade_pct)
                    signal_time = datetime.fromtimestamp(timestamps[i] / 1000, tz=timezone.utc).strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    line = (
                        f"[{signal_time}] {symbol} {TIMEFRAME} SIGNAL={signal_type} "
                        f"PRICE={close[i]:.6f} AGE_BARS={age_bars} "
                        f"GRADE_PCT={grade_pct:.2f} GRADE_LEVEL={grade_level} "
                        f'GRADE_TEXT="{grade_text}"'
                    )
                    signals.append(line)
                    signal_dedup.add(key)

        _sm_flow = calculate_smart_money_flow(
            open_[i],
            high[i],
            low[i],
            close[i],
            volume[i],
            volume_sma20[i],
        )
        detect_advanced_ict_patterns(elements, i, narrative)
        build_market_narrative(
            narrative,
            ms,
            elements,
            in_killzone,
            is_london_kz,
            is_nyam_kz,
            is_nypm_kz,
            is_asian_session,
            is_london_session,
            is_ny_session,
            bsl_swept,
            ssl_swept,
            bsl[i],
            ssl[i],
            close[i],
            equilibrium,
            atr14[i],
            volume_sma20[i],
            is_premium,
            is_discount,
            is_equilibrium,
            i,
        )
        last_score = calculate_trade_score(elements[-1], ms, bsl_swept, ssl_swept, htf_bias) if elements else None
        get_enhanced_market_narrative(
            narrative,
            ms,
            elements,
            htf_bias,
            is_premium,
            is_discount,
            is_equilibrium,
            close[i],
            equilibrium,
            atr14[i],
            bsl[i],
            ssl[i],
            last_score,
        )
        while len(elements) > maxElementsToDisplay * 3:
            elements.pop(0)

    return signals


def load_symbols(exchange: ccxt.Exchange) -> List[str]:
    exchange.load_markets()
    symbols = []
    for symbol, market in exchange.markets.items():
        if not market.get("contract") or not market.get("linear"):
            continue
        if market.get("settle") != "USDT":
            continue
        contract_type = market.get("info", {}).get("contractType")
        if contract_type and contract_type != "PERPETUAL":
            continue
        symbols.append(symbol)
    if SYMBOL_WHITELIST:
        symbols = [s for s in symbols if s in SYMBOL_WHITELIST]
    if SYMBOL_BLACKLIST:
        symbols = [s for s in symbols if s not in SYMBOL_BLACKLIST]
    if MAX_SYMBOLS > 0:
        symbols = symbols[:MAX_SYMBOLS]
    return symbols


def fetch_ohlcv(exchange: ccxt.Exchange, symbol: str) -> List[List[float]]:
    limit = N_BARS + EXTRA_BARS_MARGIN
    try:
        data = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=limit)
        return data
    except ccxt.RateLimitExceeded:
        return []
    except ccxt.NetworkError:
        return []
    except ccxt.ExchangeError:
        return []


def drop_unconfirmed_last_bar(ohlcv: List[List[float]], tf_minutes: int) -> List[List[float]]:
    if not ohlcv:
        return ohlcv
    now_ms = int(time.time() * 1000)
    last_open = int(ohlcv[-1][0])
    tf_ms = tf_minutes * 60 * 1000
    if last_open + tf_ms > now_ms:
        return ohlcv[:-1]
    return ohlcv


def main() -> None:
    if not SCAN_ENABLED:
        return
    exchange = ccxt.binanceusdm({"enableRateLimit": True})
    symbols = load_symbols(exchange)
    all_signals: List[str] = []
    for symbol in symbols:
        ohlcv = fetch_ohlcv(exchange, symbol)
        if not ohlcv:
            continue
        ohlcv = drop_unconfirmed_last_bar(ohlcv, timeframe_to_minutes(TIMEFRAME))
        if len(ohlcv) < 200:
            continue
        signals = evaluate_symbol(symbol, ohlcv)
        all_signals.extend(signals)
    for line in all_signals:
        print(line)


if __name__ == "__main__":
    main()
