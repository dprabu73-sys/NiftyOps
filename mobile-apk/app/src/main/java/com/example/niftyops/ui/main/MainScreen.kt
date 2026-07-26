package com.example.niftyops.ui.main

import java.util.Locale
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation3.runtime.NavKey

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainScreen(
  onBack: () -> Unit,
  modifier: Modifier = Modifier,
  viewModel: MainScreenViewModel = viewModel { MainScreenViewModel() },
) {
  val state by viewModel.uiState.collectAsStateWithLifecycle()
  val context = LocalContext.current
  val scrollState = rememberScrollState()

  val darkBg = Color(0xFF0B0F19)
  val cardBg = Color(0xFF151C2C)
  val cardBorder = Color(0xFF243049)
  val accentColor = Color(0xFF4F46E5)
  val textPrimary = Color(0xFFF8FAFC)
  val textSecondary = Color(0xFF94A3B8)
  val successColor = Color(0xFF10B981)
  val errorColor = Color(0xFFEF4444)
  val warningColor = Color(0xFFF59E0B)

  Scaffold(
    topBar = {
      TopAppBar(
        title = {
          Column {
            Text(
              "TradingView Extractor Pro",
              fontSize = 18.sp,
              fontWeight = FontWeight.Bold,
              color = textPrimary
            )
            Text(
              "Standalone Mode",
              fontSize = 11.sp,
              color = textSecondary
            )
          }
        },
        navigationIcon = {
          IconButton(onClick = onBack) {
            Text("◀", color = textPrimary, fontSize = 14.sp)
          }
        },
        colors = TopAppBarDefaults.topAppBarColors(
          containerColor = cardBg,
          titleContentColor = textPrimary
        )
      )
    },
    containerColor = darkBg
  ) { paddingValues ->
    Column(
      modifier = modifier
        .padding(paddingValues)
        .fillMaxSize()
        .verticalScroll(scrollState),
      verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {

      // Symbol & Settings Card
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
          Text(
            "EXTRACTION CONFIGURATION",
            fontSize = 12.sp,
            fontWeight = FontWeight.SemiBold,
            color = textSecondary
          )
          
          Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            OutlinedTextField(
              value = state.symbol,
              onValueChange = { viewModel.updateSymbol(it) },
              label = { Text("Symbol") },
              modifier = Modifier.weight(1f),
              singleLine = true,
              colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = accentColor, unfocusedBorderColor = cardBorder)
            )
            OutlinedTextField(
              value = state.exchange,
              onValueChange = { viewModel.updateExchange(it) },
              label = { Text("Exchange") },
              modifier = Modifier.weight(1f),
              singleLine = true,
              colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = accentColor, unfocusedBorderColor = cardBorder)
            )
          }

          // Interval Dropdown Selector
          var isIntervalDropdownExpanded by remember { mutableStateOf(false) }
          val intervals = listOf(
            "1 Minute", "5 Minutes", "15 Minutes", "30 Minutes",
            "1 Hour", "Daily", "Weekly", "Monthly"
          )
          
          Column {
            Text("Interval", fontSize = 12.sp, color = textSecondary)
            Box(
              modifier = Modifier
                .fillMaxWidth()
                .padding(top = 4.dp)
                .background(darkBg, RoundedCornerShape(8.dp))
                .border(1.dp, cardBorder, RoundedCornerShape(8.dp))
                .clickable { isIntervalDropdownExpanded = true }
                .padding(16.dp)
            ) {
              Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
              ) {
                Text(state.interval, color = textPrimary)
                Text("▼", color = textSecondary, fontSize = 12.sp)
              }
              DropdownMenu(
                expanded = isIntervalDropdownExpanded,
                onDismissRequest = { isIntervalDropdownExpanded = false },
                modifier = Modifier.background(cardBg)
              ) {
                intervals.forEach { label ->
                  DropdownMenuItem(
                    text = { Text(label, color = textPrimary) },
                    onClick = {
                      viewModel.updateInterval(label)
                      isIntervalDropdownExpanded = false
                    }
                  )
                }
              }
            }
          }

          // Range Dropdown Selector
          var isRangeDropdownExpanded by remember { mutableStateOf(false) }
          val ranges = listOf("1 Day", "5 Days", "7 Days", "30 Days", "60 Days", "1 Year")
          
          Column {
            Text("Timeframe Range", fontSize = 12.sp, color = textSecondary)
            Box(
              modifier = Modifier
                .fillMaxWidth()
                .padding(top = 4.dp)
                .background(darkBg, RoundedCornerShape(8.dp))
                .border(1.dp, cardBorder, RoundedCornerShape(8.dp))
                .clickable { isRangeDropdownExpanded = true }
                .padding(16.dp)
            ) {
              Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
              ) {
                Text(state.range, color = textPrimary)
                Text("▼", color = textSecondary, fontSize = 12.sp)
              }
              DropdownMenu(
                expanded = isRangeDropdownExpanded,
                onDismissRequest = { isRangeDropdownExpanded = false },
                modifier = Modifier.background(cardBg)
              ) {
                ranges.forEach { label ->
                  DropdownMenuItem(
                    text = { Text(label, color = textPrimary) },
                    onClick = {
                      viewModel.updateRange(label)
                      isRangeDropdownExpanded = false
                    }
                  )
                }
              }
            }
          }

          Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
            OutlinedTextField(
              value = state.strikeOffset,
              onValueChange = { viewModel.updateStrikeOffset(it) },
              label = { Text("Strike Offset") },
              modifier = Modifier.weight(1f),
              singleLine = true,
              colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = accentColor, unfocusedBorderColor = cardBorder)
            )
          }

          // Time Filter Section
          Column {
            Text("Time Filter", fontSize = 12.sp, color = textSecondary)
            Row(
              modifier = Modifier.fillMaxWidth().padding(top = 4.dp),
              horizontalArrangement = Arrangement.spacedBy(24.dp)
            ) {
              Row(verticalAlignment = Alignment.CenterVertically) {
                RadioButton(
                  selected = state.timeFilter == "all",
                  onClick = { viewModel.updateTimeFilter("all") },
                  colors = RadioButtonDefaults.colors(selectedColor = accentColor)
                )
                Text("All", color = textPrimary, modifier = Modifier.clickable { viewModel.updateTimeFilter("all") })
              }
              Row(verticalAlignment = Alignment.CenterVertically) {
                RadioButton(
                  selected = state.timeFilter == "0928",
                  onClick = { viewModel.updateTimeFilter("0928") },
                  colors = RadioButtonDefaults.colors(selectedColor = accentColor)
                )
                Text("09:28 Only", color = textPrimary, modifier = Modifier.clickable { viewModel.updateTimeFilter("0928") })
              }
            }
          }

          OutlinedTextField(
            value = state.filename,
            onValueChange = { viewModel.updateFilename(it) },
            label = { Text("Output Filename") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = accentColor, unfocusedBorderColor = cardBorder)
          )

          OutlinedTextField(
            value = state.googleSheetUrl,
            onValueChange = { viewModel.updateGoogleSheetUrl(it) },
            label = { Text("Google Sheets Webhook URL (Optional)") },
            placeholder = { Text("https://script.google.com/macros/s/.../exec") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            colors = OutlinedTextFieldDefaults.colors(focusedBorderColor = accentColor, unfocusedBorderColor = cardBorder)
          )
        }
      }

      // Action Button
      Button(
        onClick = { viewModel.startExtraction(context) },
        enabled = !state.isRunning,
        colors = ButtonDefaults.buttonColors(containerColor = accentColor),
        shape = RoundedCornerShape(8.dp),
        modifier = Modifier
          .fillMaxWidth()
          .height(50.dp)
      ) {
        if (state.isRunning) {
          CircularProgressIndicator(color = Color.White, modifier = Modifier.size(24.dp))
          Spacer(Modifier.width(12.dp))
          Text("Fetching & Processing...", fontWeight = FontWeight.Bold, color = Color.White)
        } else {
          Text("Fetch & Save Excel/CSV", fontWeight = FontWeight.Bold, color = Color.White)
        }
      }

      // Download Status indicator
      if (state.downloadStatus.isNotEmpty()) {
        val statusColor = when {
          state.downloadStatus.startsWith("Success") -> successColor
          state.downloadStatus.startsWith("Failed") -> errorColor
          else -> textPrimary
        }
        Text(
          state.downloadStatus,
          color = statusColor,
          fontSize = 13.sp,
          fontWeight = FontWeight.Medium,
          textAlign = TextAlign.Center,
          modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp)
        )
      }

      // Extracted Data Preview Table Card
      if (state.records.isNotEmpty()) {
        Card(
          colors = CardDefaults.cardColors(containerColor = cardBg),
          modifier = Modifier
            .fillMaxWidth()
            .border(1.dp, cardBorder, RoundedCornerShape(12.dp))
        ) {
          Column(modifier = Modifier.padding(12.dp)) {
            Text(
              "EXTRACTED DATA PREVIEW",
              fontSize = 12.sp,
              fontWeight = FontWeight.SemiBold,
              color = textSecondary,
              modifier = Modifier.padding(bottom = 8.dp)
            )
            
            // Horizontal scroll container for the spreadsheet layout
            val horizontalScrollState = rememberScrollState()
            Box(
              modifier = Modifier
                .fillMaxWidth()
                .horizontalScroll(horizontalScrollState)
                .background(darkBg, RoundedCornerShape(8.dp))
                .border(1.dp, cardBorder, RoundedCornerShape(8.dp))
            ) {
              Column {
                // Table Headers Row
                Row(
                  modifier = Modifier
                    .background(Color(0xFF1E293B))
                    .padding(vertical = 10.dp, horizontal = 8.dp),
                  verticalAlignment = Alignment.CenterVertically
                ) {
                  TableHeaderCell("DATE", 100)
                  TableHeaderCell("09:28 CLOSE", 100)
                  TableHeaderCell("CALL", 80)
                  TableHeaderCell("PUT", 80)
                  
                  TableHeaderCell("15:15 O", 80)
                  TableHeaderCell("15:15 H", 80)
                  TableHeaderCell("15:15 L", 80)
                  TableHeaderCell("15:15 C", 80)
                  
                  TableHeaderCell("09:15 O", 80)
                  TableHeaderCell("09:15 H", 80)
                  TableHeaderCell("09:15 L", 80)
                  TableHeaderCell("09:15 C", 80)
                  
                  TableHeaderCell("09:30 O", 80)
                  TableHeaderCell("09:30 H", 80)
                  TableHeaderCell("09:30 L", 80)
                  TableHeaderCell("09:30 C", 80)
                  
                  TableHeaderCell("09:45 O", 80)
                  TableHeaderCell("09:45 H", 80)
                  TableHeaderCell("09:45 L", 80)
                  TableHeaderCell("09:45 C", 80)
                }
                
                Divider(color = cardBorder, thickness = 1.dp)

                // Table Data Rows
                state.records.forEachIndexed { index, record ->
                  val rowBg = if (index % 2 == 0) Color.Transparent else Color(0xFF0F172A)
                  Row(
                    modifier = Modifier
                      .background(rowBg)
                      .padding(vertical = 10.dp, horizontal = 8.dp),
                    verticalAlignment = Alignment.CenterVertically
                  ) {
                    TableCell(record.date, 100, textPrimary, FontFamily.Monospace)
                    TableCell(String.format(Locale.US, "%.2f", record.close0928), 100, successColor, FontFamily.Monospace)
                    TableCell(record.callOption.toString(), 80, textPrimary, FontWeight.Bold)
                    TableCell(record.putOption.toString(), 80, textPrimary, FontWeight.Bold)
                    
                    TableCell(record.ha1515Open, 80, textSecondary, FontFamily.Monospace)
                    TableCell(record.ha1515High, 80, textSecondary, FontFamily.Monospace)
                    TableCell(record.ha1515Low, 80, textSecondary, FontFamily.Monospace)
                    TableCell(record.ha1515Close, 80, textSecondary, FontFamily.Monospace)
                    
                    TableCell(record.ha0915Open, 80, textSecondary, FontFamily.Monospace)
                    TableCell(record.ha0915High, 80, textSecondary, FontFamily.Monospace)
                    TableCell(record.ha0915Low, 80, textSecondary, FontFamily.Monospace)
                    TableCell(record.ha0915Close, 80, textSecondary, FontFamily.Monospace)
                    
                    TableCell(record.ha0930Open, 80, textSecondary, FontFamily.Monospace)
                    TableCell(record.ha0930High, 80, textSecondary, FontFamily.Monospace)
                    TableCell(record.ha0930Low, 80, textSecondary, FontFamily.Monospace)
                    TableCell(record.ha0930Close, 80, textSecondary, FontFamily.Monospace)
                    
                    TableCell(record.ha0945Open, 80, textSecondary, FontFamily.Monospace)
                    TableCell(record.ha0945High, 80, textSecondary, FontFamily.Monospace)
                    TableCell(record.ha0945Low, 80, textSecondary, FontFamily.Monospace)
                    TableCell(record.ha0945Close, 80, textSecondary, FontFamily.Monospace)
                  }
                  if (index < state.records.size - 1) {
                    Divider(color = cardBorder.copy(alpha = 0.5f), thickness = 0.5.dp)
                  }
                }
              }
            }
          }
        }
      }

      // Console Card
      Card(
        colors = CardDefaults.cardColors(containerColor = Color(0xFF05070F)),
        modifier = Modifier
          .fillMaxWidth()
          .height(260.dp)
          .border(1.dp, cardBorder, RoundedCornerShape(12.dp))
      ) {
        Column(modifier = Modifier.padding(12.dp)) {
          Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
          ) {
            Text(
              "LIVE EXECUTION LOGS",
              fontSize = 11.sp,
              fontWeight = FontWeight.Bold,
              color = textSecondary
            )
            Text(
              "Clear",
              fontSize = 11.sp,
              color = textSecondary,
              modifier = Modifier
                .clickable { viewModel.clearLogs() }
                .padding(horizontal = 8.dp, vertical = 2.dp)
            )
          }
          
          Spacer(Modifier.height(8.dp))
          
          val logScrollState = rememberScrollState()
          Column(
            modifier = Modifier
              .fillMaxSize()
              .verticalScroll(logScrollState)
          ) {
            state.logs.forEach { log ->
              Row(
                modifier = Modifier.fillMaxWidth().padding(vertical = 2.dp),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
              ) {
                if (log.time.isNotEmpty()) {
                  Text(
                    "[${log.time}]",
                    fontFamily = FontFamily.Monospace,
                    fontSize = 11.sp,
                    color = Color(0xFF565F89)
                  )
                }
                val textColor = when (log.type) {
                  "success" -> successColor
                  "error" -> errorColor
                  "warn" -> warningColor
                  else -> textSecondary
                }
                Text(
                  log.message,
                  fontFamily = FontFamily.Monospace,
                  fontSize = 11.sp,
                  color = textColor,
                  modifier = Modifier.weight(1f)
                )
              }
            }
            
            // Auto scroll to bottom
            LaunchedEffect(state.logs.size) {
              logScrollState.animateScrollTo(logScrollState.maxValue)
            }
          }
        }
      }

      Spacer(Modifier.height(24.dp))
    }
  }
}

@Composable
fun TableHeaderCell(text: String, width: Int) {
  Text(
    text = text,
    fontSize = 10.sp,
    fontWeight = FontWeight.Bold,
    color = Color(0xFFE2E8F0),
    textAlign = TextAlign.Start,
    modifier = Modifier.width(width.dp).padding(horizontal = 4.dp)
  )
}

@Composable
fun TableCell(
  text: String,
  width: Int,
  color: Color,
  fontWeight: FontWeight = FontWeight.Normal
) {
  Text(
    text = text,
    fontSize = 11.sp,
    fontWeight = fontWeight,
    color = color,
    textAlign = TextAlign.Start,
    modifier = Modifier.width(width.dp).padding(horizontal = 4.dp)
  )
}

@Composable
fun TableCell(
  text: String,
  width: Int,
  color: Color,
  fontFamily: FontFamily
) {
  Text(
    text = text,
    fontSize = 11.sp,
    fontFamily = fontFamily,
    color = color,
    textAlign = TextAlign.Start,
    modifier = Modifier.width(width.dp).padding(horizontal = 4.dp)
  )
}
