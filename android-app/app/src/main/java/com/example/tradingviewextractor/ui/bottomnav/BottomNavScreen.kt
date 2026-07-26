package com.example.tradingviewextractor.ui.bottomnav

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.tradingviewextractor.ui.terminal.LiveTerminalScreen
import com.example.tradingviewextractor.ui.extractor.NativeExtractorScreen
import com.example.tradingviewextractor.ui.analyzer.NativeAnalyzerScreen
import com.example.tradingviewextractor.ui.main.MainScreenViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BottomNavScreen(
    initialTab: Int = 0,
    viewModel: MainScreenViewModel = viewModel { MainScreenViewModel() }
) {
    var selectedTab by remember { mutableStateOf(initialTab) }

    val darkBg = Color(0xFF0B0F19)
    val cardBg = Color(0xFF151C2C)
    val accentColor = Color(0xFF4F46E5)
    val textSecondary = Color(0xFF94A3B8)

    Scaffold(
        bottomBar = {
            NavigationBar(
                containerColor = cardBg,
                tonalElevation = 8.dp
            ) {
                NavigationBarItem(
                    selected = selectedTab == 0,
                    onClick = { selectedTab = 0 },
                    icon = { Text("📊", fontSize = 20.sp) },
                    label = { Text("Terminal", fontSize = 11.sp) },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = accentColor,
                        indicatorColor = accentColor.copy(alpha = 0.2f)
                    )
                )

                NavigationBarItem(
                    selected = selectedTab == 1,
                    onClick = { selectedTab = 1 },
                    icon = { Text("📥", fontSize = 20.sp) },
                    label = { Text("Extractor", fontSize = 11.sp) },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = accentColor,
                        indicatorColor = accentColor.copy(alpha = 0.2f)
                    )
                )

                NavigationBarItem(
                    selected = selectedTab == 2,
                    onClick = { selectedTab = 2 },
                    icon = { Text("📈", fontSize = 20.sp) },
                    label = { Text("Analyzer", fontSize = 11.sp) },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = accentColor,
                        indicatorColor = accentColor.copy(alpha = 0.2f)
                    )
                )

                NavigationBarItem(
                    selected = selectedTab == 3,
                    onClick = { selectedTab = 3 },
                    icon = { Text("⚙️", fontSize = 20.sp) },
                    label = { Text("Settings", fontSize = 11.sp) },
                    colors = NavigationBarItemDefaults.colors(
                        selectedIconColor = accentColor,
                        indicatorColor = accentColor.copy(alpha = 0.2f)
                    )
                )
            }
        },
        containerColor = darkBg
    ) { paddingValues ->
        Box(modifier = Modifier.padding(paddingValues).fillMaxSize()) {
            when (selectedTab) {
                0 -> LiveTerminalScreen(viewModel = viewModel)
                1 -> NativeExtractorScreen(viewModel = viewModel)
                2 -> NativeAnalyzerScreen(viewModel = viewModel)
                3 -> SimplePlaceholderScreen("Settings & Connection", "⚙️ Server IP: https://niftyops.onrender.com\nDesigned & Developed by Prabu Dhanapal")
            }
        }
    }
}

@Composable
fun SimplePlaceholderScreen(title: String, subtitle: String) {
    Column(
        modifier = Modifier.fillMaxSize().padding(24.dp),
        verticalArrangement = Arrangement.Center
    ) {
        Text(title, fontSize = 20.sp, fontWeight = androidx.compose.ui.text.font.FontWeight.Bold, color = Color(0xFFF8FAFC))
        Spacer(modifier = Modifier.height(8.dp))
        Text(subtitle, fontSize = 13.sp, color = Color(0xFF94A3B8))
    }
}
