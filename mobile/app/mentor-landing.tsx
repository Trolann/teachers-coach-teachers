import React, { useState } from 'react';
import { View, Text, Switch, StyleSheet, Image, TouchableOpacity } from 'react-native';
import SwipeCards from 'react-native-swipe-cards';

const mentees = [
  { id: 1, name: 'Alex Johnson', district: 'Sacramento City Unified School District', goal: 'Improve teaching skills in math' },
  { id: 2, name: 'Maria Gomez', district: 'East Side Union High School District', goal: 'Explore science curriculum options' } // Dummy mentees
];

const MentorLandingScreen = () => {
  const [isOnline, setIsOnline] = useState(false);
  const [acceptedMentee, setAcceptedMentee] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const userName = 'Susie'; // Replace with dynamic username

  const toggleSwitch = () => setIsOnline(previousState => !previousState);

  const Card = ({ name, district, goal }) => (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>{name}</Text>
      <Text style={styles.cardText}>District: {district}</Text>
      <Text style={styles.cardText}>Goal: {goal}</Text>
    </View>
  );

  const handleAccept = () => {
    const mentee = mentees[currentIndex];
    setAcceptedMentee(mentee);
    console.log('Accepted Mentee:', mentee);
  };

  const handleYes = () => {
    setCurrentIndex(i => i + 1);
  };

  const handleNo = () => {
    setCurrentIndex(i => i + 1);
  };

  const renderCard = (cardData) => <Card {...cardData} />;

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>Hi, {userName} 👋</Text>
          <Text style={styles.subtext}>Are you ready to mentor?</Text>
        </View>
        <Image
          source={require('../assets/images/mentor-profile-picture.png')} // Replace with profile picture of the user stored within our database
          style={styles.profileImage}
        />
      </View>

      {/* Toggle */}
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
          trackColor={{ false: '#767577', true: '#C7F9CC' }}
          thumbColor={isOnline ? '#34C759' : '#f4f3f4'}
          ios_backgroundColor="#3e3e3e"
          onValueChange={toggleSwitch}
          value={isOnline}
        />
      </View>

      {/* Mentee Cards */}
      {isOnline && mentees.length > 0 ? (
        <View style={{ flex: 1, alignItems: 'center' }}>
          <Text style={styles.noMatchesTitle}>Mentee Request ❤️</Text>
          <SwipeCards
            cards={mentees}
            renderCard={renderCard}
            renderNoMoreCards={() => <Text>No more mentees</Text>}
            handleYes={handleYes}
            handleNo={handleNo}
            showYes={false}
            showNo={false}
          />
          <TouchableOpacity style={styles.acceptButton} onPress={handleAccept}>
            <Text style={styles.acceptButtonText}>Accept</Text>
          </TouchableOpacity>
        </View>
      ) : isOnline ? (
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
    padding: 24,
    justifyContent: 'flex-start',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 40,
  },
  greeting: {
    fontSize: 28,
    fontWeight: '600',
  },
  subtext: {
    fontSize: 18,
    color: '#555',
  },
  profileImage: {
    width: 80,
    height: 80,
    borderRadius: 44,
  },
  toggleContainer: {
    alignItems: 'center',
    marginTop: 20,
    marginBottom: 32,
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
    marginBottom: 12,
  },
  noMatchesText: {
    fontSize: 16,
    color: '#555',
    textAlign: 'center',
    lineHeight: 22,
  },
  card: {
    width: 300,
    padding: 20,
    backgroundColor: '#f0f0f0',
    borderRadius: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 5,
  },
  cardTitle: {
    fontSize: 22,
    fontWeight: '700',
    marginBottom: 10,
  },
  cardText: {
    fontSize: 16,
    marginBottom: 6,
    color: '#333',
  },
  acceptButton: {
    marginTop: 20,
    paddingVertical: 12,
    paddingHorizontal: 40,
    backgroundColor: '#34C759',
    borderRadius: 12,
  },
  acceptButtonText: {
    fontSize: 18,
    color: '#fff',
    fontWeight: '600',
  },
});