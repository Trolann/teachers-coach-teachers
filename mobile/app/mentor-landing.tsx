import React, { useState, useRef, useEffect } from 'react';
import { View, Text, Switch, StyleSheet, Image, TouchableOpacity, Linking } from 'react-native';
import SwipeCards from 'react-native-swipe-cards';
import BackendManager from './auth/BackendManager';
import Header from '@/components/Header';
import { router } from 'expo-router';
import Ionicons from '@expo/vector-icons/build/Ionicons';
import { STREAM_DEMO_CREDS } from '../constants/StreamDemoCredentials';

const { callId } = STREAM_DEMO_CREDS;

const mentees = [
  {
    id: 1,
    name: 'Alex Johnson',
    primarySubject: 'Math',
    district: 'Sacramento City Unified School District',
    image: require('../assets/images/stock_mentee2.png'),
  },
  {
    id: 2,
    name: 'Maria Gomez',
    primarySubject: 'Science',
    district: 'East Side Union High School District',
    image: require('../assets/images/stock_mentee2.png'),
  },
];

const MentorLandingScreen = () => {
  const [isOnline, setIsOnline] = useState(false);
  const [cards, setCards] = useState(mentees);
  const [buttonsDisabled, setButtonsDisabled] = useState(false);
  const userName = 'Susie';
  const swiperRef = useRef(null);

  const toggleSwitch = async (value: boolean) => {
    setIsOnline(value);
    const path = value ? '/api/mentor_status/set_online' : '/api/mentor_status/set_offline';
    try {
      const response = await BackendManager.getInstance().sendRequest(path, 'POST');
      if (!response.ok) {
        setIsOnline(!value);
        console.error('Status toggle failed:', await response.json());
      }
    } catch (error) {
      setIsOnline(!value);
      console.error('Error toggling status:', error);
    }
  };

  const Card = ({ name, primarySubject, district, image }) => (
    <View style={styles.card}>
      <Image source={image} style={styles.mentorImage} />
      <View style={styles.infoOverlay}>
        <Text style={styles.mentorName}>{name}</Text>
        <Text style={styles.mentorSubject}>{primarySubject}</Text>
        <Text style={styles.mentorLocation}>{district}</Text>
      </View>
    </View>
  );

  const handleAccept = (card) => {
    if (buttonsDisabled) return;
    setButtonsDisabled(true);

    const url = `https://getstream.io/video/demos/join/${callId}`;
    Linking.openURL(url).catch((err) => {
      console.error("Failed to open URL:", err);
      setButtonsDisabled(false); // Re-enable if failed
    });
  };

  const handleReject = (card) => {
    // Can be used for tracking or logic
    console.log('Rejected:', card?.name);
  };

  const handleNoMoreCards = () => {
    setCards([]);
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Header subtitle="Mentor Landing" />
      </View>

      <View style={styles.toggleContainer}>
        <Text style={styles.togglePrompt}>
          {isOnline ? 'Status: Online' : 'Status: Offline'}
        </Text>
        {!isOnline && (
          <Text style={styles.toggleSubtext}>
            Click the toggle button to indicate you are online
          </Text>
        )}
        <Switch
          trackColor={{ false: '#D1D5DB', true: '#C7F9CC' }} // light gray when off
          thumbColor={isOnline ? '#34C759' : '#FFFFFF'} // green or white thumb
          ios_backgroundColor="#D1D5DB" // ✅ light gray background for iOS
          onValueChange={toggleSwitch}
          value={isOnline}
        />
      </View>

      {isOnline && cards.length > 0 ? (
        <View style={styles.swiperWrapper}>
          <Text style={styles.noMatchesTitle}>Mentee Request ❤️</Text>
          <SwipeCards
            cards={cards}
            renderCard={(cardData) => <Card {...cardData} />}
            renderNoMoreCards={() => (
              <View style={styles.emptyCard}>
                <Text style={styles.emptyCardText}>No more mentees</Text>
              </View>
            )}
            handleYup={handleAccept}
            handleNope={handleReject}
            showYup
            showNope
            cardRemoved={() => setButtonsDisabled(false)}
            cardStyle={styles.card}
          />
          <View style={styles.buttonContainer}>
            <TouchableOpacity
              style={styles.rejectButton}
              onPress={() => swiperRef.current?.nope()}
            >
              <Text style={styles.rejectButtonText}>Reject</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.acceptButton}
              onPress={() => {
                const currentCard = cards[0];
                if (currentCard) handleAccept(currentCard);
              }}
            >
              <View style={styles.joinCallContent}>
                <Text style={styles.acceptButtonText}>Join Call</Text>
                <Ionicons name="videocam-outline" size={20} color="#fff" style={{ marginLeft: 8 }} />
              </View>
            </TouchableOpacity>
          </View>
        </View>
      ) : isOnline && cards.length === 0 ? (
        <View style={styles.noMatchesContainer}>
          <Text style={styles.noMatchesTitle}>No Mentee Matches 💔</Text>
          <Text style={styles.noMatchesText}>
            Please wait patiently until our AI matches you
          </Text>
        </View>
      ) : null}
    </View>
  );
};

