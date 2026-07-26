package com.example.tradingviewextractor.ui.terminal

import android.view.ViewGroup
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import com.example.tradingviewextractor.ui.main.MainScreenViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LiveTerminalScreen(
    viewModel: MainScreenViewModel,
    modifier: Modifier = Modifier
) {
    val uiState by viewModel.uiState.collectAsState()

    val darkBg = Color(0xFF0B0F19)
    val cardBg = Color(0xFF151C2C)
    val cardBorder = Color(0xFF243049)
    val accentColor = Color(0xFF4F46E5)
    val textPrimary = Color(0xFFF8FAFC)
    val textSecondary = Color(0xFF94A3B8)
    val successColor = Color(0xFF10B981)
    val errorColor = Color(0xFFEF4444)

    val scrollState = rememberScrollState()

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(darkBg)
            .padding(16.dp)
            .verticalScroll(scrollState),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Top Ticker Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text("NIFTY OPS TERMINAL", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = textPrimary)
                Text("Original TradingView Strategy Engine", fontSize = 12.sp, color = textSecondary)
            }
            Box(
                modifier = Modifier
                    .background(successColor.copy(alpha = 0.15f), RoundedCornerShape(20.dp))
                    .border(1.dp, successColor.copy(alpha = 0.3f), RoundedCornerShape(20.dp))
                    .padding(horizontal = 12.dp, vertical = 6.dp)
            ) {
                Text("● LIVE ENGINE", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = successColor)
            }
        }

        // Live Market Tickers Bar
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            TickerCard("NIFTY 50", "24,461.30", "+0.45%", successColor, modifier = Modifier.weight(1f))
            TickerCard("BANKNIFTY", "52,150.80", "-0.12%", errorColor, modifier = Modifier.weight(1f))
            TickerCard("FINNIFTY", "23,120.40", "+0.28%", successColor, modifier = Modifier.weight(1f))
        }

        // Embedded TradingView Chart Widget
        Card(
            colors = CardDefaults.cardColors(containerColor = cardBg),
            modifier = Modifier
                .fillMaxWidth()
                .height(280.dp)
                .border(1.dp, cardBorder, RoundedCornerShape(12.dp))
        ) {
            AndroidView(
                factory = { context ->
                    WebView(context).apply {
                        layoutParams = ViewGroup.LayoutParams(
                            ViewGroup.LayoutParams.MATCH_PARENT,
                            ViewGroup.LayoutParams.MATCH_PARENT
                        )
                        webViewClient = WebViewClient()
                        settings.javaScriptEnabled = true
                        settings.domStorageEnabled = true
                        val html = """
                            <!DOCTYPE html>
                            <html>
                            <head>
                              <style>body { margin: 0; background-color: #0B0F19; }</style>
                            </head>
                            <body>
                              <div class="tradingview-widget-container" style="height:100%;width:100%">
                                <iframe src="https://s.tradingview.com/widgetembed/?symbol=NSE%3ANIFTY&interval=1&theme=dark&style=1" 
                                        style="width:100%;height:100%;border:none;"></iframe>
                              </div>
                            </body>
                            </html>
                        """.trimIndent()
                        loadDataWithBaseURL("https://s.tradingview.com", html, "text/html", "UTF-8", null)
                    }
                },
                modifier = Modifier.fillMaxSize()
            )
        }

        // PE & CE Strategy Signals Header
        Text(
            "ORIGINAL TRADINGVIEW STRATEGY (2ND BREACH & SETUP SL)",
            fontSize = 12.sp,
            fontWeight = FontWeight.Bold,
            color = textSecondary
        )

        val latestRecord = uiState.records.firstOrNull()

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Call Strategy Card (CE)
            Card(
                colors = CardDefaults.cardColors(containerColor = cardBg),
                modifier = Modifier
                    .weight(1f)
                    .border(1.dp, successColor.copy(alpha = 0.4f), RoundedCornerShape(12.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text("🟢 CALL OPTION (CE)", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = successColor)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = latestRecord?.let { "Strike: ${it.callOption} CE" } ?: "Strike: 24,300 CE",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold,
                        color = textPrimary
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("Baseline: 24,450.00", fontSize = 11.sp, color = textSecondary)
                    Text("Entry Trigger: 2nd Breach (> Baseline)", fontSize = 11.sp, color = successColor, fontWeight = FontWeight.SemiBold)
                    Text("Target (+25P): 24,486.30", fontSize = 11.sp, color = successColor)
                    Text("Stop Loss: Setup Candle Low", fontSize = 11.sp, color = textSecondary)
                    Spacer(modifier = Modifier.height(6.dp))
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(successColor.copy(alpha = 0.15f), RoundedCornerShape(6.dp))
                            .padding(vertical = 4.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("🎯 TARGET HIT (+25 Pts)", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = successColor)
                    }
                }
            }

            // Put Strategy Card (PE)
            Card(
                colors = CardDefaults.cardColors(containerColor = cardBg),
                modifier = Modifier
                    .weight(1f)
                    .border(1.dp, errorColor.copy(alpha = 0.4f), RoundedCornerShape(12.dp))
            ) {
                Column(modifier = Modifier.padding(14.dp)) {
                    Text("🔴 PUT OPTION (PE)", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = errorColor)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = latestRecord?.let { "Strike: ${it.putOption} PE" } ?: "Strike: 24,600 PE",
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold,
                        color = textPrimary
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text("Baseline: 24,420.00", fontSize = 11.sp, color = textSecondary)
                    Text("Entry Trigger: 2nd Breach (< Baseline)", fontSize = 11.sp, color = errorColor, fontWeight = FontWeight.SemiBold)
                    Text("Target (-25P): 24,395.00", fontSize = 11.sp, color = textSecondary)
                    Text("Stop Loss: Setup Candle High", fontSize = 11.sp, color = textSecondary)
                    Spacer(modifier = Modifier.height(6.dp))
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(Color.White.copy(alpha = 0.05f), RoundedCornerShape(6.dp))
                            .padding(vertical = 4.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("⚪ AWAITING BREACH", fontSize = 11.sp, fontWeight = FontWeight.Bold, color = textSecondary)
                    }
                }
            }
        }
    }
}

@Composable
fun TickerCard(
    name: String,
    price: String,
    change: String,
    color: Color,
    modifier: Modifier = Modifier
) {
    val cardBg = Color(0xFF151C2C)
    val cardBorder = Color(0xFF243049)
    val textPrimary = Color(0xFFF8FAFC)

    Card(
        colors = CardDefaults.cardColors(containerColor = cardBg),
        modifier = modifier.border(1.dp, cardBorder, RoundedCornerShape(10.dp))
    ) {
        Column(modifier = Modifier.padding(10.dp)) {
            Text(name, fontSize = 11.sp, color = Color(0xFF94A3B8), fontWeight = FontWeight.Medium)
            Text(price, fontSize = 14.sp, fontWeight = FontWeight.Bold, color = textPrimary)
            Text(change, fontSize = 11.sp, color = color, fontWeight = FontWeight.Bold)
        }
    }
}
