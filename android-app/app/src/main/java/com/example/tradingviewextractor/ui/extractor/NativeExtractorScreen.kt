package com.example.tradingviewextractor.ui.extractor

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.tradingviewextractor.ui.main.MainScreenViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NativeExtractorScreen(
    viewModel: MainScreenViewModel,
    modifier: Modifier = Modifier
) {
    val uiState by viewModel.uiState.collectAsState()
    val context = LocalContext.current

    val darkBg = Color(0xFF0B0F19)
    val cardBg = Color(0xFF151C2C)
    val cardBorder = Color(0xFF243049)
    val accentColor = Color(0xFF4F46E5)
    val textPrimary = Color(0xFFF8FAFC)
    val textSecondary = Color(0xFF94A3B8)
    val successColor = Color(0xFF10B981)

    val scrollState = rememberScrollState()

    Column(
        modifier = modifier
            .fillMaxSize()
            .background(darkBg)
            .padding(16.dp)
            .verticalScroll(scrollState),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text("STANDALONE HA EXTRACTOR", fontSize = 18.sp, fontWeight = FontWeight.Bold, color = textPrimary)

        // Extractor Config Form
        Card(
            colors = CardDefaults.cardColors(containerColor = cardBg),
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, cardBorder, RoundedCornerShape(12.dp))
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    OutlinedTextField(
                        value = uiState.symbol,
                        onValueChange = { viewModel.updateSymbol(it) },
                        label = { Text("Symbol") },
                        modifier = Modifier.weight(1f)
                    )
                    OutlinedTextField(
                        value = uiState.exchange,
                        onValueChange = { viewModel.updateExchange(it) },
                        label = { Text("Exchange") },
                        modifier = Modifier.weight(1f)
                    )
                }

                Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                    OutlinedTextField(
                        value = uiState.strikeOffset,
                        onValueChange = { viewModel.updateStrikeOffset(it) },
                        label = { Text("Strike Offset") },
                        modifier = Modifier.weight(1f)
                    )
                    OutlinedTextField(
                        value = uiState.range,
                        onValueChange = { viewModel.updateRange(it) },
                        label = { Text("Time Range") },
                        modifier = Modifier.weight(1f)
                    )
                }

                Button(
                    onClick = { viewModel.startExtraction(context) },
                    enabled = !uiState.isRunning,
                    colors = ButtonDefaults.buttonColors(containerColor = accentColor),
                    modifier = Modifier.fillMaxWidth().height(48.dp)
                ) {
                    if (uiState.isRunning) {
                        CircularProgressIndicator(color = Color.White, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Calculating Heikin Ashi...")
                    } else {
                        Text("⚡ Start Live Engine & Sync Memory", fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        // Real-Time Outcome Table (Zero File Downloads)
        Text("STRATEGY OUTCOME PREVIEW (MEMORY SYNC)", fontSize = 13.sp, fontWeight = FontWeight.Bold, color = textSecondary)

        Card(
            colors = CardDefaults.cardColors(containerColor = cardBg),
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, cardBorder, RoundedCornerShape(12.dp))
        ) {
            val hScroll = rememberScrollState()
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(12.dp)
                    .horizontalScroll(hScroll)
            ) {
                // Table Header
                Row(
                    modifier = Modifier
                        .background(accentColor.copy(alpha = 0.2f), RoundedCornerShape(6.dp))
                        .padding(8.dp),
                    horizontalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    TableHeaderCell("Date", 100.dp)
                    TableHeaderCell("09:28 Close", 90.dp)
                    TableHeaderCell("Call Strike (CE)", 110.dp)
                    TableHeaderCell("Put Strike (PE)", 110.dp)
                    TableHeaderCell("Prev 15:15 HA", 120.dp)
                    TableHeaderCell("09:15 HA", 120.dp)
                }

                Spacer(modifier = Modifier.height(6.dp))

                if (uiState.records.isEmpty()) {
                    Text(
                        "No extraction data loaded. Tap 'Start Live Engine' above to view live memory sync.",
                        fontSize = 12.sp,
                        color = textSecondary,
                        modifier = Modifier.padding(16.dp)
                    )
                } else {
                    uiState.records.forEach { record ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 6.dp, horizontal = 8.dp),
                            horizontalArrangement = Arrangement.spacedBy(16.dp)
                        ) {
                            TableCell(record.date, 100.dp, textPrimary)
                            TableCell(String.format("%.2f", record.close0928), 90.dp, successColor)
                            TableCell("${record.callOption} CE", 110.dp, successColor)
                            TableCell("${record.putOption} PE", 110.dp, Color(0xFFEF4444))
                            TableCell(record.ha1515Close, 120.dp, textSecondary)
                            TableCell(record.ha0915Close, 120.dp, textSecondary)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun TableHeaderCell(text: String, width: androidx.compose.ui.unit.Dp) {
    Text(text, fontSize = 11.sp, fontWeight = FontWeight.Bold, color = Color(0xFFA5B4FC), modifier = Modifier.width(width))
}

@Composable
fun TableCell(text: String, width: androidx.compose.ui.unit.Dp, color: Color) {
    Text(text, fontSize = 12.sp, color = color, fontFamily = FontFamily.Monospace, modifier = Modifier.width(width))
}
