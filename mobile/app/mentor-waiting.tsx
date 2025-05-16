import React from 'react';
import { View, Text, Image, SafeAreaView } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import Header from '@/components/Header';
import BackendManager from './auth/BackendManager';

export default function MentorWaiting() {

  return (
    <SafeAreaView style={{ flex: 1, padding: 24, justifyContent: 'center', backgroundColor: '#fff' }}>
    <Header subtitle="Mentor Application Status"/>
      <View style={{ alignItems: 'center' }}>
        <Text style={{ marginTop: 8, fontSize: 14, color: '#666' }}>Thank you for applying!</Text>

        <View style={{ marginTop: 40, alignItems: 'center' }}>
          <Text style={{ fontSize: 24, fontWeight: 'bold', textAlign: 'center' }}>
            We are reviewing{'\n'}your application
          </Text>
          <Text style={{ marginTop: 12, fontSize: 14, color: '#666', textAlign: 'center' }}>
            Your application was received.
          </Text>
        </View>
      </View>
    </SafeAreaView>
  );
}
