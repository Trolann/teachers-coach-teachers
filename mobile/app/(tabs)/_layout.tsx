import { Tabs, useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import React from 'react';
import { ActivityIndicator, Platform, View } from 'react-native';

import { HapticTab } from '@/components/HapticTab';
import { IconSymbol } from '@/components/ui/IconSymbol';
import TabBarBackground from '@/components/ui/TabBarBackground';
import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';
import LoginScreen from '../auth/login';
import SignupScreen from '../auth/signup';


export default function TabLayout() {
  const colorScheme = useColorScheme();
  const router = useRouter();

  // Simulating authentication state (replace with actual auth logic)
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

  // TODO: No longer simulate auth state
  useEffect(() => {
    // Simulating fetching auth status
    setTimeout(() => {
        // TODO: Trevor changed this to true to debug with index.tsx
      setIsAuthenticated(true); // Change to true if user is logged in
    }, 1000);
  }, []);
  
  if (isAuthenticated === null) {
    // Show a loading indicator while checking auth state
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color={Colors[colorScheme ?? 'light'].tint} />
      </View>
    );
  }

  if (!isAuthenticated) {
    // return <SignupScreen />;
    return <LoginScreen />;
  }

  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: Colors[colorScheme ?? 'light'].tint,
        headerShown: false,
        tabBarButton: HapticTab,
        tabBarBackground: TabBarBackground,
        tabBarStyle: Platform.select({
          ios: {
            // Use a transparent background on iOS to show the blur effect
            position: 'absolute',
          },
          default: {},
        }),
      }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          tabBarIcon: ({ color }) => <IconSymbol size={28} name="house.fill" color={color} />,
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          title: 'Explore',
          tabBarIcon: ({ color }) => <IconSymbol size={28} name="paperplane.fill" color={color} />,
        }}
      />
    </Tabs>
  );
}
