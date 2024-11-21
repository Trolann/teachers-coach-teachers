import React, { useEffect, useState } from 'react';
import { View, Text, ActivityIndicator, StyleSheet } from 'react-native';

export default function HomeScreen() {
  const [dbStatus, setDbStatus] = useState('Checking database...');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkDatabase = async () => {
      try {
        const response = await fetch('http://localhost:5001/check-database');
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
