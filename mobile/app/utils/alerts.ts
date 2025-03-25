import { Alert, Platform } from 'react-native';

export const sendAlert = (title: string, message: string, onConfirm?: () => void) => {
  if (Platform.OS === 'ios' || Platform.OS === 'android') {
    Alert.alert(
      title,
      message,
      [
        { text: "Cancel", style: "cancel" },
        { text: "OK", onPress: onConfirm }
      ]
    );
  } else if (Platform.OS === 'web') {
    if (window.confirm(message)) {
      onConfirm?.();
    }
  }
};

export default sendAlert;