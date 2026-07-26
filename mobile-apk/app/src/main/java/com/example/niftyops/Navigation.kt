package com.example.niftyops

import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation3.runtime.entryProvider
import androidx.navigation3.runtime.rememberNavBackStack
import androidx.navigation3.ui.NavDisplay
import com.example.niftyops.ui.main.MainScreen
import com.example.niftyops.ui.launcher.LauncherScreen
import com.example.niftyops.ui.webview.WebViewScreen

@Composable
fun MainNavigation() {
  val backStack = rememberNavBackStack(Launcher)

  NavDisplay(
    backStack = backStack,
    onBack = { backStack.removeLastOrNull() },
    entryProvider =
      entryProvider {
        entry<Launcher> {
          LauncherScreen(
            onLaunchTerminal = { backStack.add(WebViewScreen) },
            onLaunchExtractor = { backStack.add(WebViewScreen) }
          )
        }
        entry<Main> {
          MainScreen(
            onBack = { backStack.remove(Main) },
            modifier = Modifier.safeDrawingPadding().padding(16.dp)
          )
        }
        entry<WebViewScreen> {
          WebViewScreen(
            onBackToLauncher = { backStack.remove(WebViewScreen) }
          )
        }
      },
  )
}
