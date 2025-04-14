import React from 'react';
import { Stack } from 'expo-router';
import { ThemeProvider } from '@react-navigation/native';
import { useColorScheme } from 'react-native';
import { DarkTheme, DefaultTheme } from '@react-navigation/native';
import { StatusBar } from 'expo-status-bar';

export default function RootLayout() {
  const colorScheme = useColorScheme();

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <Stack
        screenOptions={{
          headerShown: false, // 🔥 globally remove all headers
          animation: 'slide_from_right', // 👈 accordion-style right-slide
          presentation: 'card', // 👌 native feel
        }}
      >
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="pre-application" />
        <Stack.Screen name="pre-matching-mentee" />
        <Stack.Screen name="+not-found" options={{ animation: 'fade' }} />
      </Stack>

      <StatusBar style="auto" />
    </ThemeProvider>
  );
}
