import React, { useEffect, useState } from 'react';
import { API_URL } from '../../config/api';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';

export default function HomeScreen() {
  const [dbStatus, setDbStatus] = useState('Checking database...');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkDatabase = async () => {
      console.log('Fetching from:', `${API_URL}/admin/debug/check-database`);
      try {
        const accessToken = "test-1234" // TODO: Replace with accesstoken from cognito
        const headers = new Headers();
        headers.append('Authorization', `Bearer ${accessToken}`);
        const response = await fetch(`${API_URL}/admin/debug/check-database`, {
            method: 'GET',
            headers: headers
        });
        if (!response.ok) {
          throw new Error('Failed to fetch database status');
        }
        const data = await response.json();
        setDbStatus(data.message);
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
