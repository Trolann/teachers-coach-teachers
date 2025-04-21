import React, { useRef, useEffect } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import ConfettiCannon from 'react-native-confetti-cannon';
import MenteeCard from '@/components/MenteeCard';
import { Ionicons } from '@expo/vector-icons';

type Props = {
  goToCallScreen: () => void;
};

export const HomeScreen = ({ goToCallScreen }: Props) => {
  const { mentor: mentorString } = useLocalSearchParams();
  const mentor = mentorString ? JSON.parse(mentorString as string) : null;

  const confettiRef = useRef<any>(null);

  useEffect(() => {
    confettiRef.current?.start();
  }, []);

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        {/* Confetti positioned absolutely over everything */}
        <View style={StyleSheet.absoluteFill}>
          <ConfettiCannon
            count={80}
            origin={{ x: -10, y: 0 }}
            autoStart={false}
            fadeOut={true}
            ref={confettiRef}
            explosionSpeed={400}
            fallSpeed={2900}
          />
        </View>

        <Text style={styles.cardTitle}>
          You've Matched with {mentor?.name || 'your mentor'} 🥳
        </Text>

        <View style={styles.bottomContainer}>
          <View style={styles.card}>
            <MenteeCard
              mentor={mentor}
              infoVisible={undefined}
              toggleInfo={undefined}
            />



          </View>
        </View>
      </View>
      <TouchableOpacity style={styles.button} onPress={goToCallScreen}>
        <View style={styles.buttonContent}>
          <Text style={styles.buttonText}>Join Video Call</Text>
          <Ionicons name="videocam-outline" size={24} color="#fff" style={{ marginLeft: 8 }} />
        </View>
      </TouchableOpacity>
    </SafeAreaView>
  );
};



const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#f7f7f7',
  },
  absoluteFill: {
    position: 'absolute',
    top: 0,
    right: 0,
    bottom: 0,
    left: 0,
  },

  container: {
    backgroundColor: '#f7f7f7',
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  bottomContainer: {
    flexGrow: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f7f7f7',
  },

  card: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
    alignItems: 'center',
  },
  cardTitle: {
    fontSize: 26,
    fontWeight: '600',
    color: '#222',
    marginBottom: 20,
    textAlign: 'center',
    paddingBottom: 10,
  },
  button: {
    backgroundColor: '#00c851',
    paddingVertical: 12,
    paddingHorizontal: 25,
    borderRadius: 0,
    paddingBottom: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '500',
  },

  infoText: {
    fontSize: 16,
    marginBottom: 10,
    color: '#444',
  },
  infoValue: {
    fontWeight: '500',
    color: '#000',
  },
  bio: {
    marginTop: 12,
    fontSize: 15,
    lineHeight: 22,
    color: '#555',
    paddingBottom: 15,
  },
  buttonContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },

});
