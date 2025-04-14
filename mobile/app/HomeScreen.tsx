import React, { useRef, useEffect } from 'react';
import { Image, View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { Header } from '@/components/Header';
import { useLocalSearchParams } from 'expo-router';
import MenteeCard from '@/components/MenteeCard';
import ConfettiCannon from 'react-native-confetti-cannon';

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
    <View style={styles.safeArea}>
      {/* Confetti positioned absolutely over everything */}
      <ConfettiCannon
        count={80}
        origin={{ x: -10, y: 0 }}
        autoStart={false}
        fadeOut={true}
        ref={confettiRef}
        explosionSpeed={400}
        fallSpeed={2900}
      />

      <View style={styles.container}>
        <Text style={styles.cardTitle}>
          You've Matched with {mentor?.name || 'your mentor'} ❤️
        </Text>

        <View style={styles.bottomContainer}>
          <View style={styles.card}>
            <MenteeCard
              mentor={mentor}
              infoVisible={undefined}
              toggleInfo={undefined}
            />

            <TouchableOpacity style={styles.button} onPress={goToCallScreen}>
              <Text style={styles.buttonText}>Join Video Call ☎️</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </View>
  );
};



const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  absoluteFill: {
    position: 'absolute',
    top: 0,
    right: 0,
    bottom: 0,
    left: 0
  },

  container: {
    flex: 1,
    paddingHorizontal: 15,
    paddingTop: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
  bottomContainer: {
    flexGrow: 0,
    justifyContent: 'center',
    alignItems: 'center',
  },

  card: {
    backgroundColor: '#fefefe',
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
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
  },
  button: {
    backgroundColor: '#00c851',
    paddingVertical: 12,
    paddingHorizontal: 25,
    borderRadius: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 15,
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

});
