package com.example.tradingviewextractor

import androidx.navigation3.runtime.NavKey
import kotlinx.serialization.Serializable

@Serializable data object Splash : NavKey
@Serializable data object Launcher : NavKey
@Serializable data class MainApp(val initialTab: Int = 0) : NavKey

