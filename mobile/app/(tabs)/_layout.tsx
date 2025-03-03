import { Tabs, useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import React from 'react';
import { ActivityIndicator, Platform, View } from 'react-native';

import { HapticTab } from '@/components/HapticTab';
import { IconSymbol } from '@/components/ui/IconSymbol';
import TabBarBackground from '@/components/ui/TabBarBackground';
import { Colors } from '@/constants/Colors';
import { useColorScheme } from '@/hooks/useColorScheme';
import SignupScreen from '../auth/signup';
import TokenManager from '../auth/TokenManager';

export default function TabLayout() {
  const colorScheme = useColorScheme();
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);

    const checkAuth = async () => {
      try {
        const hasToken = await TokenManager.getInstance().hasValidTokens();

        if (hasToken && isMounted) {
          console.log("User is authenticated. Redirecting to pre-application.");
          router.replace('/pre-application'); 
        } else {
          console.log("No valid token found. Redirecting to signup.");
          setIsAuthenticated(false); 
        }
      } catch (error) {
        console.error('Error checking auth token:', error);
        setIsAuthenticated(false);
      }
    };

    checkAuth();

    return () => setIsMounted(false);
  }, [isMounted]);

  if (isAuthenticated === null) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color={Colors[colorScheme ?? 'light'].tint} />
      </View>
    );
  }

  if (!isAuthenticated) {
    return <SignupScreen />;
  }

  return (
    <Tabs
      screenOptions={{
        headerShown: false, // ✅ Hides headers for all tab screens
        tabBarActiveTintColor: Colors[colorScheme ?? 'light'].tint,
        tabBarButton: HapticTab,
        tabBarBackground: TabBarBackground,
        tabBarStyle: Platform.select({
          ios: { position: 'absolute' },
          default: {},
        }),
      }}>
      <Tabs.Screen
        name="index"
        options={{
          title: 'Home',
          headerShown: false, // ✅ Ensure individual screens also have no headers
          tabBarIcon: ({ color }) => <IconSymbol size={28} name="house.fill" color={color} />,
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          title: 'Explore',
          headerShown: false, // ✅ Ensure no headers for Explore page
          tabBarIcon: ({ color }) => <IconSymbol size={28} name="paperplane.fill" color={color} />,
        }}
      />
    </Tabs>
  );
}
