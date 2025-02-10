import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';
import BackendManager from '../auth/backendmanager';
import TokenManager from '../auth/tokenmanager';

export default function HomeScreen() {
  const [dbStatus, setDbStatus] = useState('Checking database...');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkDatabase = async () => {
      try {
        // TODO: REMOVE THIS WHEN WE GET COGNITO TOKENS
        // Set debug tokens
        // const tokenManager = TokenManager.getInstance();
        // await tokenManager.clearTokens();
        // await tokenManager.setTokens({
        //   accessToken: 'test-mobile-5678',
        //   refreshToken: 'refresh-test',
        //   idToken: 'id-test',
        //   expiresIn: 3600
        // });
        // TODO: STOP REMOVING HERE
        const backend = BackendManager.getInstance();
        const message = await backend.checkDatabase();
        setDbStatus(message);
      } catch (error) {
        setDbStatus('Error connecting to backend');
        console.error(error);
      } finally {
        setLoading(false);
      }
    };

    checkDatabase();
  }, []);

  return (
    <View style={styles.container}>
      {loading ? (
        <ActivityIndicator size="large" color="#0000ff" />
      ) : (
        <Text style={styles.status}>{dbStatus}</Text>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  status: {
    fontSize: 18,
    color: '#333',
  },
});
