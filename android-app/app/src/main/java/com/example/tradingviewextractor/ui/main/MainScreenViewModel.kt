package com.example.tradingviewextractor.ui.main

import android.content.ContentValues
import android.content.Context
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import java.util.TimeZone

data class LogEntry(
    val time: String,
    val message: String,
    val type: String
)

data class MarketRecord(
    val date: String,
    val close0928: Double,
    val callOption: Int,
    val putOption: Int,
    
    val ha1515Open: String,
    val ha1515High: String,
    val ha1515Low: String,
    val ha1515Close: String,
    
    val ha0915Open: String,
    val ha0915High: String,
    val ha0915Low: String,
    val ha0915Close: String,
    
    val ha0930Open: String,
    val ha0930High: String,
    val ha0930Low: String,
    val ha0930Close: String,
    
    val ha0945Open: String,
    val ha0945High: String,
    val ha0945Low: String,
    val ha0945Close: String
)

data class RawCandle(
    val epoch: Long,
    val date: String,
    val time: String,
    val open: Double,
    val high: Double,
    val low: Double,
    val close: Double
)

data class HaCandle(
    val date: String,
    val time: String,
    val closeStd: Double,
    val haOpen: Double,
    val haHigh: Double,
    val haLow: Double,
    val haClose: Double
)

data class UiState(
    val symbol: String = "NIFTY",
    val exchange: String = "NSE",
    val interval: String = "1 Minute",
    val range: String = "7 Days", // "1 Day", "5 Days", "7 Days", "30 Days", "60 Days", "1 Year"
    val strikeOffset: String = "100",
    val timeFilter: String = "0928", // "all" or "0928"
    val filename: String = "nifty_data.csv",
    val googleSheetUrl: String = "https://script.google.com/macros/s/AKfycbzeINdkKQbkx80cqa1n3e4r60aH9A6Ilmf0AQ93QMmLi9E6wNmt9qTakY85LpCqjZH5cw/exec",
    val logs: List<LogEntry> = listOf(LogEntry("", "HA OHLC Extractor: Ready to fetch and calculate levels.", "info")),
    val records: List<MarketRecord> = emptyList(),
    val isRunning: Boolean = false,
    val downloadStatus: String = "" // "Downloading...", "Success: Saved to Downloads/<file>", "Failed: <error>"
)

class MainScreenViewModel : ViewModel() {

    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun updateSymbol(value: String) { _uiState.value = _uiState.value.copy(symbol = value) }
    fun updateExchange(value: String) { _uiState.value = _uiState.value.copy(exchange = value) }
    fun updateInterval(value: String) { _uiState.value = _uiState.value.copy(interval = value) }
    fun updateRange(value: String) { _uiState.value = _uiState.value.copy(range = value) }
    fun updateStrikeOffset(value: String) { _uiState.value = _uiState.value.copy(strikeOffset = value) }
    fun updateTimeFilter(value: String) { _uiState.value = _uiState.value.copy(timeFilter = value) }
    fun updateFilename(value: String) { _uiState.value = _uiState.value.copy(filename = value) }
    fun updateGoogleSheetUrl(value: String) { _uiState.value = _uiState.value.copy(googleSheetUrl = value) }

    fun clearLogs() {
        _uiState.value = _uiState.value.copy(logs = emptyList())
    }

