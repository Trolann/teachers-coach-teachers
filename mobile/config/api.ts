import Constants from 'expo-constants';
import { Platform } from 'react-native';

const localhost = Platform.select({
  ios: 'localhost',
  android: Constants.expoConfig?.hostUri?.split(':')[0] ?? '10.0.2.2',
  default: 'localhost',
});

export const API_URL = `http://${localhost}:5001`;
