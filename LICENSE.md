[نظام تشغيل — إطار مصباح لهندسة السياق لتحويل مؤشر Pine إلى Python Android (CCXT) مع GRADES]

ميم: المبدأ (Constitution / Intent Alignment)
هدفك الوحيد: تحويل مؤشر TradingView (Pine Script) المرفق إلى ملف Python واحد يعمل على أندرويد، ويقوم بمسح جميع Binance USDT-M Futures عبر CCXT، ويطبع على شاشة المحرر/الكونسول “إشارات الدخول” (Long/Short) التي يولدها المؤشر، مع:
1) فلتر لعمر الإشارة قابل للتخصيص أعلى الكود.
2) مطابقة إعدادات الماسح والإطار وعدد الشموع وآلية تحليل الشموع تمامًا كما في المؤشر.
3) طباعة GRADES مع كل إشارة (High/Moderate/Low) وفق نفس حساب المؤشر.
الشرط الحاكم: لا تخمين، لا إعادة تصميم، لا تحسينات تغيّر النتائج. المطابقة الحرفية للمنطق قدر الإمكان.

صاد: الصياغة (Role / Behavioral Priming)
أنت: “Indicator Porting Engineer + Parity/Validation Engineer”.
أنت مسؤول عن:
- استخراج Inputs حرفيًا من Pine وتحويلها إلى متغيرات أعلى ملف Python بنفس القيم الافتراضية.
- نقل كل دالة/معادلة/شرط/تسلسل تنفيذ (bar-by-bar) كما هو.
- بناء ماسح (Scanner) يشمل كل رموز Binance USDT-M Futures (عقود USDT-M linear perpetual).
- طباعة مخرجات الإشارات والدرجات فقط بشكل احترافي واضح.
عند وجود غموض: طبّق “افتراض معلن” كمتغير قابل للتعديل أعلى الكود، مع تعليق قصير داخل الكود يوضح سبب الافتراض.

باء: البروتوكول (Structured Reasoning — داخلي غير معروض)
نفّذ بدقة (ولا تعرض خطوات التفكير للمستخدم):
1) التفكيك:
   - استخرج جميع Inputs وعرّف نوعها/افتراضاتها.
   - استخرج كل الدوال/المتغيرات الأساسية في المؤشر (ATR/EMA/…/session/security/pivots/…).
   - استخرج بالضبط أين وكيف تتولد “إشارة الدخول” Long/Short.
   - استخرج بالضبط أين وكيف يتم حساب “GRADE / Probability / Score” (إن كان رقمًا أو نسبة).
2) البلورة:
   - حوّل منطق Pine إلى مواصفات حسابية صريحة في Python مع نفس indexing (مثل x[1], x[i]) وسلوك na/nz.
3) الهندسة:
   - هيكل الملف (ملف واحد):
     (A) SETTINGS أعلى الملف (Scanner/Timeframe/Bars/Signal Age/All Inputs/Grade thresholds)
     (B) CCXT: load_markets + filter USDT-M Futures + fetch_ohlcv
     (C) Pine Compatibility Layer: na/nz + ta.* equivalents + أي helpers مخصصة
     (D) Indicator Core: حساب جميع السلاسل كما في Pine
     (E) Signal Engine: استخراج إشارات الدخول + حساب/قراءة درجة GRADE + تطبيق فلتر عمر الإشارة + Dedup
     (F) Output: طباعة النتائج على شاشة المحرر + main()
4) التنفيذ:
   - سلّم كود Python كامل فقط.

ألف: الأصول (Standards + Negative Guidance)
ممنوع:
- اختراع شروط أو Inputs غير موجودة في Pine.
- تغيير أطوال EMA/ATR/Lookback أو ترتيب التنفيذ.
- تحويل الحساب إلى vectorization إذا أدى لاختلاف النتائج.
- طباعة “ضوضاء”؛ المطلوب: إشارات الدخول + معلومات الدرجة فقط (مع ملخص اختياري يمكن تعطيله).
ملزم:
- أعلى الكود: كل الإعدادات المطلوبة قابلة للتعديل.
- التعامل مع barstate.isconfirmed: اعتبر الإشارة على الشمعة المغلقة فقط.
- احترام pivots/security/lookahead إن كانت موجودة (أعد تمثيلها أو وفر Toggle أعلى الكود عند الضرورة مع تعليق).

حاء: الحصيلة (Strict Output Contract)
أخرج “ملف Python واحد” فقط — بدون Markdown وبدون شرح خارج الكود.

الملف يجب أن يحتوي أعلى الكود على هذه الإعدادات (إلزامي):
1) إعدادات الماسح:
   - SCAN_ENABLED = True
   - MAX_SYMBOLS = 0  (0 = كل الرموز)
   - SYMBOL_WHITELIST = []  (اختياري)
   - SYMBOL_BLACKLIST = []  (اختياري)
2) إعدادات الإطار وعدد الشموع:
   - TIMEFRAME = "<مطابق للمؤشر>"
   - N_BARS = <مطابق للـ max_bars_back أو متطلبات المؤشر>
   - EXTRA_BARS_MARGIN = رقم صغير لتعويض المؤشرات المتأخرة
3) فلتر عمر الإشارة (قابل للتخصيص أعلى الكود):
   - MAX_SIGNAL_AGE_BARS = رقم
   - (اختياري) MAX_SIGNAL_AGE_MINUTES = رقم
4) قواعد GRADES (إلزامي لطباعة التصنيف):
   - إذا كانت درجة المؤشر “Probability/Score” كنسبة مئوية:
     * >= 80%  => High probability / Top grade
     * >= 60%  => Moderate quality / Medium grade
     * <  60%  => Low quality / Low grade
   - ضع هذه الحدود كمتغيرات أعلى الكود:
     GRADE_HIGH_THRESHOLD = 80.0
     GRADE_MED_THRESHOLD  = 60.0
   - IMPORTANT: لا تستخدم هذه القواعد لتوليد الدرجة؛ الدرجة تُحسب من المؤشر نفسه.
     هذه القواعد فقط لتصنيف الدرجة النهائية إلى (HIGH/MED/LOW) مع النصوص المقابلة.

شكل الطباعة (إلزامي) — كل إشارة تطبع سطرًا واحدًا:
[YYYY-MM-DD HH:MM] SYMBOL TF SIGNAL=LONG|SHORT PRICE=... AGE_BARS=...
GRADE_PCT=... GRADE_LEVEL=HIGH|MED|LOW
GRADE_TEXT="High probability / Top grade" | "Moderate quality / Medium grade" | "Low quality / Low grade"

- يجب أن يطبع البرنامج النتائج على شاشة المحرر/الكونسول تلقائيًا عند التشغيل.
- يجب منع تكرار نفس الإشارة (Dedup) بمفتاح:
  (symbol, timeframe, signal_time, signal_type)

متطلبات تشغيل على Android:
- استخدم: ccxt + (numpy/pandas عند الحاجة فقط)
- ضع try/except للأخطاء الشائعة: rate limit, network, empty ohlcv
- اجعل التنفيذ سريعًا: يمكن تحديد LIMIT للشموع لكل رمز، واحترام معدل الطلبات.

//@version=5
indicator('Advanced ICT Theory - A-ICT', "📊 A-ICT", overlay=true, max_boxes_count=500, max_lines_count=500, max_labels_count=500)