    private fun addLog(message: String, type: String = "info") {
        val timeStr = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())
        val newLogs = _uiState.value.logs + LogEntry(timeStr, message, type)
        _uiState.value = _uiState.value.copy(logs = newLogs)
    }

    fun startExtraction(context: Context) {
        val state = _uiState.value
        if (state.isRunning) return

        _uiState.value = state.copy(
            isRunning = true,
            downloadStatus = "",
            records = emptyList(),
            logs = listOf(LogEntry("", "Initiating standalone data fetch for ${state.symbol}:${state.exchange}...", "info"))
        )

        viewModelScope.launch {
            try {
                // Enforce 1-Minute interval as HA Extractor requires specific timestamps
                val actualInterval = "1 Minute"
                // Enforce at least 7 days to cover multiple daily boundaries
                val actualRange = when (state.range) {
                    "1 Day", "5 Days" -> "7 Days"
                    else -> state.range
                }
                
                val yahooRange = when (actualRange) {
                    "7 Days" -> "7d"
                    "30 Days" -> "30d"
                    "60 Days" -> "60d"
                    "1 Year" -> "1y"
                    else -> "7d"
                }

                addLog("HA Extractor active -> Enforcing 1-Minute interval and range '$actualRange' for calculation...", "info")
                addLog("Fetching market data from Yahoo Finance API...", "info")
                val rawJson = fetchYahooFinanceData(state.symbol, state.exchange, actualInterval, yahooRange)
                
                addLog("Calculating Heikin Ashi values and aligning daily timestamps...", "info")
                val csvData = parseAndProcessData(rawJson, state)
                
                addLog("Saving dataset to local device storage...", "info")
                saveCsvToDevice(csvData, state.filename, context)

                // Sync to Google Sheet if configured
                val currentState = _uiState.value
                if (currentState.googleSheetUrl.trim().isNotEmpty()) {
                    syncToGoogleSheets(currentState.records, currentState.googleSheetUrl)
                }

            } catch (e: Exception) {
                addLog("Error: ${e.message}", "error")
                _uiState.value = _uiState.value.copy(downloadStatus = "Failed: ${e.message}")
            } finally {
                _uiState.value = _uiState.value.copy(isRunning = false)
            }
        }
    }

    private suspend fun fetchYahooFinanceData(
        symbol: String,
        exchange: String,
        interval: String,
        range: String
    ): String = withContext(Dispatchers.IO) {
        val ticker = when (symbol.uppercase(Locale.US)) {
            "NIFTY", "NIFTY50", "NIFTY 50" -> "^NSEI"
            "BANKNIFTY", "NIFTYBANK" -> "^NSEBANK"
            "FINNIFTY" -> "NIFTY_FIN_SERVICE.NS"
            else -> {
                if (exchange.uppercase(Locale.US) == "BSE") "$symbol.BO" else "$symbol.NS"
            }
        }

        val yahooInterval = "1m" // Force 1-minute
        val urlStr = "https://query1.finance.yahoo.com/v8/finance/chart/$ticker?interval=$yahooInterval&range=$range"
        val url = URL(urlStr)
        val conn = url.openConnection() as HttpURLConnection
        conn.requestMethod = "GET"
        conn.connectTimeout = 12000
        conn.readTimeout = 15000
        conn.setRequestProperty("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        val responseCode = conn.responseCode
        if (responseCode == HttpURLConnection.HTTP_OK) {
            return@withContext conn.inputStream.bufferedReader().use { it.readText() }
        } else {
            val errorStreamText = conn.errorStream?.bufferedReader()?.use { it.readText() } ?: ""
            val detailedMsg = try {
                JSONObject(errorStreamText).getJSONObject("chart").getString("error")
            } catch (e: Exception) {
                "HTTP $responseCode"
            }
            throw Exception("Yahoo Finance API returned error: $detailedMsg")
        }
    }

    private fun parseAndProcessData(rawJson: String, state: UiState): String {
        val root = JSONObject(rawJson)
        val chart = root.getJSONObject("chart")
        val resultList = chart.getJSONArray("result")
        if (resultList.length() == 0) {
            throw Exception("No data returned for ticker.")
        }
        
        val result = resultList.getJSONObject(0)
        if (!result.has("timestamp")) {
            throw Exception("No historical records found for this timeframe/symbol.")
        }
        
        val timestamps = result.getJSONArray("timestamp")
        val indicators = result.getJSONObject("indicators")
        val quote = indicators.getJSONArray("quote").getJSONObject(0)
        
        val opens = quote.getJSONArray("open")
        val highs = quote.getJSONArray("high")
        val lows = quote.getJSONArray("low")
        val closes = quote.getJSONArray("close")

        val offset = state.strikeOffset.toIntOrNull() ?: 100
        
        val sdfDate = SimpleDateFormat("yyyy-MM-dd", Locale.US).apply {
            timeZone = TimeZone.getTimeZone("Asia/Kolkata")
        }
        val sdfTime = SimpleDateFormat("HH:mm", Locale.US).apply {
            timeZone = TimeZone.getTimeZone("Asia/Kolkata")
        }

        // 1. Parse standard candles sequentially
        val rawCandles = mutableListOf<RawCandle>()
        for (i in 0 until timestamps.length()) {
            if (closes.isNull(i) || opens.isNull(i) || highs.isNull(i) || lows.isNull(i)) {
                continue
            }
            val epoch = timestamps.getLong(i)
            val dateObj = Date(epoch * 1000)
            rawCandles.add(RawCandle(
                epoch = epoch,
                date = sdfDate.format(dateObj),
                time = sdfTime.format(dateObj),
                open = opens.getDouble(i),
                high = highs.getDouble(i),
                low = lows.getDouble(i),
                close = closes.getDouble(i)
            ))
        }

        // Sort chronologically by epoch
        rawCandles.sortBy { it.epoch }

        if (rawCandles.isEmpty()) {
            throw Exception("No valid standard candle records parsed.")
        }

        // 2. Calculate Heikin Ashi values sequentially
        val haCandles = mutableListOf<HaCandle>()
        var prevHaOpen = (rawCandles[0].open + rawCandles[0].close) / 2.0
        for (candle in rawCandles) {
            val haClose = (candle.open + candle.high + candle.low + candle.close) / 4.0
            val haOpen = prevHaOpen
            val haHigh = Math.max(candle.high, Math.max(haOpen, haClose))
            val haLow = Math.min(candle.low, Math.min(haOpen, haClose))

            haCandles.add(HaCandle(
                date = candle.date,
                time = candle.time,
                closeStd = candle.close,
                haOpen = haOpen,
                haHigh = haHigh,
                haLow = haLow,
                haClose = haClose
            ))

            // Update for next iteration
            prevHaOpen = (haOpen + haClose) / 2.0
        }

        // 3. Group chronologically by date
        val uniqueDates = haCandles.map { it.date }.distinct().sorted()
        
        val csvBuilder = StringBuilder()
        csvBuilder.append("Date,09:28 Close,Call Option,Put Option,15:15 HA Open,15:15 HA High,15:15 HA Low,15:15 HA Close,09:15 HA Open,09:15 HA High,09:15 HA Low,09:15 HA Close,09:30 HA Open,09:30 HA High,09:30 HA Low,09:30 HA Close,09:45 HA Open,09:45 HA High,09:45 HA Low,09:45 HA Close\n")

        val parsedRecords = mutableListOf<MarketRecord>()
        var recordCount = 0

        for (idx in uniqueDates.indices) {
            val currentDate = uniqueDates[idx]
            val prevDate = if (idx > 0) uniqueDates[idx - 1] else null

            // Find 09:28 standard close bar
            val bar0928 = haCandles.find { it.date == currentDate && it.time == "09:28" }
            if (bar0928 == null) {
                continue
            }

            val close0928 = bar0928.closeStd
            val callOption = ((close0928 - offset) / offset).toInt() * offset
            val putOption = Math.ceil((close0928 + offset) / offset).toInt() * offset

            // Key Heikin Ashi timestamps
            val bar0915 = haCandles.find { it.date == currentDate && it.time == "09:15" }
            val bar0930 = haCandles.find { it.date == currentDate && it.time == "09:30" }
            val bar0945 = haCandles.find { it.date == currentDate && it.time == "09:45" }

            // Previous trading day's 15:15
            val bar1515 = if (prevDate != null) haCandles.find { it.date == prevDate && it.time == "15:15" } else null

            fun formatHa(bar: HaCandle?): List<String> {
                if (bar != null) {
                    return listOf(
                        String.format(Locale.US, "%.2f", bar.haOpen),
                        String.format(Locale.US, "%.2f", bar.haHigh),
                        String.format(Locale.US, "%.2f", bar.haLow),
                        String.format(Locale.US, "%.2f", bar.haClose)
                    )
                }
                return listOf("", "", "", "")
            }

            val ha1515 = formatHa(bar1515)
            val ha0915 = formatHa(bar0915)
            val ha0930 = formatHa(bar0930)
            val ha0945 = formatHa(bar0945)

            csvBuilder.append(
                "$currentDate,${String.format(Locale.US, "%.2f", close0928)},$callOption,$putOption," +
                "${ha1515.joinToString(",")},${ha0915.joinToString(",")}," +
                "${ha0930.joinToString(",")},${ha0945.joinToString(",")}\n"
            )

            parsedRecords.add(MarketRecord(
                date = currentDate,
                close0928 = close0928,
                callOption = callOption,
                putOption = putOption,
                
                ha1515Open = ha1515[0],
                ha1515High = ha1515[1],
                ha1515Low = ha1515[2],
                ha1515Close = ha1515[3],
                
                ha0915Open = ha0915[0],
                ha0915High = ha0915[1],
                ha0915Low = ha0915[2],
                ha0915Close = ha0915[3],
                
                ha0930Open = ha0930[0],
                ha0930High = ha0930[1],
                ha0930Low = ha0930[2],
                ha0930Close = ha0930[3],
                
                ha0945Open = ha0945[0],
                ha0945High = ha0945[1],
                ha0945Low = ha0945[2],
                ha0945Close = ha0945[3]
            ))

            recordCount++
        }

        if (recordCount == 0) {
            throw Exception("No daily trading sessions with a 09:28 bar were found. Try fetching more days of historical data.")
        }

        // Update records in state
        _uiState.value = _uiState.value.copy(records = parsedRecords)

        addLog("Processed $recordCount trading days with Heikin Ashi OHLC levels.", "success")
        return csvBuilder.toString()
    }

    private suspend fun saveCsvToDevice(csvData: String, filename: String, context: Context) = withContext(Dispatchers.IO) {
        val cleanFilename = if (filename.endsWith(".csv")) filename else "${filename.removeSuffix(".xlsx")}.csv"
        try {
            val resolver = context.contentResolver
            val contentValues = ContentValues().apply {
                put(MediaStore.MediaColumns.DISPLAY_NAME, cleanFilename)
                put(MediaStore.MediaColumns.MIME_TYPE, "text/csv")
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS)
                }
            }
            
            val downloadsUri = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                MediaStore.Downloads.EXTERNAL_CONTENT_URI
            } else {
                MediaStore.Files.getContentUri("external")
            }
            
            val fileUri = resolver.insert(downloadsUri, contentValues)
            if (fileUri != null) {
                resolver.openOutputStream(fileUri).use { output ->
                    if (output != null) {
                        OutputStreamWriter(output).use { it.write(csvData) }
                    } else {
                        throw Exception("Failed to open output stream")
                    }
                }
                withContext(Dispatchers.Main) {
                    addLog("Dataset successfully saved to: Downloads/$cleanFilename", "success")
                    _uiState.value = _uiState.value.copy(
                        downloadStatus = "Success: Saved to Downloads/$cleanFilename"
                    )
                }
            } else {
                throw Exception("Failed to insert MediaStore record")
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                addLog("File write error: ${e.message}", "error")
                _uiState.value = _uiState.value.copy(
                    downloadStatus = "Failed: ${e.message}"
                )
            }
        }
    }

    private suspend fun syncToGoogleSheets(records: List<MarketRecord>, urlStr: String) = withContext(Dispatchers.IO) {
        if (urlStr.trim().isEmpty() || records.isEmpty()) return@withContext
        try {
            withContext(Dispatchers.Main) {
                addLog("Syncing dataset directly to Google Sheet...", "info")
            }
            val url = URL(urlStr.trim())
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.connectTimeout = 15000
            conn.readTimeout = 20000
            conn.doOutput = true
            conn.setRequestProperty("Content-Type", "application/json")
            conn.setRequestProperty("User-Agent", "Mozilla/5.0")

            val jsonArray = org.json.JSONArray()
            for (record in records) {
                val jsonRow = JSONObject().apply {
                    put("Date", record.date)
                    put("09:28 Close", record.close0928)
                    put("Call Option", record.callOption)
                    put("Put Option", record.putOption)
                    
                    put("15:15 HA Open", record.ha1515Open)
                    put("15:15 HA High", record.ha1515High)
                    put("15:15 HA Low", record.ha1515Low)
                    put("15:15 HA Close", record.ha1515Close)
                    
                    put("09:15 HA Open", record.ha0915Open)
                    put("09:15 HA High", record.ha0915High)
                    put("09:15 HA Low", record.ha0915Low)
                    put("09:15 HA Close", record.ha0915Close)
                    
                    put("09:30 HA Open", record.ha0930Open)
                    put("09:30 HA High", record.ha0930High)
                    put("09:30 HA Low", record.ha0930Low)
                    put("09:30 HA Close", record.ha0930Close)
                    
                    put("09:45 HA Open", record.ha0945Open)
                    put("09:45 HA High", record.ha0945High)
                    put("09:45 HA Low", record.ha0945Low)
                    put("09:45 HA Close", record.ha0945Close)
                }
                jsonArray.put(jsonRow)
            }

            OutputStreamWriter(conn.outputStream).use { it.write(jsonArray.toString()) }

            val responseCode = conn.responseCode
            if (responseCode == HttpURLConnection.HTTP_OK) {
                val responseText = conn.inputStream.bufferedReader().use { it.readText() }
                val responseJson = JSONObject(responseText)
                if (responseJson.getString("status") == "success") {
                    val rowsAdded = responseJson.getInt("rows_added")
                    withContext(Dispatchers.Main) {
                        addLog("Google Sheet live sync successful! Added $rowsAdded rows.", "success")
                        _uiState.value = _uiState.value.copy(
                            downloadStatus = _uiState.value.downloadStatus + " & Synced to Google Sheet"
                        )
                    }
                } else {
                    val errorMsg = responseJson.getString("error")
                    throw Exception(errorMsg)
                }
            } else {
                throw Exception("HTTP $responseCode from Google Apps Script Web App")
            }
        } catch (e: Exception) {
            withContext(Dispatchers.Main) {
                addLog("Google Sheets sync failed: ${e.message}", "error")
            }
        }
    }

    // --- EXACT ORIGINAL TRADINGVIEW STRATEGY ENGINE ---
    data class StrategyResult(
        val baseline: Double,
        val setupCandleLow: Double?,
        val entryTime: String?,
        val entryPrice: Double?,
        val targetPrice: Double?,
        val exitReason: String, // "TARGET HIT", "SL HIT", "NO SETUP", "NO ENTRY", "FALLBACK ENTRY"
        val exitTime: String?,
        val exitPrice: Double?,
        val pnlPoints: Double
    )

    fun evaluateOriginalTvStrategy(
        candles: List<RawCandle>,
        baseline: Double,
        targetPoints: Double = 25.0,
        slType: String = "close"
    ): StrategyResult {
        // Filter out early 09:15 and 09:20 candles (scan starts 09:25 AM onwards)
        val scanCandles = candles.filter { it.time !in listOf("09:15", "09:20") }
        if (scanCandles.isEmpty()) {
            return StrategyResult(baseline, null, null, null, null, "NO DATA", null, null, 0.0)
        }

        // 1. Setup Candle Scanner: Monitor for a candle completely below baseline (High < Baseline)
        var setupCandleIdx: Int? = null
        var lockedSl: Double? = null
        for (i in scanCandles.indices) {
            if (scanCandles[i].high < baseline) {
                setupCandleIdx = i
                lockedSl = scanCandles[i].low
                break
            }
        }

        // 2. Entry Breach Scanner: Scan for 2nd breach of baseline
        var firstBreachIdx: Int? = null
        var entryIdx: Int? = null
        var entryPrice: Double? = null
        var entryTime: String? = null
        var entryType = "auto"

        for (i in scanCandles.indices) {
            val highVal = maxOf(scanCandles[i].open, scanCandles[i].high, scanCandles[i].low, scanCandles[i].close)
            if (highVal > baseline) {
                if (firstBreachIdx == null) {
                    firstBreachIdx = i
                } else if (entryIdx == null) {
                    entryIdx = i
                    entryPrice = scanCandles[i].open
                    entryTime = scanCandles[i].time
                    break
                }
            }
        }

        // Fallback: only first breach, no 2nd confirmation candle
        if (firstBreachIdx != null && entryIdx == null) {
            val c = scanCandles[firstBreachIdx]
            entryIdx = firstBreachIdx
            entryPrice = maxOf(c.open, c.high, c.low, c.close)
            entryTime = c.time
            entryType = "fallback"
        }

        if (entryIdx == null || entryPrice == null) {
            return StrategyResult(
                baseline = baseline,
                setupCandleLow = lockedSl,
                entryTime = null,
                entryPrice = null,
                targetPrice = null,
                exitReason = "NO ENTRY",
                exitTime = null,
                exitPrice = null,
                pnlPoints = 0.0
            )
        }

        // 3. Target Price Calculation: Target = Entry Candle High + Target Points (+25 Pts)
        val entryCandleHigh = scanCandles[entryIdx].high
        val targetPrice = entryCandleHigh + targetPoints

        var targetHitIdx: Int? = null
        var targetHitTime: String? = null
        var slHitIdx: Int? = null
        var slHitTime: String? = null
        var slExitPrice: Double? = null

        // Scan for Target Hit
        for (i in entryIdx until scanCandles.size) {
            if (scanCandles[i].high >= targetPrice) {
                targetHitIdx = i
                targetHitTime = scanCandles[i].time
                break
            }
        }

        // Scan for SL Hit (active ONLY if setup candle was identified)
        if (setupCandleIdx != null && lockedSl != null) {
            val startIdx = maxOf(entryIdx, setupCandleIdx + 1)
            for (i in startIdx until scanCandles.size) {
                val c = scanCandles[i]
                val triggerVal = if (slType == "low") c.low else c.close
                if (triggerVal < lockedSl) {
                    slHitIdx = i
                    slHitTime = c.time
                    slExitPrice = minOf(c.open, c.high, c.low, c.close)
                    break
                }
            }
        }

        // Resolve Target vs SL Resolution
        return when {
            targetHitIdx != null && (slHitIdx == null || targetHitIdx <= slHitIdx) -> {
                StrategyResult(
                    baseline = baseline,
                    setupCandleLow = lockedSl,
                    entryTime = entryTime,
                    entryPrice = entryPrice,
                    targetPrice = targetPrice,
                    exitReason = "TARGET HIT",
                    exitTime = targetHitTime,
                    exitPrice = targetPrice,
                    pnlPoints = targetPoints
                )
            }
            slHitIdx != null -> {
                val exitPx = slExitPrice ?: (lockedSl ?: baseline)
                val pnl = exitPx - entryPrice
                StrategyResult(
                    baseline = baseline,
                    setupCandleLow = lockedSl,
                    entryTime = entryTime,
                    entryPrice = entryPrice,
                    targetPrice = targetPrice,
                    exitReason = "SL HIT",
                    exitTime = slHitTime,
                    exitPrice = exitPx,
                    pnlPoints = pnl
                )
            }
            else -> {
                StrategyResult(
                    baseline = baseline,
                    setupCandleLow = lockedSl,
                    entryTime = entryTime,
                    entryPrice = entryPrice,
                    targetPrice = targetPrice,
                    exitReason = "IN TRADE / OPEN",
                    exitTime = null,
                    exitPrice = null,
                    pnlPoints = 0.0
                )
            }
        }
    }

}
