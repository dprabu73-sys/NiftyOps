package com.example.niftyops.ui.launcher

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LauncherScreen(
    onLaunchTerminal: () -> Unit,
    onLaunchExtractor: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val sharedPrefs = remember { context.getSharedPreferences("niftyops_prefs", Context.MODE_PRIVATE) }
    
    var serverUrl by remember { 
        mutableStateOf(sharedPrefs.getString("server_url", "http://192.168.1.100:5001") ?: "http://192.168.1.100:5001") 
    }
    
    var showUrlDialog by remember { mutableStateOf(false) }
    var tempUrl by remember { mutableStateOf(serverUrl) }

    val darkBg = Color(0xFF080E1A)
    val cardBg = Color(0xFF0D1523)
    val cardBorder = Color(0xFF243049)
    val textPrimary = Color(0xFFF0F6FF)
    val textSecondary = Color(0xFF6B7FA3)
    val accentColor = Color(0xFF6366F1)
    val successColor = Color(0xFF10B981)

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(darkBg),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(24.dp),
            modifier = Modifier.padding(24.dp)
        ) {
            // App Logo Section
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .background(
                        Brush.linearGradient(listOf(accentColor, Color(0xFF818CF8))),
                        RoundedCornerShape(20.dp)
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text("⚡", fontSize = 40.sp, color = Color.White)
            }

            Column(horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.spacedBy(4.dp)) {
                Text(
                    "NIFTY OPS",
                    fontSize = 28.sp,
                    fontWeight = FontWeight.ExtraBold,
                    color = textPrimary,
                    letterSpacing = 1.sp
                )
                Text(
                    "Auto-Pilot Trade Terminal",
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Medium,
                    color = textSecondary
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Main Actions
            Column(
                verticalArrangement = Arrangement.spacedBy(16.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                // Button 1: Live Trading Terminal (WebView)
                Card(
                    onClick = onLaunchTerminal,
                    colors = CardDefaults.cardColors(containerColor = cardBg),
                    modifier = Modifier
                        .fillMaxWidth()
                        .border(1.dp, cardBorder, RoundedCornerShape(14.dp))
                ) {
                    Row(
                        modifier = Modifier.padding(20.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(44.dp)
                                .background(accentColor.copy(alpha = 0.15f), RoundedCornerShape(10.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            Text("📊", fontSize = 20.sp)
                        }
                        Column(modifier = Modifier.weight(1f)) {
                            Text("Live Trade Terminal", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = textPrimary)
                            Text("Complete Strategy Analyzer, Journal, Settings & Auto-Pilot logics", fontSize = 11.sp, color = textSecondary)
                        }
                    }
                }

                // Button 2: Standalone HA Extractor (Offline Native)
                Card(
                    onClick = onLaunchExtractor,
                    colors = CardDefaults.cardColors(containerColor = cardBg),
                    modifier = Modifier
                        .fillMaxWidth()
                        .border(1.dp, cardBorder, RoundedCornerShape(14.dp))
                ) {
                    Row(
                        modifier = Modifier.padding(20.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Box(
                            modifier = Modifier
                                .size(44.dp)
                                .background(successColor.copy(alpha = 0.15f), RoundedCornerShape(10.dp)),
                            contentAlignment = Alignment.Center
                        ) {
                            Text("📥", fontSize = 20.sp)
                        }
                        Column(modifier = Modifier.weight(1f)) {
                            Text("Standalone HA Extractor", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = textPrimary)
                            Text("Local Yahoo Finance data fetcher & Heikin Ashi levels logger (Offline)", fontSize = 11.sp, color = textSecondary)
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Configuration Info Footer
            Column(
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(6.dp),
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { 
                        tempUrl = serverUrl
                        showUrlDialog = true 
                    }
                    .padding(8.dp)
            ) {
                Text("Flask Server URL", fontSize = 10.sp, fontWeight = FontWeight.Bold, color = Color(0xFF3D5070), letterSpacing = 0.5.sp)
                Text(serverUrl, fontSize = 12.sp, color = accentColor, fontWeight = FontWeight.Medium)
                Text("Click to edit configuration", fontSize = 9.sp, color = textSecondary)
            }
        }
    }

    if (showUrlDialog) {
        AlertDialog(
            onDismissRequest = { showUrlDialog = false },
            title = { Text("Server Configuration", color = textPrimary) },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Enter the Flask Server IP / Domain address:", fontSize = 12.sp, color = textSecondary)
                    OutlinedTextField(
                        value = tempUrl,
                        onValueChange = { tempUrl = it },
                        label = { Text("Server URL") },
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = accentColor,
                            unfocusedBorderColor = cardBorder
                        )
                    )
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        serverUrl = tempUrl
                        sharedPrefs.edit().putString("server_url", tempUrl).apply()
                        showUrlDialog = false
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = accentColor)
                ) {
                    Text("Save")
                }
            },
            dismissButton = {
                TextButton(onClick = { showUrlDialog = false }) {
                    Text("Cancel", color = textSecondary)
                }
            },
            containerColor = cardBg
        )
    }
}