export default MentorLandingScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    paddingTop: 65,
    justifyContent: 'flex-start',
  },
  header: {
    paddingHorizontal: 20,
  },
  toggleContainer: {
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 20,
  },
  togglePrompt: {
    fontSize: 24,
    fontWeight: '600',
    marginBottom: 8,
  },
  toggleSubtext: {
    fontSize: 18,
    color: '#777',
    textAlign: 'center',
    marginBottom: 16,
  },
  noMatchesContainer: {
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  noMatchesTitle: {
    fontSize: 22,
    fontWeight: '600',
    color: '#333',
    marginBottom: 30,
  },
  noMatchesText: {
    fontSize: 16,
    color: '#555',
    textAlign: 'center',
    lineHeight: 22,
  },
  swiperWrapper: {
    height: 500,
    justifyContent: 'center',
    alignItems: 'center',
    width: '100%',
  },
  card: {
    width: 320,
    height: 440,
    borderColor: 'black',
    borderRadius: 20,
    backgroundColor: '#fff',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 20,
    elevation: 5,
    alignItems: 'center',
    overflow: 'hidden',
    alignSelf: 'center',
  },
  mentorImage: {
    width: '90%',
    height: '70%',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  infoOverlay: {
    width: '100%',
    height: '30%',
    backgroundColor: '#fff',
    paddingVertical: 3,
    paddingHorizontal: 8,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
    alignItems: 'center',
    justifyContent: 'center',
  },
  mentorName: {
    fontSize: 22,
    fontWeight: '700',
    textAlign: 'center',
    color: '#333',
  },
  mentorSubject: {
    fontSize: 18,
    color: '#555',
    marginTop: 4,
  },
  mentorLocation: {
    fontSize: 16,
    color: '#777',
    marginTop: 2,
  },
  joinCallContent:{
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  emptyCard: {
    justifyContent: 'center',
    alignItems: 'center',
    height: 320,
    width: '90%',
    maxWidth: 320,
    backgroundColor: '#f9f9f9',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#ddd', 
    alignSelf: 'center',
    padding: 24,
  },
  emptyCardText: {
    fontSize: 20,
    color: '#888',
    textAlign: 'center',
  },
  buttonContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    gap: 20, // space between buttons
  },
  rejectButton: {
    paddingVertical: 12,
    paddingHorizontal: 40,
    backgroundColor: '#FF3B30', // red
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  rejectButtonText: {
    fontSize: 18,
    color: '#fff',
    fontWeight: '600',
  },
  acceptButton: {
    paddingVertical: 12,
    paddingHorizontal: 40,
    backgroundColor: '#34C759', // green
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  acceptButtonText: {
    fontSize: 18,
    color: '#fff',
    fontWeight: '600',
  },
});
