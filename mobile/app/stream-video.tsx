import React, { useState } from 'react';
import { SafeAreaView, StyleSheet } from 'react-native';
import { HomeScreen } from './HomeScreen';
import { CallScreen } from './CallScreen';
import 'react-native-gesture-handler';


// 1. Import the StreamVideo and StreamVideoClient components
import {
  StreamVideo,
  StreamVideoClient,
} from '@stream-io/video-react-native-sdk';
import { router, useLocalSearchParams } from 'expo-router';

// 2. Create a StreamVideoClient instance
import { STREAM_DEMO_CREDS } from '../constants/StreamDemoCredentials';
import { Gesture, GestureHandlerRootView } from 'react-native-gesture-handler';

const { apiKey, userId, token, callId } = STREAM_DEMO_CREDS;

const user = {
  id: userId,
  name: 'Random User',
  image: 'https://getstream.io/random_png/?id=1&name=Random+User',
};

// 4. Create a StreamVideoClient instance
const client = new StreamVideoClient({ apiKey, user, token });

export default function App() {

  // console.log(imagePath);

  const [activeScreen, setActiveScreen] = useState('home');

  const goToCallScreen = () => setActiveScreen('call-screen');
  const goToHomeScreen = () => {
    setActiveScreen('home');
    router.push({
      pathname: '/mentee-matching',
    });
  };
  return (
    // 5. Wrap your app with the StreamVideo component
    <GestureHandlerRootView style={{ flex: 1 }}>
    <StreamVideo client={client}>
      <SafeAreaView style={styles.container}>
        {activeScreen === 'call-screen' ? (
          <CallScreen goToHomeScreen={goToHomeScreen} callId={callId} />
        ) : (
          <HomeScreen goToCallScreen={goToCallScreen} />
        )}
      </SafeAreaView>
    </StreamVideo>
    </GestureHandlerRootView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    textAlign: 'center',
  },
});
