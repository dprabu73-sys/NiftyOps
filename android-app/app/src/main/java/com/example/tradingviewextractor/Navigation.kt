package com.example.tradingviewextractor

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.navigation3.runtime.entryProvider
import androidx.navigation3.runtime.rememberNavBackStack
import androidx.navigation3.ui.NavDisplay
import com.example.tradingviewextractor.ui.main.MainScreen
import kotlinx.coroutines.delay

@Composable
fun MainNavigation() {
  val backStack = rememberNavBackStack(Splash)

  NavDisplay(
    backStack = backStack,
    onBack = { backStack.removeLastOrNull() },
    entryProvider =
      entryProvider {
        entry<Splash> {
          SplashScreen(
            onNavigateToMain = {
              backStack.add(Main)
              backStack.remove(Splash) // Remove splash from backstack so back button exits the app
            }
          )
        }
        entry<Main> {
          MainScreen(
            onItemClick = { navKey -> backStack.add(navKey) },
            modifier = Modifier.safeDrawingPadding().padding(16.dp)
          )
        }
      },
  )
}

@Composable
fun SplashScreen(onNavigateToMain: () -> Unit) {
  val darkBg = Color(0xFF0B0F19)
  val textPrimary = Color(0xFFF8FAFC)
  val textSecondary = Color(0xFF94A3B8)
  val accentColor = Color(0xFF4F46E5)

  LaunchedEffect(Unit) {
    delay(2000)
    onNavigateToMain()
  }

  Box(
    modifier = Modifier
      .fillMaxSize()
      .background(darkBg),
    contentAlignment = Alignment.Center
  ) {
    Column(
      horizontalAlignment = Alignment.CenterHorizontally,
      verticalArrangement = Arrangement.spacedBy(16.dp),
      modifier = Modifier.padding(24.dp)
    ) {
      Text(
        "TradingView Extractor Pro",
        fontSize = 24.sp,
        fontWeight = FontWeight.Bold,
        color = textPrimary
      )
      
      CircularProgressIndicator(
        color = accentColor,
        modifier = Modifier.size(36.dp)
      )
      
      Spacer(modifier = Modifier.height(32.dp))
      
      Text(
        "Developed by Prabu Dhanapal",
        fontSize = 13.sp,
        color = textSecondary,
        fontWeight = FontWeight.Medium
      )
    }
  }
}