//==============================================================================
// 🎯 COMPREHENSIVE USER GUIDE & CONCEPTUAL FRAMEWORK
//==============================================================================
//
// 📊 ADVANCED ICT THEORY (AIT) - INSTITUTIONAL MARKET MANIPULATION DETECTOR
//
// This enhanced version includes:
// 1. Pattern identification boxes with proper classification
// 2. Delayed classification for accurate pattern detection
// 3. Full dashboard with all metrics
// 4. Separate key/guide dashboard
// 5. Complete visual system with lines, boxes, and labels
//
//==============================================================================
// 📊 Advanced ICT Theory INPUT CONFIGURATION
//==============================================================================
group_detection = "🎯 AIT Detection Engine"
minDisplacementCandles = input.int(2, 'Min Displacement Candles', minval=1, tooltip='🎯 WHAT IT IS: The minimum number of consecutive displacement candles required to validate an ICT element like OB or FVG.\n\n⚡ HOW IT WORKS: Displacement candles show strong momentum (large body, high volume). This setting ensures only significant moves form elements.\n\n📈 HIGHER VALUES (3-5): More selective, identifies major institutional moves. Fewer but higher-quality elements.\n📉 LOWER VALUES (1-2): More sensitive, captures minor displacements. Useful for scalping.\n\n🕒 TIMEFRAME OPTIMIZATION:\n• Scalping (1-5min): 1-2 (quick detections)\n• Day Trading (15min-1H): 2-3 (balanced)\n• Swing Trading (4H-1D): 3-5 (major moves)\n\n🏦 SECTOR RECOMMENDATIONS:\n• Forex: 2 (clean price action)\n• Crypto: 2-3 (volatility)\n• Stocks: 3 (institutional focus)\n\n💡 PRO TIP: Start with 2. Increase if too many weak elements appear.', group=group_detection)
mitigationMethod = input.string('Cross', 'Mitigation Method', options=['Cross', 'Close'], tooltip='🎯 WHAT IT IS: Defines how element mitigation (break) is confirmed in ICT structure.\n\n⚡ HOW IT WORKS:\n• Cross: Price crosses the level (including wicks) - faster but riskier.\n• Close: Candle must close beyond the level - more confirmation.\n\n📈 CROSS: Responsive for momentum trades.\n📉 CLOSE: Conservative, reduces false breaks.\n\n🕒 TIMEFRAME OPTIMIZATION:\n• Lower TFs: Cross (quick signals)\n• Higher TFs: Close (reliable breaks)\n\n💡 PRO TIP: Use Cross in trending markets, Close in ranging ones.', group=group_detection)
minElementSize = input.float(0.5, 'Min Element Size (ATR)', minval=0.1, step=0.1, tooltip='🎯 WHAT IT IS: Minimum size filter for elements, as ATR multiple.\n\n⚡ HOW IT WORKS: Elements smaller than ATR × value are ignored, filtering noise.\n\n📈 HIGHER VALUES (0.8-1.5): Only large, significant elements.\n📉 LOWER VALUES (0.1-0.4): Includes smaller elements.\n\n🕒 TIMEFRAME OPTIMIZATION:\n• Short-term: 0.3-0.5\n• Long-term: 0.7-1.0\n\n💡 PRO TIP: 0.5 balances sensitivity and quality.', group=group_detection)
maxHistoryBars = input.int(300, 'Max History Bars', minval=100, maxval=500, tooltip='🎯 WHAT IT IS: Limits historical bars analyzed for elements.\n\n⚡ HOW IT WORKS: Focuses on recent data for performance.\n\n📈 HIGHER VALUES (400-500): More history, better context.\n📉 LOWER VALUES (100-200): Faster, recent focus.\n\n💡 PRO TIP: 300 is optimal for most setups.', group=group_detection)
brokenAgeThreshold = input.int(50, 'Age Threshold', minval=20, tooltip='🎯 WHAT IT IS: Bars after which mitigated elements are removed.\n\n⚡ HOW IT WORKS: Clears old visuals to reduce clutter.\n\n📈 HIGHER VALUES (60-100): Keeps more history.\n📉 LOWER VALUES (20-40): Cleaner chart.\n\n💡 PRO TIP: 50 balances relevance and clarity.', group=group_detection)
pendingTimeout = input.int(10, 'Pending Timeout', minval=5, maxval=20, tooltip='🎯 WHAT IT IS: Bars after which unclassified pending elements are removed.\n\n⚡ HOW IT WORKS: Prevents stale pending items.\n\n📈 HIGHER VALUES (15-20): Gives more time for classification.\n📉 LOWER VALUES (5-10): Quicker cleanup.\n\n💡 PRO TIP: 10 works well for dynamic markets.', group=group_detection)
minQualityThreshold = input.int(30, 'Min Quality Threshold', minval=0, maxval=100, tooltip='🎯 WHAT IT IS: Minimum quality score for displaying elements.\n\n⚡ HOW IT WORKS: Filters low-quality detections.\n\n📈 HIGHER VALUES (50-80): Only premium setups.\n📉 LOWER VALUES (10-30): More elements shown.\n\n💡 PRO TIP: Start at 30, increase for selectivity.', group=group_detection)
group_structure = "🏗️ Market Structure"
internalPivotLookback = input.int(3, 'Internal Structure Lookback', minval=2, maxval=5, tooltip='🎯 WHAT IT IS: Bars to look back for internal structure pivots.\n\n⚡ HOW IT WORKS: Detects minor swings for BOS/CHoCH.\n\n📈 HIGHER VALUES (4-5): Smoother internal structure.\n📉 LOWER VALUES (2-3): More sensitive to changes.\n\n💡 PRO TIP: 3 is standard for most TFs.', group=group_structure)
externalPivotLookback = input.int(10, 'External Structure Lookback', minval=5, maxval=20, tooltip='🎯 WHAT IT IS: Bars to look back for external structure pivots.\n\n⚡ HOW IT WORKS: Identifies major swings for overall trend.\n\n📈 HIGHER VALUES (15-20): Broader market context.\n📉 LOWER VALUES (5-10): Focus on recent structure.\n\n💡 PRO TIP: 10 balances detail and overview.', group=group_structure)
majorSwingLookback = input.int(20, 'Major Swing Lookback', minval=10, maxval=50, tooltip='🎯 WHAT IT IS: Bars to look back for major swing points.\n\n⚡ HOW IT WORKS: Detects high-level highs/lows for long-term bias.\n\n📈 HIGHER VALUES (30-50): Long-term swings.\n📉 LOWER VALUES (10-20): Medium-term focus.\n\n💡 PRO TIP: 20 for swing trading.', group=group_structure)
requireVolumeConfirm = input.bool(true, 'Require Volume Confirmation', tooltip='🎯 WHAT IT IS: Mandates above-average volume for structure breaks.\n\n⚡ HOW IT WORKS: Confirms BOS/CHoCH with volume spike.\n\n💡 PRO TIP: Enable for higher conviction, disable in low-volume markets.', group=group_structure)
requireCandleConfirm = input.bool(true, 'Require Candle Pattern Confirmation', tooltip='🎯 WHAT IT IS: Requires specific candle patterns for structure validation.\n\n⚡ HOW IT WORKS: Ensures breaks align with bullish/bearish candles.\n\n💡 PRO TIP: Enable to filter noise, disable for pure price action.', group=group_structure)
group_display = "📊 Display Configuration"
maxElementsToDisplay = input.int(10, 'Max Active Elements', minval=5, maxval=20, tooltip='🎯 WHAT IT IS: Maximum number of elements shown on chart.\n\n⚡ HOW IT WORKS: Limits visuals to recent/high-quality ones.\n\n📈 HIGHER VALUES: More elements visible.\n📉 LOWER VALUES: Cleaner chart.\n\n💡 PRO TIP: 10 prevents clutter.', group=group_display)
showIdentificationBoxes = input.bool(true, 'Show Identification Boxes', tooltip='🎯 WHAT IT IS: Displays boxes around detected patterns.\n\n⚡ HOW IT WORKS: Highlights OBs, FVGs, etc., for easy spotting.\n\n💡 PRO TIP: Essential for beginners.', group=group_display)
showPatternLines = input.bool(true, 'Show Pattern Lines', tooltip='🎯 WHAT IT IS: Draws lines for BOS/CHoCH patterns.\n\n⚡ HOW IT WORKS: Connects structure breaks visually.\n\n💡 PRO TIP: Keep on for trend analysis.', group=group_display)
showOriginLine = input.bool(true, 'Show Origin Level', tooltip='🎯 WHAT IT IS: Highlights the primary bias level.\n\n⚡ HOW IT WORKS: Shows origin of current structure.\n\n💡 PRO TIP: Key for directional bias.', group=group_display)
showMitigationLevels = input.bool(true, 'Show Mitigation Levels', tooltip='🎯 WHAT IT IS: Displays key mitigation zones.\n\n⚡ HOW IT WORKS: Marks broken levels as S/R.\n\n💡 PRO TIP: Use for targets/stops.', group=group_display)
showElementLines = input.bool(true, 'Show Element Lines', tooltip='🎯 WHAT IT IS: Draws core lines for elements.\n\n⚡ HOW IT WORKS: Visualizes midpoints of patterns.\n\n💡 PRO TIP: Fundamental feature.', group=group_display)
showTradeScore = input.bool(true, 'Show Trade Quality Score', tooltip='🎯 WHAT IT IS: Displays quality grades for setups.\n\n⚡ HOW IT WORKS: Grades [A+ to D] based on confluence.\n\n💡 PRO TIP: Focus on A/B grades.', group=group_display)
group_zones = "🔲 Identification Boxes Style"
boxStyle = input.string('Solid', 'Box Style', options=['Solid', 'Dashed', 'Dotted'], tooltip='🎯 WHAT IT IS: Appearance of pattern boxes.\n\n⚡ HOW IT WORKS: Solid for filled, Dashed/Dotted for outlines.\n\n💡 PRO TIP: Solid for emphasis.', group=group_zones)
type1BoxColor = input.color(#2962FF, 'Order Block Color', tooltip='🎯 WHAT IT IS: Color for Order Block boxes.\n\n💡 PRO TIP: Blue for bullish OBs.', group=group_zones)
type2BoxColor = input.color(#FF6B00, 'Trap Zone Color', tooltip='🎯 WHAT IT IS: Color for Trap Zone boxes.\n\n💡 PRO TIP: Orange for liquidity traps.', group=group_zones)
type3BoxColor = input.color(#00E676, 'Reversal Zone Color', tooltip='🎯 WHAT IT IS: Color for Reversal/S&R zones.\n\n💡 PRO TIP: Green for support areas.', group=group_zones)
fvgBoxColor = input.color(#9C27B0, 'FVG Color', tooltip='🎯 WHAT IT IS: Color for Fair Value Gap boxes.\n\n💡 PRO TIP: Purple for imbalance gaps.', group=group_zones)
boxTransparency = input.int(85, 'Box Transparency', minval=50, tooltip='🎯 WHAT IT IS: Opacity of boxes.\n\n📈 HIGHER: More transparent.\n📉 LOWER: More solid.\n\n💡 PRO TIP: 85 for subtle overlay.', group=group_zones)
group_levels = "📏 Level Appearance"
originLineWidth = input.int(3, 'Origin Width', minval=1, tooltip='🎯 WHAT IT IS: Thickness of origin lines.\n\n📈 HIGHER: Bolder lines.\n\n💡 PRO TIP: 3 for visibility.', group=group_levels)
mitigationLineWidth = input.int(2, 'Mitigation Width', minval=1, tooltip='🎯 WHAT IT IS: Thickness of mitigation lines.\n\n📈 HIGHER: Bolder.\n\n💡 PRO TIP: 2 for clarity.', group=group_levels)
patternLineWidth = input.int(2, 'Pattern Line Width', minval=1, tooltip='🎯 WHAT IT IS: Thickness of pattern lines.\n\n📈 HIGHER: Bolder.\n\n💡 PRO TIP: 2 standard.', group=group_levels)
labelPosition = input.int(5, 'Label Offset', minval=1, tooltip='🎯 WHAT IT IS: Distance of labels from bars.\n\n📈 HIGHER: Further right.\n\n💡 PRO TIP: 5 avoids overlap.', group=group_levels)
group_colors = "🎨 Color Scheme"
colorScheme = input.string('Professional', 'Theme', options=['Professional', 'Vibrant', 'Dark', 'Custom'], tooltip='🎯 WHAT IT IS: Preset themes for visuals.\n\n⚡ OPTIONS: Professional (clean), Vibrant (bold), Dark (subtle), Custom (user-defined).\n\n💡 PRO TIP: Professional for most users.', group=group_colors)
customOriginColor = input.color(#FFD700, 'Custom Origin', tooltip='🎯 WHAT IT IS: Custom color for origin levels in Custom theme.\n\n💡 PRO TIP: Gold for premium look.', group=group_colors)
customMitigationColor = input.color(#00BCD4, 'Custom Mitigation', tooltip='🎯 WHAT IT IS: Custom color for mitigation levels.\n\n💡 PRO TIP: Cyan for visibility.', group=group_colors)
g_dashboard = "📊 Main Dashboard Settings"
showDashboard = input.bool(true, "Show Main Dashboard", tooltip='🎯 WHAT IT IS: Toggle for main metrics dashboard.\n\n⚡ HOW IT WORKS: Displays live ICT stats.\n\n💡 PRO TIP: Always enable.', group = g_dashboard)
dashboardSize = input.string("Large", "Size", options = ["Small", "Medium", "Large"], tooltip='🎯 WHAT IT IS: Controls dashboard detail level.\n\n⚡ OPTIONS: Small (basic), Medium (expanded), Large (full with guide).\n\n💡 PRO TIP: Large for complete view.', group = g_dashboard)
dashboardPosition = input.string("Bottom Right", "Position", options = ["Top Right", "Top Left", "Bottom Right", "Bottom Left"], tooltip='🎯 WHAT IT IS: Screen position for dashboard.\n\n💡 PRO TIP: Bottom Right keeps price visible.', group = g_dashboard)
dashboardTransparency = input.int(20, "Transparency", minval = 0, tooltip='🎯 WHAT IT IS: Dashboard opacity.\n\n📈 HIGHER: More transparent.\n\n💡 PRO TIP: 20 for subtle overlay.', group = g_dashboard)
g_narrative = "📖 Narrative Dashboard Settings"
showNarrativeDashboard = input.bool(true, "Show Narrative Dashboard", tooltip='🎯 WHAT IT IS: Toggle for narrative analysis dashboard.\n\n⚡ HOW IT WORKS: Shows element details and market story.\n\n💡 PRO TIP: Enable for insights.', group = g_narrative)
narrativeDashboardPosition = input.string("Bottom Left", "Position", options = ["Top Right", "Top Left", "Bottom Right", "Bottom Left"], tooltip='🎯 WHAT IT IS: Screen position for narrative dashboard.\n\n💡 PRO TIP: Bottom Left for balance.', group = g_narrative)
narrativeTransparency = input.int(20, "Transparency", minval = 0, tooltip='🎯 WHAT IT IS: Narrative dashboard opacity.\n\n📈 HIGHER: More transparent.\n\n💡 PRO TIP: 20 for readability.', group = g_narrative)
group_mtf = "🕒 Multi-Timeframe Analysis"
showHTF = input.bool(true, "Show HTF Analysis", tooltip='🎯 WHAT IT IS: Enables higher timeframe alignment checks.\n\n⚡ HOW IT WORKS: Aligns signals with HTF bias.\n\n💡 PRO TIP: Essential for confluence.', group=group_mtf)
htfTimeframe = input.string("60", "HTF Timeframe", options=["15", "30", "60", "240", "D"], tooltip='🎯 WHAT IT IS: Higher timeframe for analysis.\n\n⚡ OPTIONS: 15min to Daily.\n\n💡 PRO TIP: Use 60min for intraday.', group=group_mtf)
htfAlignmentRequired = input.bool(true, "Require HTF Alignment", tooltip='🎯 WHAT IT IS: Mandates HTF agreement for validity.\n\n⚡ HOW IT WORKS: Filters misaligned signals.\n\n💡 PRO TIP: Enable for better accuracy.', group=group_mtf)
group_liquidity = "💧 Liquidity Mapping"
showLiquidity = input.bool(true, "Show Liquidity Levels", tooltip='🎯 WHAT IT IS: Displays buy/sell side liquidity lines.\n\n⚡ HOW IT WORKS: Tracks highs/lows for sweeps.\n\n💡 PRO TIP: Key for trap identification.', group=group_liquidity)
liquidityLookback = input.int(20, "Liquidity Lookback", minval=10, tooltip='🎯 WHAT IT IS: Bars back for liquidity calculation.\n\n📈 HIGHER: Broader liquidity view.\n\n💡 PRO TIP: 20 standard.', group=group_liquidity)
showSweptLiquidity = input.bool(true, "Show Swept Liquidity", tooltip='🎯 WHAT IT IS: Visualizes swept (broken) liquidity.\n\n⚡ HOW IT WORKS: Dotted lines for swept levels.\n\n💡 PRO TIP: Enable to track manipulations.', group=group_liquidity)
group_premium = "⚖️ Premium/Discount"
showPremiumDiscount = input.bool(true, "Show Premium/Discount Zones", tooltip='🎯 WHAT IT IS: Highlights premium/discount areas.\n\n⚡ HOW IT WORKS: Based on equilibrium calculation.\n\n💡 PRO TIP: Trade discounts in uptrends.', group=group_premium)
pdLookback = input.int(50, "P/D Lookback", minval=20, tooltip='🎯 WHAT IT IS: Bars for premium/discount calculation.\n\n📈 HIGHER: Smoother zones.\n\n💡 PRO TIP: 50 for accuracy.', group=group_premium)
group_sessions = "⏰ Sessions & Killzones"
showSessions = input.bool(true, "Show Trading Sessions", tooltip='🎯 WHAT IT IS: Colors session backgrounds.\n\n⚡ HOW IT WORKS: Asian (blue), London (yellow), NY (green).\n\n💡 PRO TIP: For session-based trading.', group=group_sessions)
showKillzones = input.bool(true, "Show ICT Killzones", tooltip='🎯 WHAT IT IS: Highlights high-volatility killzones.\n\n⚡ HOW IT WORKS: Red boxes for manipulation periods.\n\n💡 PRO TIP: Trade during killzones.', group=group_sessions)
group_ipda = "⏰ Interbank Price Delivery Algorithm - IPDA Windows"
showIPDA = input.bool(true, "Show IPDA Windows", tooltip='🎯 WHAT IT IS: Displays IPDA delivery periods.\n\n⚡ HOW IT WORKS: Blue (Asian), Orange (London Open), Purple (NY Open).\n\n💡 PRO TIP: Watch for deliveries in these windows.', group=group_ipda)
// ========================================
 // TYPE DEFINITIONS
// ========================================
type ICTElement
    float high = na
    float low = na
    int startBar = na
    int endBar = na
    bool mitigated = false
    int mitigationBar = na
    string elementType = "Pending"
    string timeframe = ""
    bool isOrigin = false
    bool isMitigation = false
    float strength = 0.5
    bool insideKillzone = false
    bool nearLiquidity = false
    float qualityScore = 0.0
    bool causedBOS = false
    bool inLogicalArea = false
    bool hasHighVolumeFVG = false
    string narrativeRole = ""
    box identificationBox = na
    line patternLine = na
    label patternLabel = na
type MarketStructure
    bool bullishBOS = false
    bool bearishBOS = false
    bool choch = false
    int lastBOSBar = na
    float lastBOSPrice = na
    bool internalBullishBOS = false
    bool internalBearishBOS = false
    bool externalBullishBOS = false
    bool externalBearishBOS = false
    float lastInternalHigh = na
    float lastInternalLow = na
    float lastExternalHigh = na
    float lastExternalLow = na
    string primaryTrend = "NEUTRAL"
    string orderFlow = "NEUTRAL"
type FVGPattern
    bool detected = false
    bool isBullish = false
    float high = na
    float low = na
    int startBar = na
    box fvgBox = na
    line fvgLine = na
    label fvgLabel = na
type ICTPattern
    string name
    bool detected = false
    int detectionBar = na
    float strength = 0.0
type TradeScore
    float momentum = 0
    float structure = 0
    float liquidity = 0
    float confluence = 0
    float total = 0
    string grade = ""
type TradeSuggestion
    string action = ""
    float entryPrice = 0
    float stopLoss = 0
    float takeProfit1 = 0
    float takeProfit2 = 0
    float riskReward = 0
type SmartMoneyFlow
    float buyVolume = 0
    float sellVolume = 0
    float netFlow = 0
    string bias = "NEUTRAL"
type MarketNarrative
    string currentPhase = ""
    string lastEvent = "No recent structural change"
    string nextExpectation = ""
    string causalSequence = ""
    int sequenceStartBar = 0
    float keyLevel = na
    string keySetup = ""
type IPDAWindow
    string name
    string startTime
    string endTime
    bool active
// ========================================
 // GLOBAL CALCULATIONS
// ========================================
volumeSMA20 = ta.sma(volume, 20)
volumeSMA10 = ta.sma(volume, 10)
atr14 = ta.atr(14)
rsi14 = ta.rsi(close, 14)
avgRange20 = ta.sma(high - low, 20)
trendSMA = ta.sma(close, 50)
internalHigh = ta.pivothigh(high, internalPivotLookback, internalPivotLookback)
internalLow = ta.pivotlow(low, internalPivotLookback, internalPivotLookback)
externalHigh = ta.pivothigh(high, externalPivotLookback, externalPivotLookback)
externalLow = ta.pivotlow(low, externalPivotLookback, externalPivotLookback)
majorHigh = ta.pivothigh(high, majorSwingLookback, majorSwingLookback)
majorLow = ta.pivotlow(low, majorSwingLookback, majorSwingLookback)
[htfH, htfL, htfC, htfO, htfV] = request.security(syminfo.tickerid, htfTimeframe, [high, low, close, open, volume], lookahead=barmerge.lookahead_on)
htfSMA20 = request.security(syminfo.tickerid, htfTimeframe, ta.sma(close, 20), lookahead=barmerge.lookahead_on)
htfTrend = htfC > htfSMA20 ? "BULLISH" : htfC < htfSMA20 ? "BEARISH" : "NEUTRAL"
htfBias = htfC > htfH[1] ? "BULLISH" : htfC < htfL[1] ? "BEARISH" : "NEUTRAL"
bsl = ta.highest(high, liquidityLookback)
ssl = ta.lowest(low, liquidityLookback)
bslSwept = high > bsl[1] and close < bsl[1]
sslSwept = low < ssl[1] and close > ssl[1]
pdHigh = ta.highest(high, pdLookback)
pdLow = ta.lowest(low, pdLookback)
equilibrium = (pdHigh + pdLow) / 2
isPremium = close > equilibrium + (pdHigh - equilibrium) * 0.5
isDiscount = close < equilibrium - (equilibrium - pdLow) * 0.5
isEquilibrium = not isPremium and not isDiscount
isAsianSession = not na(time(timeframe.period, "0000-0800", "UTC"))
isLondonSession = not na(time(timeframe.period, "0800-1200", "UTC"))
isNYSession = not na(time(timeframe.period, "1200-1600", "UTC"))
isLondonKZ = not na(time(timeframe.period, "0800-0900", "UTC"))
isNYAMKZ = not na(time(timeframe.period, "1330-1430", "UTC"))
isNYPMKZ = not na(time(timeframe.period, "1500-1600", "UTC"))
inKillzone = isLondonKZ or isNYAMKZ or isNYPMKZ
ipdaAsianRange = not na(time(timeframe.period, "0000-0300", "UTC"))
ipdaLondonOpen = not na(time(timeframe.period, "0800-0900", "UTC"))
ipdaNYOpen = not na(time(timeframe.period, "1330-1430", "UTC"))
// ========================================
 // COLOR THEMES
// ========================================
getColorTheme(theme) =>
    switch theme
        'Vibrant' => [color.new(#FFD700, 0), color.new(#00E5FF, 0), color.new(#FF4081, 0), color.new(#76FF03, 0)]
        'Dark' => [color.new(#FFA726, 0), color.new(#42A5F5, 0), color.new(#AB47BC, 0), color.new(#66BB6A, 0)]
        'Custom' => [customOriginColor, customMitigationColor, color.new(#808080, 0), color.new(#404040, 0)]
        => [color.new(#FFB800, 0), color.new(#00ACC1, 0), color.new(#7B1FA2, 0), color.new(#43A047, 0)]
[originColor, mitigationColor, brokenColor, bgColor] = getColorTheme(colorScheme)
// ========================================
 // GLOBAL VARIABLES
// ========================================
var array<ICTElement> elements = array.new<ICTElement>()
var array<line> elementLines = array.new<line>()
var array<label> elementLabels = array.new<label>()
var array<line> structureLines = array.new<line>()
var array<label> structureLabels = array.new<label>()
var array<FVGPattern> fvgPatterns = array.new<FVGPattern>()
var table dashboard = na
var table narrativeDashboard = na
var ICTElement currentOrigin = na
var array<ICTElement> mitigationLevels = array.new<ICTElement>()
var int lastDetectionBar = 0
var MarketStructure ms = MarketStructure.new()
var MarketNarrative narrative = MarketNarrative.new()
var box asianBox = na
var box londonBox = na
var box nyBox = na
var box londonKZBox = na
var box nyamKZBox = na
var box nypmKZBox = na
var box premiumBox = na
var box discountBox = na
var box equilibriumBox = na
// ========================================
 // CORE FUNCTIONS
// ========================================
safeGet(arr, index) =>
    size = array.size(arr)
    size > 0 and index >= 0 and index < size ? array.get(arr, index) : na
detectAdvancedStructure() =>
    ms.primaryTrend := close > trendSMA ? "BULLISH" : close < trendSMA ? "BEARISH" : "NEUTRAL"
    if not na(internalHigh)
        ms.lastInternalHigh := internalHigh
    if not na(internalLow)
        ms.lastInternalLow := internalLow
    if not na(externalHigh)
        ms.lastExternalHigh := externalHigh
    if not na(externalLow)
        ms.lastExternalLow := externalLow
    ms.internalBullishBOS := not na(ms.lastInternalHigh) and high > ms.lastInternalHigh
    ms.internalBearishBOS := not na(ms.lastInternalLow) and low < ms.lastInternalLow
    volumeConfirm = not requireVolumeConfirm or volume > volumeSMA20 * 1.2
    bullishCandleConfirm = not requireCandleConfirm or (close > open and close[1] > open[1])
    bearishCandleConfirm = not requireCandleConfirm or (close < open and close[1] < open[1])
    if not na(ms.lastExternalHigh) and high > ms.lastExternalHigh and volumeConfirm and bullishCandleConfirm
        ms.externalBullishBOS := true
        ms.bullishBOS := true
        ms.bearishBOS := false
        ms.lastBOSBar := bar_index
        ms.lastBOSPrice := high
        ms.orderFlow := "BULLISH"
    else
        ms.externalBullishBOS := false
    if not na(ms.lastExternalLow) and low < ms.lastExternalLow and volumeConfirm and bearishCandleConfirm
        ms.externalBearishBOS := true
        ms.bearishBOS := true
        ms.bullishBOS := false
        ms.lastBOSBar := bar_index
        ms.lastBOSPrice := low
        ms.orderFlow := "BEARISH"
    else
        ms.externalBearishBOS := false
    ms.choch := false
    if ms.orderFlow == "BULLISH" and ms.externalBearishBOS
        ms.choch := true
        narrative.lastEvent := "CHoCH: Bullish to Bearish"  
    if ms.orderFlow == "BEARISH" and ms.externalBullishBOS
        ms.choch := true
        narrative.lastEvent := "CHoCH: Bearish to Bullish"
detectFVG() =>
    fvg = FVGPattern.new()
    minGapSize = atr14 * 0.5
    bullishGap = low > high[2]
    if bullishGap
        gapSize = low - high[2]
        if gapSize > minGapSize and close > open and volume > volumeSMA20 * 1.2
            fvg.detected := true
            fvg.isBullish := true
            fvg.high := low
            fvg.low := high[2]
            fvg.startBar := bar_index - 2
    bearishGap = high < low[2]
    if bearishGap
        gapSize = low[2] - high
        if gapSize > minGapSize and close < open and volume > volumeSMA20 * 1.2
            fvg.detected := true
            fvg.isBullish := false
            fvg.high := low[2]
            fvg.low := high
            fvg.startBar := bar_index - 2       
    fvg
calculateTradeScore(element) =>
    score = TradeScore.new()
    if na(element)
        score
    else
        score.momentum := element.strength * 25
        if element.causedBOS
            score.structure := 25
        else if ms.externalBullishBOS and element.elementType == "Order Block"
            score.structure := 20
        else if element.elementType == "Trap Zone" and element.nearLiquidity
            score.structure := 15
        else if element.inLogicalArea
            score.structure := 10
        else
            score.structure := 5
        if element.nearLiquidity and (bslSwept or sslSwept)
            score.liquidity := 25
        else if element.nearLiquidity
            score.liquidity := 15
        else
            score.liquidity := 5
        confluenceFactors = 0
        if element.insideKillzone
            confluenceFactors += 2
        if element.inLogicalArea
            confluenceFactors += 2
        if htfBias == ms.orderFlow
            confluenceFactors += 3
        score.confluence := math.min(confluenceFactors * 3.5, 25)
        score.total := score.momentum + score.structure + score.liquidity + score.confluence
        score.grade := score.total >= 80 ? "A+" : score.total >= 65 ? "A" : score.total >= 50 ? "B" : score.total >= 40 ? "C" : "D"   
        score
calculateSmartMoneyFlow() =>
    flow = SmartMoneyFlow.new()
    flow.buyVolume := 0.0
    flow.sellVolume := 0.0
    flow.netFlow := 0.0
    flow.bias := "NEUTRAL"
    if volume > 0
        priceRange = math.max(high - low, 0.00001)
        if close > open
            flow.buyVolume := volume * (close - low) / priceRange
            flow.sellVolume := volume - flow.buyVolume
        else
            flow.sellVolume := volume * (high - close) / priceRange
            flow.buyVolume := volume - flow.sellVolume
        flow.netFlow := flow.buyVolume - flow.sellVolume
        if flow.netFlow > volumeSMA20 * 0.2
            flow.bias := "STRONG BULLISH FLOW"
        else if flow.netFlow > 0
            flow.bias := "BULLISH FLOW"
        else if flow.netFlow < -volumeSMA20 * 0.2
            flow.bias := "STRONG BEARISH FLOW"
        else if flow.netFlow < 0
            flow.bias := "BEARISH FLOW"
        else
            flow.bias := "NEUTRAL"
    flow
generateNarrativeTradeSuggestion(element) =>
    suggestion = TradeSuggestion.new()
    
    if na(element) or element.mitigated
        suggestion
    else
        score = calculateTradeScore(element)
        
        if score.total >= 55 and element.narrativeRole != ""
            if ms.orderFlow == "BULLISH" and element.elementType == "Type 1" and isDiscount
                suggestion.action := "LONG - " + element.narrativeRole
                suggestion.entryPrice := close
                suggestion.stopLoss := element.low - atr14 * 0.2
                suggestion.takeProfit1 := close + (close - suggestion.stopLoss) * 1.5
                suggestion.takeProfit2 := close + (close - suggestion.stopLoss) * 3
                if element.nearLiquidity
                    suggestion.takeProfit1 := bsl
            else if ms.orderFlow == "BEARISH" and element.elementType == "Type 1" and isPremium
                suggestion.action := "SHORT - " + element.narrativeRole
                suggestion.entryPrice := close
                suggestion.stopLoss := element.high + atr14 * 0.2
                suggestion.takeProfit1 := close - (suggestion.stopLoss - close) * 1.5
                suggestion.takeProfit2 := close - (suggestion.stopLoss - close) * 3
                if element.nearLiquidity
                    suggestion.takeProfit1 := ssl      
        if suggestion.action != ""
            suggestion.riskReward := math.abs(suggestion.takeProfit1 - suggestion.entryPrice) / math.abs(suggestion.entryPrice - suggestion.stopLoss)
        suggestion
detectAdvancedICTPatterns() =>
    patterns = array.new<ICTPattern>()
    breakerBlock = ICTPattern.new()
    breakerBlock.name := "Breaker Block"
    breakerBlock.detected := false
    if array.size(elements) >= 2
        lastElement = safeGet(elements, array.size(elements) - 1)
        prevElement = safeGet(elements, array.size(elements) - 2)
        if not na(lastElement) and not na(prevElement)
            if lastElement.mitigated and prevElement.mitigated
                if lastElement.elementType == "Type 1" and prevElement.elementType == "Type 2"
                    breakerBlock.detected := true
                    breakerBlock.detectionBar := bar_index
                    breakerBlock.strength := (lastElement.strength + prevElement.strength) / 2
                    narrative.lastEvent := "Breaker Block formed"
    array.push(patterns, breakerBlock)
    mitigationBlock = ICTPattern.new()
    mitigationBlock.name := "Mitigation Block"
    mitigationBlock.detected := false  
    if array.size(elements) >= 1
        lastElement = safeGet(elements, array.size(elements) - 1)
        if not na(lastElement) and lastElement.mitigated and lastElement.causedBOS
            mitigationBlock.detected := true
            mitigationBlock.detectionBar := bar_index
            mitigationBlock.strength := lastElement.strength           
    array.push(patterns, mitigationBlock)    
    patterns
buildMarketNarrative() =>
    sessionDetail = ""
    if inKillzone
        if isLondonKZ
            sessionDetail := "London KZ - Expect directional move"
        else if isNYAMKZ
            sessionDetail := "NY AM KZ - Peak volatility window"
        else if isNYPMKZ
            sessionDetail := "NY PM KZ - Position squaring"
        narrative.currentPhase := sessionDetail
    else if isAsianSession
        narrative.currentPhase := "Asian Range - Accumulation phase"
    else if isLondonSession
        narrative.currentPhase := "London Session - Expansion expected"
    else if isNYSession
        narrative.currentPhase := "NY Session - Continuation/Reversal"
    else
        narrative.currentPhase := "Inter-session - Low probability"
    sequence = ""
    recentLiquiditySweep = (bslSwept or sslSwept)
    recentBOS = bar_index - ms.lastBOSBar < 10
    hasUnmitigatedOB = false
    nearestOBLevel = 0.0
    strongestElement = ICTElement.new()
    if array.size(elements) > 0
        for i = array.size(elements) - 1 to math.max(0, array.size(elements) - 10)
            e = safeGet(elements, i)
            if not na(e) and not e.mitigated and e.elementType != "Pending"
                if e.qualityScore > 60
                    hasUnmitigatedOB := true
                    nearestOBLevel := (e.high + e.low) / 2
                    if e.qualityScore > strongestElement.qualityScore
                        strongestElement := e
    if recentLiquiditySweep
        sequence += "💧 " + (bslSwept ? "Buy-side" : "Sell-side") + " liquidity swept → "
        narrative.keyLevel := bslSwept ? bsl : ssl
    if ms.choch
        sequence += "⚡ CHoCH confirmed → Bias shift to " + ms.orderFlow + " → "
    if recentBOS
        bosType = ms.externalBullishBOS ? "Bullish" : ms.externalBearishBOS ? "Bearish" : "Internal"
        sequence += "📊 " + bosType + " BOS → "
    if hasUnmitigatedOB
        sequence += "🎯 Active " + strongestElement.elementType + " at " + str.tostring(nearestOBLevel, "#.####") + " → "
    expectation = ""
    if recentLiquiditySweep and not recentBOS
        if bslSwept
            expectation := "🔻 Reversal likely after BSL sweep. Watch for bearish OB formation near " + str.tostring(bsl, "#.####")
        else
            expectation := "🔺 Reversal likely after SSL sweep. Watch for bullish OB formation near " + str.tostring(ssl, "#.####")
    else if recentBOS and hasUnmitigatedOB
        if ms.orderFlow == "BULLISH"
            if close > nearestOBLevel
                expectation := "📉 Pullback expected to bullish OB at " + str.tostring(nearestOBLevel, "#.####") + " before continuation up"
            else
                expectation := "🚀 Price approaching bullish OB. Long entry opportunity near " + str.tostring(nearestOBLevel, "#.####")
        else
            if close < nearestOBLevel
                expectation := "📈 Retracement expected to bearish OB at " + str.tostring(nearestOBLevel, "#.####") + " before continuation down"
            else
                expectation := "💥 Price approaching bearish OB. Short entry opportunity near " + str.tostring(nearestOBLevel, "#.####")
    else if ms.choch
        expectation := "🔄 Character change! Old " + (ms.orderFlow == "BULLISH" ? "resistance" : "support") + " becomes " + (ms.orderFlow == "BULLISH" ? "support" : "resistance") + ". First retest pending"
    else if isPremium and ms.orderFlow == "BEARISH"
        expectation := "📍 In premium zone + bearish bias. Seeking sell setups. Target: " + str.tostring(equilibrium, "#.####")
    else if isDiscount and ms.orderFlow == "BULLISH"
        expectation := "📍 In discount zone + bullish bias. Seeking buy setups. Target: " + str.tostring(equilibrium, "#.####")
    else if inKillzone
        if isLondonKZ
            expectation := "⏰ London KZ active. Expect sweep of Asian high/low at " + str.tostring(bsl, "#.####") + "/" + str.tostring(ssl, "#.####")
        else if isNYAMKZ
            if ms.orderFlow == "NEUTRAL"
                expectation := "⏰ NY AM KZ: Awaiting directional commitment. Monitor " + str.tostring(bsl, "#.####") + " and " + str.tostring(ssl, "#.####")
            else
                expectation := "⏰ NY AM KZ + " + ms.orderFlow + " bias. Expect acceleration " + (ms.orderFlow == "BULLISH" ? "higher" : "lower")
        else if isNYPMKZ
            expectation := "⏰ NY PM KZ: Position squaring time. Fade moves without strong volume"
    else if isEquilibrium
        nearBSL = math.abs(close - bsl) < atr14 * 2
        nearSSL = math.abs(close - ssl) < atr14 * 2
        if nearBSL
            expectation := "⚖️ At equilibrium near BSL. Rejection = Short, Break = Long targeting " + str.tostring(bsl + atr14 * 2, "#.####")
        else if nearSSL
            expectation := "⚖️ At equilibrium near SSL. Rejection = Long, Break = Short targeting " + str.tostring(ssl - atr14 * 2, "#.####")
        else
            expectation := "⚖️ At equilibrium. Wait for directional break with volume > " + str.tostring(math.round(volumeSMA20 * 1.5), "#")
    else
        if array.size(elements) == 0
            expectation := "🔍 No quality setups detected. Wait for clear structure break or liquidity sweep"
        else
            expectation := "📊 Monitoring " + str.tostring(array.size(elements)) + " elements. Next key level: " + 
                          (close > equilibrium ? str.tostring(bsl, "#.####") + " (BSL)" : str.tostring(ssl, "#.####") + " (SSL)")
    narrative.nextExpectation := expectation
    narrative.causalSequence := sequence
getEnhancedMarketNarrative() =>
    buildMarketNarrative()
    fullNarrative = "📍 " + narrative.currentPhase + "\n"
    fullNarrative += "🎯 Bias: " + ms.orderFlow
    if htfBias == ms.orderFlow and ms.orderFlow != "NEUTRAL"
        fullNarrative += " ✅ HTF Aligned"
    else if htfBias != "NEUTRAL" and ms.orderFlow != "NEUTRAL" and htfBias != ms.orderFlow
        fullNarrative += " ⚠️ HTF Conflict"
    fullNarrative += "\n"
    marketPosition = isPremium ? "Premium" : isDiscount ? "Discount" : "Equilibrium"
    fullNarrative += "📊 Zone: " + marketPosition
    if isPremium or isDiscount
        fullNarrative += " (" + str.tostring(math.round(math.abs(close - equilibrium) / atr14), "#") + " ATR from EQ)"
    fullNarrative += "\n"
    if narrative.causalSequence != ""
        fullNarrative += "🔗 Events: " + narrative.causalSequence + "\n"
    fullNarrative += "🎯 " + narrative.nextExpectation + "\n"
    if array.size(elements) > 0
        lastE = safeGet(elements, array.size(elements) - 1)
        if not na(lastE) and not lastE.mitigated
            score = calculateTradeScore(lastE)
            if score.total >= 60
                suggestion = generateNarrativeTradeSuggestion(lastE)
                if suggestion.action != ""
                    fullNarrative += "⚡ Setup Ready: " + suggestion.action + " RR:" + str.tostring(suggestion.riskReward, "#.#")                    
    fullNarrative
classifyElement(element) =>
    if na(element)
        element
    else
        age = bar_index - element.endBar
        causedBullishBOS = false
        causedBearishBOS = false        
        if ms.bullishBOS and ms.lastBOSBar > element.endBar and ms.lastBOSBar - element.endBar <= 10
            causedBullishBOS := true
            element.causedBOS := true
        if ms.bearishBOS and ms.lastBOSBar > element.endBar and ms.lastBOSBar - element.endBar <= 10
            causedBearishBOS := true
            element.causedBOS := true
        liquiditySweep = (bslSwept or sslSwept) and bar_index - element.endBar <= 5
        highVolume = false
        if element.endBar >= bar_index - maxHistoryBars
            idx = bar_index - element.endBar
            if idx >= 0 and idx < 500
                highVolume := volume[idx] > volumeSMA20[idx] * 1.5
        if causedBullishBOS or causedBearishBOS
            element.elementType := "Order Block"
            element.narrativeRole := causedBullishBOS ? "Bullish OB (caused BOS)" : "Bearish OB (caused BOS)"
            element.strength := 0.9
        else if liquiditySweep
            element.elementType := "Trap Zone"
            element.narrativeRole := "Liquidity Trap"
            element.strength := 0.8
        else if highVolume and element.inLogicalArea
            element.elementType := "Order Block"
            element.narrativeRole := ms.orderFlow + " OB (high volume)"
            element.strength := 0.7
        else if age > 5
            element.elementType := "S/R Zone"
            element.narrativeRole := "Support/Resistance"
            element.strength := 0.5           
        element  
determineAdvancedICTType(e, breakDirection) =>
    ictType = "Pending"
    strength = 0.5
    narrativeRole = ""
    if na(e)
        [ictType, strength, narrativeRole]
    else
        barsSinceElement = bar_index - e.endBar
        if barsSinceElement < 2
            [ictType, strength, narrativeRole]
        else
            isStrongMove = math.abs(close - close[2]) > atr14 * 1.5
            hasVolume = volume > volumeSMA20 * 1.3 and volume[1] > volumeSMA20 * 1.2
            hasBOS = ms.bullishBOS or ms.bearishBOS
            hasExternalBOS = ms.externalBullishBOS or ms.externalBearishBOS
            hasLiquiditySweep = bslSwept or sslSwept
            isPivot = not na(internalHigh) or not na(internalLow)
            causedStructuralBreak = false
            if array.size(elements) > 0
                for i = array.size(elements) - 1 to math.max(0, array.size(elements) - 5)
                    elem = safeGet(elements, i)
                    if not na(elem) and elem.endBar >= ms.lastBOSBar - 5 and elem.endBar <= ms.lastBOSBar
                        causedStructuralBreak := true
                        elem.causedBOS := true
                        break
            if breakDirection == "up"
                if hasExternalBOS and hasVolume and isStrongMove and e.insideKillzone
                    ictType := "Type 1"
                    strength := math.min(volume / volumeSMA20 * 0.7, 1.0)
                    narrativeRole := "Momentum continuation after external BOS"
                else if hasLiquiditySweep and close < open
                    ictType := "Type 2"
                    strength := 0.8
                    narrativeRole := "Liquidity grab and reversal"
                else if isPivot or (rsi14 > 70 and not hasVolume)
                    ictType := "Type 3"
                    strength := 0.6
                    narrativeRole := "Potential reversal pivot"
                else
                    ictType := "Type 3"
                    strength := 0.5
                    narrativeRole := "Minor structure"
            else
                if hasExternalBOS and hasVolume and isStrongMove and e.insideKillzone
                    ictType := "Type 1"
                    strength := math.min(volume / volumeSMA20 * 0.7, 1.0)
                    narrativeRole := "Momentum continuation after external BOS"
                else if hasLiquiditySweep and close > open
                    ictType := "Type 2"
                    strength := 0.8
                    narrativeRole := "Liquidity grab and reversal"
                else if isPivot or (rsi14 < 30 and not hasVolume)
                    ictType := "Type 3"
                    strength := 0.6
                    narrativeRole := "Potential reversal pivot"
                else
                    ictType := "Type 3"
                    strength := 0.5
                    narrativeRole := "Minor structure"
            [ictType, math.min(strength, 1.0), narrativeRole]
assessQuality(element) =>
    if na(element)
        0.0
    else
        score = 0.0
        if element.insideKillzone
            score += 20
        else if isLondonSession or isNYSession
            score += 10  
        if (ms.orderFlow == "BULLISH" and isDiscount) or (ms.orderFlow == "BEARISH" and isPremium)
            score += 25
            element.inLogicalArea := true
        else if isEquilibrium
            score += 10
        if volume > volumeSMA20 * 1.5
            score += 20
        fvgPresent = math.abs(high[1] - low[2]) > atr14 * 0.5 or math.abs(low[1] - high[2]) > atr14 * 0.5
        if fvgPresent and volume[1] > volumeSMA20 * 1.3
            score += 20
            element.hasHighVolumeFVG := true
        if htfBias == ms.orderFlow
            score += 15  
        math.min(score, 100.0)
getIPDAWindows() =>
    windows = array.new<IPDAWindow>()
    array.push(windows, IPDAWindow.new("Asian Range", "0000", "0300", not na(time(timeframe.period, "0000-0300", "UTC"))))
    array.push(windows, IPDAWindow.new("London Open", "0800", "0900", not na(time(timeframe.period, "0800-0900", "UTC"))))
    array.push(windows, IPDAWindow.new("NY Open", "1330", "1430", not na(time(timeframe.period, "1330-1430", "UTC"))))
// ========================================
 // DASHBOARD FUNCTIONS
// ========================================
cell(t, col, row, txt, txtColor, bgColor, trans) =>
    table.cell(t, col, row, txt, text_color=txtColor, bgcolor=color.new(bgColor, trans), text_size=size.small)
drawDashboard(t) =>
    table result = na
    if not showDashboard
        if not na(t)
            table.delete(t)
    else
        if not na(t)
            table.delete(t)
        type1Count = 0
        type2Count = 0
        type3Count = 0
        pendingCount = 0
        mitigatedCount = 0
        unmitigatedCount = 0
        highQualityCount = 0
        if array.size(elements) > 0
            for i = 0 to math.min(array.size(elements) - 1, 50)
                e = safeGet(elements, i)
                if not na(e)
                    if e.elementType == "Order Block"
                        type1Count += 1
                    else if e.elementType == "Trap Zone"
                        type2Count += 1
                    else if e.elementType == "Reversal Zone" or e.elementType == "S/R Zone"
                        type3Count += 1
                    else if e.elementType == "Pending"
                        pendingCount += 1
                    if e.mitigated
                        mitigatedCount += 1
                    else
                        unmitigatedCount += 1                       
                    if e.qualityScore >= 65
                        highQualityCount += 1       
        smFlow = calculateSmartMoneyFlow()
        int base_rows = 10
        int medium_extra = 5
        int large_extra = 15
        int buffer = 5
        int footer_row = 1
        int max_rows = (dashboardSize == "Large" ? base_rows + medium_extra + large_extra : dashboardSize == "Medium" ? base_rows + medium_extra : base_rows) + buffer + footer_row
        pos = dashboardPosition == "Top Left" ? position.top_left : dashboardPosition == "Top Right" ? position.top_right : dashboardPosition == "Bottom Left" ? position.bottom_left : position.bottom_right
        table currentTable = table.new(pos, 4, max_rows, border_width = 1)       
        row = 0
        cell(currentTable, 0, row, "Advanced ICT Theory", color.white, color.black, dashboardTransparency)
        table.merge_cells(currentTable, 0, row, 3, row)
        row += 1
        cell(currentTable, 0, row, "ICT METRICS & BREAKDOWN", color.white, #2A2E39, dashboardTransparency)
        table.merge_cells(currentTable, 0, row, 3, row)
        row += 1
        cell(currentTable, 0, row, "Total Elements", color.white, color.gray, dashboardTransparency)
        cell(currentTable, 1, row, str.tostring(array.size(elements)), color.white, color.gray, dashboardTransparency)
        cell(currentTable, 2, row, "High Quality", color.green, color.gray, dashboardTransparency)
        cell(currentTable, 3, row, str.tostring(highQualityCount), color.white, color.gray, dashboardTransparency)
        row += 1       
        cell(currentTable, 0, row, "Pending", color.yellow, color.gray, dashboardTransparency)
        cell(currentTable, 1, row, str.tostring(pendingCount), color.white, color.gray, dashboardTransparency)
        cell(currentTable, 2, row, "Unmitigated", #00E676, color.gray, dashboardTransparency)
        cell(currentTable, 3, row, str.tostring(unmitigatedCount - pendingCount), color.white, color.gray, dashboardTransparency)
        row += 1       
        cell(currentTable, 0, row, "Mitigated", #FF5252, color.gray, dashboardTransparency)
        cell(currentTable, 1, row, str.tostring(mitigatedCount), color.white, color.gray, dashboardTransparency)
        cell(currentTable, 2, row, "Order Blocks", type1BoxColor, color.gray, dashboardTransparency)
        cell(currentTable, 3, row, str.tostring(type1Count), color.white, color.gray, dashboardTransparency)
        row += 1        
        cell(currentTable, 0, row, "Trap Zones", type2BoxColor, color.gray, dashboardTransparency)
        cell(currentTable, 1, row, str.tostring(type2Count), color.white, color.gray, dashboardTransparency)
        cell(currentTable, 2, row, "Reversal/S&R", type3BoxColor, color.gray, dashboardTransparency)
        cell(currentTable, 3, row, str.tostring(type3Count), color.white, color.gray, dashboardTransparency)
        row += 1       
        cell(currentTable, 0, row, "FVGs Active", fvgBoxColor, color.gray, dashboardTransparency)
        cell(currentTable, 1, row, str.tostring(array.size(fvgPatterns)), color.white, color.gray, dashboardTransparency)
        row += 1
        cell(currentTable, 0, row, "STRUCTURE & MARKET CONTEXT", color.white, #2A2E39, dashboardTransparency)
        table.merge_cells(currentTable, 0, row, 3, row)
        row += 1
        cell(currentTable, 0, row, "Order Flow", color.white, color.gray, dashboardTransparency)
        flowColor = ms.orderFlow == "BULLISH" ? color.green : ms.orderFlow == "BEARISH" ? color.red : color.yellow
        cell(currentTable, 1, row, ms.orderFlow, flowColor, color.gray, dashboardTransparency)
        cell(currentTable, 2, row, "Last BOS", color.white, color.gray, dashboardTransparency)
        bosText = ms.externalBullishBOS ? "External Bull" : ms.externalBearishBOS ? "External Bear" : ms.internalBullishBOS ? "Internal Bull" : ms.internalBearishBOS ? "Internal Bear" : "None"
        cell(currentTable, 3, row, bosText, color.white, color.gray, dashboardTransparency)
        row += 1        
        cell(currentTable, 0, row, "CHoCH Active", color.white, color.gray, dashboardTransparency)
        chochColor = ms.choch ? color.orange : color.gray
        cell(currentTable, 1, row, ms.choch ? "YES" : "NO", chochColor, color.gray, dashboardTransparency)
        cell(currentTable, 2, row, "HTF Bias", color.white, color.gray, dashboardTransparency)
        htfColor = htfBias == "BULLISH" ? color.green : htfBias == "BEARISH" ? color.red : color.yellow
        alignText = htfBias == ms.orderFlow ? " ✓" : " ✗"
        cell(currentTable, 3, row, htfBias + alignText, htfColor, color.gray, dashboardTransparency)
        row += 1       
        cell(currentTable, 0, row, "Market State", color.white, color.gray, dashboardTransparency)
        stateText = isPremium ? "PREMIUM" : isDiscount ? "DISCOUNT" : "EQUILIBRIUM"
        stateColor = isPremium ? color.red : isDiscount ? color.green : color.yellow
        cell(currentTable, 1, row, stateText, stateColor, color.gray, dashboardTransparency)
        cell(currentTable, 2, row, "Liquidity", color.white, color.gray, dashboardTransparency)
        liqText = bslSwept ? "BSL Swept" : sslSwept ? "SSL Swept" : "Protected"
        liqColor = bslSwept or sslSwept ? color.orange : color.white
        cell(currentTable, 3, row, liqText, liqColor, color.gray, dashboardTransparency)
        row += 1
        if dashboardSize == "Medium" or dashboardSize == "Large"
            cell(currentTable, 0, row, "SMART MONEY FLOW", color.white, #2A2E39, dashboardTransparency)
            table.merge_cells(currentTable, 0, row, 3, row)
            row += 1
            cell(currentTable, 0, row, "Net Flow", color.white, color.gray, dashboardTransparency)
            flowColor_SM = smFlow.netFlow > 0 ? color.green : smFlow.netFlow < 0 ? color.red : color.yellow
            cell(currentTable, 1, row, smFlow.bias, flowColor, color.gray, dashboardTransparency)
            row += 1
            cell(currentTable, 2, row, "Buy Volume", color.green, color.gray, dashboardTransparency)
            cell(currentTable, 3, row, str.tostring(math.round(smFlow.buyVolume)), color.white, color.gray, dashboardTransparency)            
            cell(currentTable, 0, row, "Sell Volume", color.red, color.gray, dashboardTransparency)
            cell(currentTable, 1, row, str.tostring(math.round(smFlow.sellVolume)), color.white, color.gray, dashboardTransparency)
            row += 1
        if dashboardSize == "Large"
            cell(currentTable, 0, row, "KEY GUIDE", color.white, #2A2E39, dashboardTransparency)
            table.merge_cells(currentTable, 0, row, 3, row)
            row += 1
            cell(currentTable, 0, row, "PATTERN TYPES", color.white, #2A2E39, dashboardTransparency)
            table.merge_cells(currentTable, 0, row, 3, row)
            row += 1
            cell(currentTable, 0, row, "━━━", type1BoxColor, color.gray, dashboardTransparency)
            cell(currentTable, 1, row, "Order Block (OB)", color.white, color.gray, dashboardTransparency)
            cell(currentTable, 2, row, "Institutional orders", color.black, color.gray, dashboardTransparency)
            cell(currentTable, 3, row, "High probability zone", color.white, color.gray, dashboardTransparency)
            row += 1
            cell(currentTable, 0, row, "━━━", type2BoxColor, color.gray, dashboardTransparency)
            cell(currentTable, 1, row, "Trap Zone", color.white, color.gray, dashboardTransparency)
            cell(currentTable, 2, row, "Liquidity grab area", color.black, color.gray, dashboardTransparency)
            cell(currentTable, 3, row, "Liquidity trap", color.white, color.gray, dashboardTransparency)
            row += 1
            cell(currentTable, 0, row, "━━━", type3BoxColor, color.gray, dashboardTransparency)
            cell(currentTable, 1, row, "Reversal/S&R", color.white, color.gray, dashboardTransparency)
            cell(currentTable, 2, row, "Key support/resistance", color.black, color.gray, dashboardTransparency)
            cell(currentTable, 3, row, "Reversal point", color.white, color.gray, dashboardTransparency)
            row += 1
            cell(currentTable, 0, row, "━━━", fvgBoxColor, color.gray, dashboardTransparency)
            cell(currentTable, 1, row, "FVG", color.white, color.gray, dashboardTransparency)
            cell(currentTable, 2, row, "Fair Value Gap", color.black, color.gray, dashboardTransparency)
            cell(currentTable, 3, row, "Gap opportunity", color.white, color.gray, dashboardTransparency)
            row += 1
            cell(currentTable, 0, row, "━━━", color.yellow, color.gray, dashboardTransparency)
            cell(currentTable, 1, row, "Pending", color.white, color.gray, dashboardTransparency)
            cell(currentTable, 2, row, "Unclassified zone", color.black, color.gray, dashboardTransparency)
            cell(currentTable, 3, row, "Await classification", color.white, color.gray, dashboardTransparency)
            row += 1
            cell(currentTable, 0, row, "STRUCTURE", color.white, #2A2E39, dashboardTransparency)
            table.merge_cells(currentTable, 0, row, 3, row)
            row += 1
            cell(currentTable, 0, row, "━━━", color.green, color.gray, dashboardTransparency)
            cell(currentTable, 1, row, "eBOS", color.white, color.gray, dashboardTransparency)
            cell(currentTable, 2, row, "External Break of Structure", color.black, color.gray, dashboardTransparency)
            cell(currentTable, 3, row, "Major break", color.white, color.gray, dashboardTransparency)
            row += 1
            cell(currentTable, 0, row, "━━━", color.orange, color.gray, dashboardTransparency)
            cell(currentTable, 1, row, "CHoCH", color.white, color.gray, dashboardTransparency)
            cell(currentTable, 2, row, "Change of Character", color.black, color.gray, dashboardTransparency)
            cell(currentTable, 3, row, "Trend change", color.white, color.gray, dashboardTransparency)
            row += 1
            cell(currentTable, 0, row, "SPECIAL LEVELS", color.white, #2A2E39, dashboardTransparency)
            table.merge_cells(currentTable, 0, row, 3, row)
            row += 1          
            cell(currentTable, 0, row, "━━━", originColor, color.gray, dashboardTransparency)
            cell(currentTable, 1, row, "Origin", color.white, color.gray, dashboardTransparency)
            cell(currentTable, 2, row, "Primary bias level", color.black, color.gray, dashboardTransparency)
            cell(currentTable, 3, row, "Bias origin", color.white, color.gray, dashboardTransparency)
            row += 1           
            cell(currentTable, 0, row, "━━━", mitigationColor, color.gray, dashboardTransparency)
            cell(currentTable, 1, row, "Mit", color.white, color.gray, dashboardTransparency)
            cell(currentTable, 2, row, "Mitigation level", color.black, color.gray, dashboardTransparency)
            cell(currentTable, 3, row, "Mitigation point", color.white, color.gray, dashboardTransparency)
            row += 1           
            cell(currentTable, 0, row, "━━━", color.blue, color.gray, dashboardTransparency)
            cell(currentTable, 1, row, "BSL", color.white, color.gray, dashboardTransparency)
            cell(currentTable, 2, row, "Buy-side liquidity", color.black, color.gray, dashboardTransparency)
            cell(currentTable, 3, row, "Buy liquidity", color.white, color.gray, dashboardTransparency)
            row += 1
            cell(currentTable, 0, row, "━━━", color.red, color.gray, dashboardTransparency)
            cell(currentTable, 1, row, "SSL", color.white, color.gray, dashboardTransparency)
            cell(currentTable, 2, row, "Sell-side liquidity", color.black, color.gray, dashboardTransparency)
            cell(currentTable, 3, row, "Sell liquidity", color.white, color.gray, dashboardTransparency)
            row += 1           
            cell(currentTable, 0, row, "GRADES", color.white, #2A2E39, dashboardTransparency)
            table.merge_cells(currentTable, 0, row, 3, row)
            row += 1
            cell(currentTable, 0, row, "[A+]", color.green, color.gray, dashboardTransparency)
            cell(currentTable, 1, row, "80%+", color.white, color.gray, dashboardTransparency)
            cell(currentTable, 2, row, "High probability", color.black, color.gray, dashboardTransparency)
            cell(currentTable, 3, row, "Top grade", color.white, color.gray, dashboardTransparency)
            row += 1
            cell(currentTable, 0, row, "[B]", color.yellow, color.gray, dashboardTransparency)
            cell(currentTable, 1, row, "60%+", color.white, color.gray, dashboardTransparency)
            cell(currentTable, 2, row, "Moderate quality", color.black, color.gray, dashboardTransparency)
            cell(currentTable, 3, row, "Medium grade", color.white, color.gray, dashboardTransparency)
            row += 1
            cell(currentTable, 0, row, "[C]", color.red, color.gray, dashboardTransparency)
            cell(currentTable, 1, row, "<60%", color.white, color.gray, dashboardTransparency)
            cell(currentTable, 2, row, "Low quality", color.black, color.gray, dashboardTransparency)
            cell(currentTable, 3, row, "Low grade", color.white, color.gray, dashboardTransparency)
            row += 1
        footerRowIndex = max_rows - 1
        cell(currentTable, 0, footerRowIndex, "💎 ⚡ Dskyz (DAFE) Trading Systems 💎", color.new(#FFD700, 0), color.new(#1A1A2E, 0), math.max(0, dashboardTransparency - 20))
        table.merge_cells(currentTable, 0, footerRowIndex, 3, footerRowIndex)
        result := currentTable
    result
drawNarrativeDashboard(t) =>
    table result = na
    if not showNarrativeDashboard
        if not na(t)
            table.delete(t)
    else
        if not na(t)
            table.delete(t)
        int max_rows = 20
        pos = narrativeDashboardPosition == "Top Left" ? position.top_left : narrativeDashboardPosition == "Top Right" ? position.top_right : narrativeDashboardPosition == "Bottom Left" ? position.bottom_left : position.bottom_right
        table currentTable = table.new(pos, 6, max_rows, border_width = 1, border_color = color.new(color.silver, 70), bgcolor = color.new(#1e222d, narrativeTransparency))
        dc_white = color.white
        dc_gray = color.silver
        dc_green = color.green
        dc_red = color.red
        dc_gold = color.yellow
        dc_orange = color.orange
        dc_aqua = color.aqua
        bg_header = color.new(color.black, 40)
        bg_section = color.new(color.gray, 80)
        bg_alt_row = color.new(color.gray, 90)
        header_size = size.normal
        value_size = size.small
        label_size = size.tiny
        current_row = 0
        table.merge_cells(currentTable, 0, current_row, 5, current_row)
        cell(currentTable, 0, current_row, "📖 Narrative Dashboard", dc_gold, bg_header, 0)
        current_row += 1
        table.merge_cells(currentTable, 0, current_row, 5, current_row)
        cell(currentTable, 0, current_row, "═══ 📊 RECENT ELEMENTS ═══", dc_gold, bg_section, 0)
        current_row += 1
        cell(currentTable, 0, current_row, "ID", dc_white, bg_header, 0)
        cell(currentTable, 1, current_row, "Type", dc_white, bg_header, 0)
        cell(currentTable, 2, current_row, "Role", dc_white, bg_header, 0)
        cell(currentTable, 3, current_row, "Quality", dc_white, bg_header, 0)
        cell(currentTable, 4, current_row, "Score", dc_white, bg_header, 0)
        cell(currentTable, 5, current_row, "Price", dc_white, bg_header, 0)
        current_row += 1
        displayCount = 0
        if array.size(elements) > 0
            for i = array.size(elements) - 1 to math.max(0, array.size(elements) - 10)
                if displayCount >= 5 or current_row >= max_rows - 2  // Prevent overflow
                    break
                e = safeGet(elements, i)
                if na(e) or e.qualityScore < minQualityThreshold
                    continue
                id = "#" + str.tostring(array.size(elements) - i)
                typ = switch e.elementType
                    "Type 1" => "T1"
                    "Type 2" => "T2"
                    "Type 3" => "T3"
                    => "Pnd"
                role = e.narrativeRole != "" ? e.narrativeRole : "Pending analysis"
                quality = str.tostring(math.round(e.qualityScore)) + "%"
                score = calculateTradeScore(e)
                scoreText = score.grade
                scoreColor = score.total >= 75 ? dc_green : score.total >= 55 ? dc_gold : dc_red
                emoji = score.total >= 75 ? "🌟" : score.total >= 55 ? "✅" : "⚠️"
                price = str.tostring((e.high + e.low)/2, "#.####")
                bg_row = current_row % 2 == 0 ? bg_alt_row : color.new(#000000, 100)
                cell(currentTable, 0, current_row, id, dc_white, bg_row, 0)
                cell(currentTable, 1, current_row, typ, dc_white, bg_row, 0)
                cell(currentTable, 2, current_row, role, dc_white, bg_row, 0)
                cell(currentTable, 3, current_row, quality, dc_aqua, bg_row, 0)
                cell(currentTable, 4, current_row, emoji + " " + scoreText, scoreColor, bg_row, 0)
                cell(currentTable, 5, current_row, price, dc_white, bg_row, 0)
                current_row += 1
                displayCount += 1
        if displayCount == 0 and current_row < max_rows
            table.merge_cells(currentTable, 0, current_row, 5, current_row)
            cell(currentTable, 0, current_row, "⚠️ No quality elements detected", dc_orange, color.new(color.gray, 0), 0)
            current_row += 1
        if current_row < max_rows
            table.merge_cells(currentTable, 0, current_row, 5, current_row)
            cell(currentTable, 0, current_row, "═══ 🔮 MARKET NARRATIVE ═══", dc_gold, bg_section, 0)
            current_row += 1
            narrativeText = getEnhancedMarketNarrative()
            lines = str.split(narrativeText, "\n")
            for i = 0 to math.min(array.size(lines) - 1, max_rows - current_row - 1)
                table.merge_cells(currentTable, 0, current_row, 5, current_row)
                lineColor = str.contains(array.get(lines, i), "High-Quality") ? dc_green : str.contains(array.get(lines, i), "Phase") ? dc_aqua : dc_white
                cell(currentTable, 0, current_row, array.get(lines, i), lineColor, color.new(#000000, 100), 0)
                current_row += 1
        result := currentTable
    result
// ========================================
// VALIDATION
// ========================================
isValidICTElement() =>
    if bar_index <= minDisplacementCandles or bar_index - lastDetectionBar < 5
        false
    else
        parentHigh = high[minDisplacementCandles]
        parentLow = low[minDisplacementCandles]
        allInside = true
        for i = 0 to minDisplacementCandles - 1
            if high[i] > parentHigh or low[i] < parentLow
                allInside := false
                break  
        fvgGap = math.abs(high[1] - low[minDisplacementCandles]) > atr14 * 0.3 or 
                 math.abs(low[1] - high[minDisplacementCandles]) > atr14 * 0.3   
        elementRange = parentHigh - parentLow
        rangeQuality = elementRange > avgRange20 * minElementSize and elementRange > atr14 * minElementSize
        volumeQuality = volume[minDisplacementCandles] > volumeSMA10 * 0.8
        recentElements = 0
        if array.size(elements) > 0
            for i = array.size(elements) - 1 to math.max(0, array.size(elements) - 5)
                e = safeGet(elements, i)
                if not na(e) and bar_index - e.endBar < 20
                    recentElements += 1  
        notTooMany = recentElements < 3
        htfValid = not htfAlignmentRequired or htfBias != "NEUTRAL"
        (allInside or fvgGap) and rangeQuality and volumeQuality and notTooMany and htfValid
// ========================================
 // MAIN DETECTION
// ========================================
detectAdvancedStructure()
if isValidICTElement() and barstate.isconfirmed
    newElement = ICTElement.new()
    newElement.high := high[minDisplacementCandles]
    newElement.low := low[minDisplacementCandles]
    newElement.startBar := bar_index - minDisplacementCandles
    newElement.endBar := bar_index
    newElement.mitigated := false
    newElement.timeframe := timeframe.period
    newElement.insideKillzone := inKillzone
    newElement.nearLiquidity := math.abs(newElement.high - bsl) < atr14 * 0.5 or math.abs(newElement.low - ssl) < atr14 * 0.5
    newElement.elementType := "Pending"
    newElement.narrativeRole := "Awaiting classification"
    newElement.qualityScore := assessQuality(newElement)
    if array.size(elements) < maxElementsToDisplay * 3
        array.push(elements, newElement)
        lastDetectionBar := bar_index
currentFVG = detectFVG()
if currentFVG.detected and array.size(fvgPatterns) < 20
    array.push(fvgPatterns, currentFVG)
// ========================================
// CLEANUP AND MITIGATION  
// ========================================
if barstate.isconfirmed
    if array.size(fvgPatterns) > 0
        for i = array.size(fvgPatterns) - 1 to 0
            fvg = safeGet(fvgPatterns, i)
            if not na(fvg) and bar_index - fvg.startBar > 50
                if not na(fvg.fvgBox)
                    box.delete(fvg.fvgBox)
                if not na(fvg.fvgLine)
                    line.delete(fvg.fvgLine)
                if not na(fvg.fvgLabel)
                    label.delete(fvg.fvgLabel)
                array.remove(fvgPatterns, i)
    toRemove = array.new<int>()
    if array.size(elements) > 0
        for i = 0 to math.min(array.size(elements) - 1, 50)
            e = safeGet(elements, i)
            if not na(e)
                age = bar_index - e.startBar
                if e.elementType == "Pending" and age >= 2 and age < pendingTimeout
                    causedBullishBOS = ms.bullishBOS and ms.lastBOSBar > e.endBar and ms.lastBOSBar - e.endBar <= 10
                    causedBearishBOS = ms.bearishBOS and ms.lastBOSBar > e.endBar and ms.lastBOSBar - e.endBar <= 10
                    if causedBullishBOS or causedBearishBOS
                        e.causedBOS := true
                        e.elementType := "Order Block"
                        e.narrativeRole := causedBullishBOS ? "Bullish OB (caused BOS)" : "Bearish OB (caused BOS)"
                        e.strength := 0.9
                    else if (bslSwept or sslSwept) and bar_index - e.endBar <= 5
                        e.elementType := "Trap Zone"
                        e.narrativeRole := "Liquidity Trap"
                        e.strength := 0.8
                    else if volume > volumeSMA20 * 1.5 and e.inLogicalArea
                        e.elementType := "Order Block"
                        e.narrativeRole := ms.orderFlow + " OB (high volume)"
                        e.strength := 0.7
                    else if age > 5
                        e.elementType := "S/R Zone"
                        e.narrativeRole := "Support/Resistance"
                        e.strength := 0.5
                if age > brokenAgeThreshold or (e.elementType == "Pending" and age > pendingTimeout)
                    if not na(e.identificationBox)
                        box.delete(e.identificationBox)
                    if not na(e.patternLine)
                        line.delete(e.patternLine)
                    if not na(e.patternLabel)
                        label.delete(e.patternLabel)
                    array.push(toRemove, i)  
    if array.size(toRemove) > 0
        for i = array.size(toRemove) - 1 to 0
            idx = array.get(toRemove, i)
            if idx < array.size(elements)
                array.remove(elements, idx)
    if array.size(elements) > 0
        for i = array.size(elements) - 1 to math.max(0, array.size(elements) - 20)
            e = safeGet(elements, i)
            if not na(e) and not e.mitigated
                mitigated = false
                breakDirection = ""
                if mitigationMethod == 'Cross'
                    if high > e.high
                        mitigated := true
                        breakDirection := "up"
                    else if low < e.low
                        mitigated := true
                        breakDirection := "down"
                else
                    if close > e.high
                        mitigated := true
                        breakDirection := "up"
                    else if close < e.low
                        mitigated := true
                        breakDirection := "down"
                if mitigated
                    e.mitigated := true
                    e.mitigationBar := bar_index
                    if e.elementType == "Pending"
                        if (breakDirection == "up" and ms.orderFlow == "BEARISH") or (breakDirection == "down" and ms.orderFlow == "BULLISH")
                            e.elementType := "Reversal Zone"
                            e.narrativeRole := "Counter-trend mitigation"
                        else
                            e.elementType := "S/R Zone"
                            e.narrativeRole := "Support/Resistance break"
                    if (breakDirection == "up" and ms.bullishBOS) or (breakDirection == "down" and ms.bearishBOS)
                        if not na(currentOrigin)
                            if currentOrigin.isOrigin
                                currentOrigin.isOrigin := false
                        e.isOrigin := true
                        currentOrigin := e
                    if array.size(mitigationLevels) >= 3
                        removed = array.shift(mitigationLevels)
                    mitLevel = ICTElement.new()
                    mitLevel.high := breakDirection == "up" ? e.high : e.low
                    mitLevel.low := mitLevel.high
                    mitLevel.startBar := bar_index
                    mitLevel.isMitigation := true
                    mitLevel.strength := e.strength
                    array.push(mitigationLevels, mitLevel)
// ========================================
 // DRAWING ENGINE
// ========================================
clearVisuals() =>
    while array.size(elementLines) > 0
        l = array.pop(elementLines)
        if not na(l)
            line.delete(l)
    while array.size(elementLabels) > 0
        lbl = array.pop(elementLabels)
        if not na(lbl)
            label.delete(lbl)
    while array.size(structureLines) > 0
        l = array.pop(structureLines)
        if not na(l)
            line.delete(l)
    while array.size(structureLabels) > 0
        lbl = array.pop(structureLabels)
        if not na(lbl)
            label.delete(lbl)
if barstate.isconfirmed
    clearVisuals()
    dashboard := drawDashboard(dashboard)
    narrativeDashboard := drawNarrativeDashboard(narrativeDashboard)
    if array.size(elements) > 0
        bestElement = ICTElement.new()
        bestScore = 0.0
        for i = array.size(elements) - 1 to math.max(0, array.size(elements) - 10)
            e = safeGet(elements, i)
            if not na(e) and not e.mitigated and e.elementType != "Pending"
                score = calculateTradeScore(e)
                if score.total > bestScore
                    bestScore := score.total
                    bestElement := e
        if bestScore >= 60
            narrative.keySetup := bestElement.elementType + " [" + calculateTradeScore(bestElement).grade + "]"
        else
            narrative.keySetup := ""
    if showSessions
        if not na(asianBox)
            box.delete(asianBox)
        if not na(londonBox)
            box.delete(londonBox)
        if not na(nyBox)
            box.delete(nyBox)
        if isAsianSession
            asianBox := box.new(bar_index, high * 1.02, bar_index + 1, low * 0.98, bgcolor=color.new(color.blue, 95), border_color=na)
        if isLondonSession
            londonBox := box.new(bar_index, high * 1.02, bar_index + 1, low * 0.98, bgcolor=color.new(color.yellow, 95), border_color=na)
        if isNYSession
            nyBox := box.new(bar_index, high * 1.02, bar_index + 1, low * 0.98, bgcolor=color.new(color.green, 95), border_color=na)
    if showKillzones
        if not na(londonKZBox)
            box.delete(londonKZBox)
        if not na(nyamKZBox)
            box.delete(nyamKZBox)
        if not na(nypmKZBox)
            box.delete(nypmKZBox)
        if isLondonKZ
            londonKZBox := box.new(bar_index, high * 1.02, bar_index + 1, low * 0.98, bgcolor=color.new(color.red, 90), border_color=color.red, border_width=1)
        if isNYAMKZ
            nyamKZBox := box.new(bar_index, high * 1.02, bar_index + 1, low * 0.98, bgcolor=color.new(color.red, 90), border_color=color.red, border_width=1)
        if isNYPMKZ
            nypmKZBox := box.new(bar_index, high * 1.02, bar_index + 1, low * 0.98, bgcolor=color.new(color.red, 90), border_color=color.red, border_width=1)
    if showPremiumDiscount
        if not na(premiumBox)
            box.delete(premiumBox)
        if not na(discountBox)
            box.delete(discountBox)
        if not na(equilibriumBox)
            box.delete(equilibriumBox)
        premiumBox := box.new(bar_index - 20, pdHigh, bar_index, equilibrium + (pdHigh - equilibrium) * 0.5, bgcolor=color.new(color.red, 85), border_color=na)
        discountBox := box.new(bar_index - 20, equilibrium - (equilibrium - pdLow) * 0.5, bar_index, pdLow, bgcolor=color.new(color.green, 85), border_color=na)
        equilibriumBox := box.new(bar_index - 20, equilibrium + atr14 * 0.1, bar_index, equilibrium - atr14 * 0.1, bgcolor=color.new(color.yellow, 80), border_color=color.yellow)
    if showLiquidity
        if not bslSwept
            bslLine = line.new(bar_index - liquidityLookback, bsl, bar_index + 5, bsl, color=color.blue, style=line.style_solid, width=2)
            array.push(elementLines, bslLine)
            bslLabel = label.new(bar_index + 5, bsl, "BSL", color=color.new(color.blue, 100), style=label.style_label_left, textcolor=color.blue, size=size.small)
            array.push(elementLabels, bslLabel)
        else if showSweptLiquidity
            bslLine = line.new(bar_index - 5, bsl, bar_index, bsl, color=color.new(color.blue, 50), style=line.style_dotted, width=1)
            array.push(elementLines, bslLine)
            bslLabel = label.new(bar_index, bsl, "BSL ✓", color=color.new(color.blue, 100), style=label.style_label_left, textcolor=color.new(color.blue, 50), size=size.small)
            array.push(elementLabels, bslLabel)
        if not sslSwept
            sslLine = line.new(bar_index - liquidityLookback, ssl, bar_index + 5, ssl, color=color.red, style=line.style_solid, width=2)
            array.push(elementLines, sslLine)
            sslLabel = label.new(bar_index + 5, ssl, "SSL", color=color.new(color.red, 100), style=label.style_label_left, textcolor=color.red, size=size.small)
            array.push(elementLabels, sslLabel)
        else if showSweptLiquidity
            sslLine = line.new(bar_index - 5, ssl, bar_index, ssl, color=color.new(color.red, 50), style=line.style_dotted, width=1)
            array.push(elementLines, sslLine)
            sslLabel = label.new(bar_index, ssl, "SSL ✓", color=color.new(color.red, 100), style=label.style_label_left, textcolor=color.new(color.red, 50), size=size.small)
            array.push(elementLabels, sslLabel)
    if showPatternLines
        if ms.externalBullishBOS and bar_index - ms.lastBOSBar < 50
            bosLine = line.new(ms.lastBOSBar, ms.lastBOSPrice, bar_index, ms.lastBOSPrice, color=color.green, style=line.style_solid, width=patternLineWidth)
            array.push(structureLines, bosLine)
            bosLabel = label.new(bar_index + labelPosition, ms.lastBOSPrice, "eBOS", color=color.new(color.green, 100), style=label.style_label_left, textcolor=color.green, size=size.small)
            array.push(structureLabels, bosLabel)
        if ms.externalBearishBOS and bar_index - ms.lastBOSBar < 50
            bosLine = line.new(ms.lastBOSBar, ms.lastBOSPrice, bar_index, ms.lastBOSPrice, color=color.red, style=line.style_solid, width=patternLineWidth)
            array.push(structureLines, bosLine)
            bosLabel = label.new(bar_index + labelPosition, ms.lastBOSPrice, "eBOS", color=color.new(color.red, 100), style=label.style_label_left, textcolor=color.red, size=size.small)
            array.push(structureLabels, bosLabel)
        if ms.choch and bar_index - ms.lastBOSBar < 50
            chochLine = line.new(ms.lastBOSBar, ms.lastBOSPrice, bar_index, ms.lastBOSPrice, color=color.orange, style=line.style_solid, width=patternLineWidth + 1)
            array.push(structureLines, chochLine)
            chochLabel = label.new(bar_index + labelPosition, ms.lastBOSPrice, "CHoCH", color=color.new(color.orange, 100), style=label.style_label_left, textcolor=color.orange, size=size.normal)
            array.push(structureLabels, chochLabel)
    if array.size(fvgPatterns) > 0
        for i = array.size(fvgPatterns) - 1 to 0
            fvg = safeGet(fvgPatterns, i)
            if not na(fvg)
                if na(fvg.fvgBox) and showIdentificationBoxes
                    boxColor = fvg.isBullish ? color.new(fvgBoxColor, boxTransparency) : color.new(fvgBoxColor, boxTransparency)
                    fvg.fvgBox := box.new(fvg.startBar, fvg.high, bar_index, fvg.low, bgcolor=boxColor, border_color=fvgBoxColor, border_width=1)
                if na(fvg.fvgLine) and showPatternLines
                    midPoint = (fvg.high + fvg.low) / 2
                    fvg.fvgLine := line.new(fvg.startBar, midPoint, bar_index, midPoint, color=fvgBoxColor, style=line.style_dashed, width=1)
                    fvg.fvgLabel := label.new(bar_index + labelPosition, midPoint, "FVG", color=color.new(fvgBoxColor, 100), style=label.style_label_left, textcolor=fvgBoxColor, size=size.small)
                else
                    if not na(fvg.fvgBox)
                        box.set_right(fvg.fvgBox, bar_index)
                    if not na(fvg.fvgLine)
                        line.set_x2(fvg.fvgLine, bar_index)
                        if not na(fvg.fvgLabel)
                            label.set_x(fvg.fvgLabel, bar_index + labelPosition)
    if showElementLines and array.size(elements) > 0
        elementCount = 0
        for i = array.size(elements) - 1 to 0
            if elementCount >= maxElementsToDisplay
                break
            e = safeGet(elements, i)
            if na(e) or e.qualityScore < minQualityThreshold
                continue
            age = bar_index - e.startBar
            if age > brokenAgeThreshold
                continue
            lineColor = color.gray
            boxColor = color.gray
            if e.elementType == "Order Block"
                lineColor := type1BoxColor
                boxColor := color.new(type1BoxColor, boxTransparency)
            else if e.elementType == "Trap Zone"
                lineColor := type2BoxColor
                boxColor := color.new(type2BoxColor, boxTransparency)
            else if e.elementType == "Reversal Zone" or e.elementType == "S/R Zone"
                lineColor := type3BoxColor
                boxColor := color.new(type3BoxColor, boxTransparency)
            else if e.elementType == "Pending"
                lineColor := color.yellow
                boxColor := color.new(color.yellow, boxTransparency + 10)
            lineWidth = e.qualityScore >= 75 ? 3 : e.qualityScore >= 50 ? 2 : 1
            startBar = math.max(e.startBar, bar_index - 500)
            if showIdentificationBoxes and na(e.identificationBox) and e.elementType != "Pending"
                e.identificationBox := box.new(startBar, e.high, e.endBar, e.low, bgcolor=boxColor, border_color=lineColor, border_width=1)
            if showPatternLines and na(e.patternLine)
                midPoint = (e.high + e.low) / 2
                e.patternLine := line.new(e.endBar, midPoint, bar_index, midPoint, color=lineColor, style=line.style_solid, width=patternLineWidth)
                typeLabel = e.elementType == "Order Block" ? "OB" : e.elementType == "Trap Zone" ? "TRAP" : e.elementType == "Reversal Zone" ? "REV" : e.elementType == "S/R Zone" ? "S/R" : "PEND"
                score = calculateTradeScore(e)
                if showTradeScore and e.elementType != "Pending"
                    typeLabel += " [" + score.grade + "]"
                e.patternLabel := label.new(bar_index + labelPosition, midPoint, typeLabel, color=color.new(lineColor, 80), style=label.style_label_left, textcolor=lineColor, size=size.small)
            else if not na(e.patternLine)
                line.set_x2(e.patternLine, bar_index)
                if not na(e.patternLabel)
                    label.set_x(e.patternLabel, bar_index + labelPosition)
            elementCount += 1
    if showOriginLine and not na(currentOrigin)
        if currentOrigin.isOrigin
            if bar_index - currentOrigin.mitigationBar < brokenAgeThreshold
                originLine = line.new(math.max(currentOrigin.mitigationBar, bar_index - 500), currentOrigin.high, bar_index + labelPosition, currentOrigin.high, color=originColor, style=line.style_solid, width=originLineWidth)
                array.push(elementLines, originLine)
                originLabel = label.new(bar_index + labelPosition, currentOrigin.high, "Origin", color=color.new(originColor, 100), style=label.style_label_left, textcolor=originColor, size=size.small)
                array.push(elementLabels, originLabel)
    if showMitigationLevels and array.size(mitigationLevels) > 0
        mitDrawnCount = 0
        for i = 0 to math.min(array.size(mitigationLevels) - 1, 2)
            if mitDrawnCount >= 2
                break
            mit = safeGet(mitigationLevels, i)
            if not na(mit) and bar_index - mit.startBar < brokenAgeThreshold
                mitLine = line.new(math.max(mit.startBar, bar_index - 500), mit.high, bar_index + labelPosition, mit.high, color=mitigationColor, style=line.style_solid, width=mitigationLineWidth)
                array.push(elementLines, mitLine)
                mitLabel = label.new(bar_index + labelPosition, mit.high, "Mit " + str.tostring(mitDrawnCount + 1), color=color.new(mitigationColor, 100), style=label.style_label_left, textcolor=mitigationColor, size=size.small)
                array.push(elementLabels, mitLabel)
                mitDrawnCount += 1
    if showIPDA
        if ipdaAsianRange
            ipdaBox = box.new(bar_index, high * 1.001, bar_index + 1, low * 0.999, bgcolor=color.new(color.blue, 92), border_color=color.blue, border_width=1)
        if ipdaLondonOpen
            ipdaBox = box.new(bar_index, high * 1.001, bar_index + 1, low * 0.999, bgcolor=color.new(color.orange, 92), border_color=color.orange, border_width=1)
        if ipdaNYOpen
            ipdaBox = box.new(bar_index, high * 1.001, bar_index + 1, low * 0.999, bgcolor=color.new(color.purple, 92), border_color=color.purple, border_width=1)
while array.size(elements) > maxElementsToDisplay * 3
    removed = array.shift(elements)
    if not na(removed.identificationBox)
        box.delete(removed.identificationBox)
    if not na(removed.patternLine)
        line.delete(removed.patternLine)
    if not na(removed.patternLabel)
        label.delete(removed.patternLabel)
// ========================================
 // ALERTS
// ========================================
if barstate.isconfirmed
    if array.size(elements) > 0
        for i = array.size(elements) - 1 to math.max(0, array.size(elements) - 5)
            e = safeGet(elements, i)
            if not na(e) and e.mitigated and e.mitigationBar == bar_index
                score = calculateTradeScore(e)
                if score.total >= 70
                    alertMessage = '🔥 HIGH QUALITY ICT SETUP!\n'
                    alertMessage += 'Type: ' + e.elementType + ' [' + score.grade + ']\n'
                    alertMessage += 'Price: ' + str.tostring(close, '#.####') + '\n'
                    alertMessage += 'Quality: ' + str.tostring(math.round(e.qualityScore)) + '%\n'
                    if e.causedBOS
                        alertMessage += '⚡ Caused BOS\n'
                    if e.insideKillzone
                        alertMessage += '🎯 In Killzone\n'
                    if e.nearLiquidity
                        alertMessage += '💧 Near Liquidity\n'
                    alert(alertMessage, alert.freq_once_per_bar)
                    break
    if ms.choch
        alert('⚠️ CHANGE OF CHARACTER!\n' + narrative.lastEvent, alert.freq_once_per_bar)
    if bslSwept or sslSwept
        sweepType = bslSwept ? 'Buy-side' : 'Sell-side'
        alert('💧 LIQUIDITY SWEEP!\n' + sweepType + ' liquidity swept.', alert.freq_once_per_bar)
[مدخلات المهمة — الصق كود Pine Script هنا بالكامل]
---BEGIN_PINE_SCRIPT---
(الصق كود المؤشر كاملاً هنا بدون حذف أو تعديل)
---END_PINE_SCRIPT---

ابدأ الآن:
- اكتب كود Python كامل واحد فقط.
- اجعل إعدادات المؤشر (Inputs) أعلى الكود بالقيم الافتراضية كما في Pine.
- اجعل إخراج الإشارات يتضمن GRADES حسب التصنيف أعلاه.
