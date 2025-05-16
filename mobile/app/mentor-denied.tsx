import React from 'react';
import { View, Text, Image, SafeAreaView } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { Header } from '@/components/Header';

export default function MentorDenied() {
  const { name } = useLocalSearchParams();

  return (
    <SafeAreaView style={{ flex: 1, padding: 24, justifyContent: 'center', backgroundColor: '#fff' }}>
      <Header subtitle="Mentor Application Status" />
      <View style={{ alignItems: 'center' }}>
        <Text style={{ marginTop: 8, fontSize: 14, color: '#666' }}>Thank you for applying!</Text>

        <View style={{ marginTop: 40, alignItems: 'center' }}>
          <Text style={{ fontSize: 24, fontWeight: 'bold', textAlign: 'center' }}>
            Your application{'\n'}has been denied
          </Text>
          <Text style={{ marginTop: 12, fontSize: 14, color: '#666', textAlign: 'center' }}>
            We're sorry. Applications are not approved for many reasons. We encourage you to sign up as a mentee and apply again in one year.
          </Text>
        </View>
      </View>
    </SafeAreaView>
  );
}
