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
          headerShown: false, 
          animation: 'fade',
          presentation: 'card', 
        }}
      >
        <Stack.Screen name="(tabs)" />
        <Stack.Screen name="pre-application" />
        <Stack.Screen name="pre-matching-mentee"/>
        <Stack.Screen name="+not-found"/>
        <Stack.Screen name="mentee-matching"/>
        <Stack.Screen name="stream-video"/>
        <Stack.Screen name="CallScreen" options={{ animation: 'slide_from_bottom' }}/>
        <Stack.Screen name="HomeScreen"/>
      </Stack>

      <StatusBar style="auto" />
    </ThemeProvider>
  );
}
