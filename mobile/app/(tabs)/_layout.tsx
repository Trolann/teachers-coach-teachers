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
  const [checkingAuth, setCheckingAuth] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const checkAuth = async () => {
      try {
        const hasToken = await TokenManager.getInstance().hasValidTokens();
        

        if (hasToken && isMounted) {
          console.log("User is authenticated. Redirecting to pre-application.");
          const userRole = await TokenManager.getInstance().getUserRole();
          // const userStatus = await TokenManager.getInstance().getUserStatus();

          // if (userRole === 'mentor' && userStatus === 'approved') {
          //   console.log("User is a mentor and approved. Redirecting to mentor landing.");
          //   router.navigate('/mentor-landing');
          // } else if (userRole === 'mentor' && userStatus === 'denied') {
          //   console.log("User is a mentor and denied. Redirecting to mentor denied.");
          //   router.navigate('/mentor-denied');
          // } else if (userRole === 'mentor' && userStatus === 'pending') {
          //   console.log("User is a mentor and pending. Redirecting to pre-application.");
          //   router.navigate('/pre-application');
          // } else if (userRole === 'mentee') {
          //   console.log("User is a mentee. Redirecting to mentee matching."); 
          //   router.navigate('/mentee-matching');
          // } else {
          //   console.log("User role is not recognized. Redirecting to pre-application.");
          //   router.navigate('/pre-application');
          // }
          // if (userRole === 'mentor') {
          //   console.log("User is a mentor. Redirecting to mentor landing."); 
          //   router.navigate('/mentor-landing');
          // } else if (userRole === 'mentee') {
          //   console.log("User is a mentee. Redirecting to mentee matching."); 
          //   router.navigate('/mentee-matching');
          // }

          
          router.replace('/mentee-matching');
          setIsAuthenticated(true);
        } else if (isMounted) {
          console.log("No valid token found. Showing signup.");
          setIsAuthenticated(false);
        }
      } catch (error) {
        console.error('Error checking auth token:', error);
        if (isMounted) setIsAuthenticated(false);
      } finally {
        if (isMounted) setCheckingAuth(false);
      }
    };

    checkAuth();

    return () => {
      isMounted = false;
    };
  }, []);

  if (checkingAuth) {
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
        headerShown: false,
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
          headerShown: false,
          tabBarIcon: ({ color }) => <IconSymbol size={28} name="house.fill" color={color} />,
        }}
      />
      <Tabs.Screen
        name="explore"
        options={{
          title: 'Explore',
          headerShown: false,
          tabBarIcon: ({ color }) => <IconSymbol size={28} name="paperplane.fill" color={color} />,
        }}
      />
    </Tabs>
  );
}
