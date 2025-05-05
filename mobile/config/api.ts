import Constants from 'expo-constants';
import { Platform } from 'react-native';

const localhost = Platform.select({
  ios: process.env.EXPO_PUBLIC_IOS_HOSTNAME || 'localhost',
  android: Constants.expoConfig?.hostUri?.split(':')[0] ?? '10.0.2.2',
  default: 'localhost',
});

export const API_URL = `http://${localhost}:5001`;
