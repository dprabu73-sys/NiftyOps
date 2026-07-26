package com.example.niftyops.ui.webview

import android.annotation.SuppressLint
import android.content.Context
import android.webkit.WebChromeClient
import android.webkit.WebView
import android.webkit.WebViewClient
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView

@OptIn(ExperimentalMaterial3Api::class)
@SuppressLint("SetJavaScriptEnabled")
@Composable
fun WebViewScreen(
    onBackToLauncher: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val sharedPrefs = remember { context.getSharedPreferences("niftyops_prefs", Context.MODE_PRIVATE) }
    
    var serverUrl by remember { 
        mutableStateOf(sharedPrefs.getString("server_url", "http://192.168.1.100:5001") ?: "http://192.168.1.100:5001") 
    }
    
    var showSettingsDialog by remember { mutableStateOf(false) }
    var tempUrl by remember { mutableStateOf(serverUrl) }
    var webViewInstance by remember { mutableStateOf<WebView?>(null) }
    var isLoading by remember { mutableStateOf(true) }

    val darkBg = Color(0xFF080E1A)
    val cardBg = Color(0xFF0D1523)
    val textPrimary = Color(0xFFF0F6FF)
    val accentColor = Color(0xFF6366F1)

    // Handle android system back key within webview
    BackHandler(enabled = webViewInstance?.canGoBack() == true) {
        webViewInstance?.goBack()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("NiftyOps Terminal", fontSize = 16.sp, fontWeight = FontWeight.Bold, color = textPrimary)
                        Text(serverUrl, fontSize = 10.sp, color = Color(0xFF6B7FA3))
                    }
                },
                navigationIcon = {
                    IconButton(onClick = {
                        if (webViewInstance?.canGoBack() == true) {
                            webViewInstance?.goBack()
                        } else {
                            onBackToLauncher()
                        }
                    }) {
                        Text("◀", color = textPrimary, fontSize = 14.sp)
                    }
                },
                actions = {
                    IconButton(onClick = { 
                        isLoading = true
                        webViewInstance?.reload() 
                    }) {
                        Text("🔄", color = textPrimary, fontSize = 16.sp)
                    }
                    IconButton(onClick = { 
                        tempUrl = serverUrl
                        showSettingsDialog = true 
                    }) {
                        Text("⚙️", color = textPrimary, fontSize = 16.sp)
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
        Box(
            modifier = modifier
                .padding(paddingValues)
                .fillMaxSize()
                .background(darkBg)
        ) {
            AndroidView(
                modifier = Modifier.fillMaxSize(),
                factory = { ctx ->
                    WebView(ctx).apply {
                        webViewClient = object : WebViewClient() {
                            override fun onPageFinished(view: WebView?, url: String?) {
                                super.onPageFinished(view, url)
                                isLoading = false
                            }
                        }
                        webChromeClient = WebChromeClient()
                        settings.javaScriptEnabled = true
                        settings.domStorageEnabled = true
                        settings.loadWithOverviewMode = true
                        settings.useWideViewPort = true
                        settings.databaseEnabled = true
                        
                        loadUrl(serverUrl)
                        webViewInstance = this
                    }
                },
                update = { webView ->
                    if (webView.url != serverUrl) {
                        webView.loadUrl(serverUrl)
                    }
                }
            )

            if (isLoading) {
                Box(
                    modifier = Modifier.fillMaxSize().background(darkBg.copy(alpha = 0.7f)),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator(color = accentColor)
                }
            }
        }
    }

    if (showSettingsDialog) {
        AlertDialog(
            onDismissRequest = { showSettingsDialog = false },
            title = { Text("Server Configuration", color = textPrimary) },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Enter the Flask Server IP / Domain address:", fontSize = 12.sp, color = Color(0xFF6B7FA3))
                    OutlinedTextField(
                        value = tempUrl,
                        onValueChange = { tempUrl = it },
                        label = { Text("Server URL") },
                        singleLine = true,
                        colors = OutlinedTextFieldDefaults.colors(
                            focusedBorderColor = accentColor,
                            unfocusedBorderColor = Color(0xFF243049)
                        )
                    )
                    Text("Tip: Ensure your mobile and PC are on the same Wi-Fi network.", fontSize = 10.sp, color = Color(0xFF3D5070))
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        serverUrl = tempUrl
                        sharedPrefs.edit().putString("server_url", tempUrl).apply()
                        showSettingsDialog = false
                        isLoading = true
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = accentColor)
                ) {
                    Text("Connect")
                }
            },
            dismissButton = {
                TextButton(onClick = { showSettingsDialog = false }) {
                    Text("Cancel", color = Color(0xFF6B7FA3))
                }
            },
            containerColor = cardBg
        )
    }
}
