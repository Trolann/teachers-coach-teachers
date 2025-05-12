import React, { useState, useRef, useEffect } from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet, Alert, Animated, Platform, Pressable, Button, Linking } from 'react-native';
import BackendManager from './auth/BackendManager';
import SwipeCards from 'react-native-swipe-cards';
import { Ionicons } from '@expo/vector-icons';
import { Href, Link, useRouter } from 'expo-router';
import Header from '@/components/Header';
import MenteeCard from '@/components/MenteeCard';

export default function MenteeLandingScreen() {
  const router = useRouter();
  const [matchedMentor, setMatchedMentor] = useState(null);

  const [infoVisible, setInfoVisible] = useState(null);

  const toggleInfo = (mentorId) => {
    setInfoVisible(infoVisible === mentorId ? null : mentorId);
  };

  /*
  const [mentorList, setMentorList] = useState([
    {
      id: 1, name: 'Melissa Gao', subject: 'Biology', location: 'Austin, Texas', rating: 4.8, image: require('../assets/images/stock_mentor2.jpg'),
      bio: "Passionate about helping students succeed in Biology. Over 5 years of experience in teaching and mentoring."
    },
    {
      id: 2, name: 'Mark Smith', subject: 'Physics', location: 'San Jose, CA', rating: 4.6, image: require('../assets/images/stock_mentor3.jpg'),
      bio: "Physics enthusiast with expertise in quantum mechanics and astrophysics. Loves solving complex problems!"
    },
    {
      id: 3, name: 'Jennifer Miller', subject: 'History', location: 'San Francisco, CA', rating: 4.6, image: require('../assets/images/stock_mentor4.jpeg'),
      bio: "History geek with a knack for storytelling. Specializes in American and European history."
    },
  ]);
  */

  const [mentorList, setMentorList] = useState([]);

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        const backend = BackendManager.getInstance();
        const matches = await backend.getMatchesForMentee();

        // Transform matches into format compatible with swipe cards
        const formatted = matches.map((mentor, index) => ({
          card_id: index + 1,
          mentor_id: mentor.user_id,
          name: `${mentor.firstName} ${mentor.lastName}`,
          subject: mentor.primarySubject,
          location: `${mentor.county}, ${mentor.state_province}, ${mentor.country}`,
          image: mentor.picture
          ? { uri: mentor.picture }
          : require('../../assets/images/user-without-picture.png')
        }));

        setMentorList(formatted);
      } catch (error) {
        console.error('Failed to load mentor matches:', error);
      }
    };

    fetchMatches();
  }, []);
  
  const animatedValue = useRef(new Animated.Value(0)).current;

  // Function to remove the first mentor from the list (mimics swiping)
  const removeTopCard = () => {
    setMentorList((prevMentors) => prevMentors.slice(1));
  };

  const handleLike = async (card) => {
    try {
      Animated.timing(animatedValue, {
        toValue: 500,
        duration: 300,
        useNativeDriver: true,
      }).start(() => {
        console.log(`Liked ${card.name}`);
        setMentorList((prevMentors) => prevMentors.filter((mentor) => mentor.card_id !== card.card_id));
        setMatchedMentor(card);
      });
  
      const backend = BackendManager.getInstance();
      // Call the API to submit a mentee request
      await backend.submitMenteeRequest(card.mentor_id);
  
    } catch (error) {
      console.error('Failed to submit mentee request:', error);
      Alert.alert('Error', 'Could not send your match request. Please try again.');
    }

    const handleJoin = () => {
      router.push({
        pathname: '/stream-video',
        params: {
          mentor: JSON.stringify(mentorList[0]),
        },
      });
    };

    if (Platform.OS === 'ios' || Platform.OS === 'android') {
      // Alert.alert(
      //   "Join Call",
      //   `Do you want to join a call with ${card.name}?`,
      //   [
      //     { text: "Cancel", style: "cancel" },
      //     { text: "Join", onPress: handleJoin },
      //   ]
      // );
    } else if (Platform.OS === 'web') {
      if (window.confirm(`Do you want to join a call with ${card.name}?`)) {
        handleJoin();
      }
    }
  };

  const handleSkip = (card) => {
    Animated.timing(animatedValue, {
      toValue: -500,
      duration: 300,
      useNativeDriver: true,
    }).start(() => {
      console.log(`Skipped ${card.name}`);
      setMentorList((prevMentors) => prevMentors.filter((mentor) => mentor.card_id !== card.card_id));
    });
  };

  // TODO: Handle Refine Search to go back button
  const handleRefineSearch = () => {
    router.navigate('./pre-matching-mentee');
  };

  const renderCard = (mentor) => {
    return (
      <Animated.View style={{ transform: [{ translateX: new Animated.Value(0) }] }}>
        <MenteeCard
          mentor={mentor}
          infoVisible={infoVisible}
          toggleInfo={toggleInfo}
        />
      </Animated.View>
    );
  }

  // Message when no cards are left
  const renderNoMoreCards = () => (
    <View style={styles.noMoreContainer}>
      <Text style={styles.noMoreText}>No More Mentors</Text>
      <Text style={styles.refineMessage}>To get more matches, refine your search</Text>
      <Ionicons name="arrow-down" size={60} color="black" style={styles.curlyArrow} />
    </View>
  );

  return (
    <View style={styles.container}>
      {/* Header Section */}
      <View style={{ paddingHorizontal: 20 }}>
        <Header subtitle="Swipe Right for a Mentor" />
      </View>

      {/* Swipe Cards */}
      <View style={styles.swipeContainer}>
        <SwipeCards
          cards={mentorList}
          renderCard={renderCard}
          handleYup={handleLike}
          handleNope={handleSkip}
          handleMaybe={handleRefineSearch}
          renderNoMoreCards={renderNoMoreCards}
          showYup
          showNope
          showMaybe
          yupText="Like"
          noText="Skip"
          maybeText="Refine"
          cardRemoved={() => console.log("Card removed")}
          cardStyle={{
            animationConfig: {
              useNativeDriver: true,
            }
          }}
        />
      </View>

      {/* Tinder Style Buttons */}
      <View style={styles.buttonsContainer}>
        {/* X Button -> Left Swipe */}
        <TouchableOpacity
          style={styles.skipButton}
          onPress={() => mentorList.length > 0 && handleSkip(mentorList[0])}>
          <Ionicons name="close-circle-sharp" size={55} color="red" />
        </TouchableOpacity>

        {/* Refine Search Button */}
        <TouchableOpacity style={styles.refineButton} onPress={handleRefineSearch}>
          <Ionicons name="refresh-circle" size={45} color="black" />
        </TouchableOpacity>

        {/* Heart Button -> Right Swipe */}
        <TouchableOpacity
          style={styles.likeButton}
          onPress={() => mentorList.length > 0 && handleLike(JSON.stringify(mentorList[0]))}>
          <Ionicons name="heart-circle-sharp" size={55} color="green" />
        </TouchableOpacity>

      </View>
      {matchedMentor && (
        <View style={styles.congratsOverlay}>
          <View style={styles.congratsCard}>
            <Text style={styles.congratsTitle}>🎉 Congrats!</Text>
            <Text style={styles.congratsText}>
              You've matched with <Text style={{ fontWeight: '600' }}>{matchedMentor.name}</Text>!
            </Text>

            <TouchableOpacity
              style={[styles.continueButton, { marginTop: 20 }]}
              onPress={() => {
                const selectedMentor = matchedMentor;
                setMatchedMentor(null); // close modal first
                router.push({
                  pathname: '/stream-video',
                  params: {
                    mentor: JSON.stringify(selectedMentor),
                  },
                });
              }}
            >
              <Text style={styles.continueButtonText}>Continue</Text>
            </TouchableOpacity>
          </View>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f7f7f7',
    paddingTop: 65,
  },
  swipeContainer: {
    flex: 1,
    alignItems: 'center',
    marginTop: 10,
  },
  card: {
    width: 310,
    height: 560,
    borderRadius: 20,
    backgroundColor: '#fff',
    shadowColor: '#000',
    shadowOpacity: 0.15,
    shadowRadius: 10,
    elevation: 5,
    alignItems: 'center',
    overflow: 'hidden',
    paddingBottom: 10,
  },
  mentorImage: {
    width: '100%',
    height: '75%',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
  },
  overlay: {
    width: '100%',
    padding: 20,
    alignItems: 'center',
  },
  mentorName: {
    fontSize: 22,
    paddingBottom: 10,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  mentorLocation: {
    fontSize: 16,
    paddingBottom: 10,
    color: '#666',
    marginTop: 5,
  },
  mentorRating: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
    margin: 3,
  },
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 5,
    backgroundColor: '#333',
    paddingVertical: 5,
    paddingHorizontal: 8,
    borderRadius: 6,
  },
  onlineIndicator: {
    position: 'absolute',
    top: 26,
    left: 23,
    width: 15,
    height: 15,
    borderRadius: 7,
    backgroundColor: 'green',
    borderWidth: 2,
    borderColor: 'green',
    zIndex: 10,
  },
  noMoreContainer: {
    alignItems: 'center',
    marginTop: 30,
  },
  noMoreText: {
    fontSize: 35,
    paddingBottom: 10,
    fontWeight: 'bold',
    color: '#333',
  },
  curlyArrow: {
    marginTop: 10,
  },
  refineMessage: {
    fontSize: 16,
    color: '#666',
    marginTop: 5,
    marginBottom: 10,
    textAlign: 'center',
  },
  buttonsContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 50,
    paddingBottom: 40,
  },
  skipButton: {
    backgroundColor: 'white',
    borderRadius: 50,
    padding: 10,
    elevation: 3,
  },
  likeButton: {
    backgroundColor: 'white',
    borderRadius: 50,
    padding: 10,
    elevation: 3,
  },
  refineButton: {
    backgroundColor: 'white',
    borderRadius: 50,
    padding: 10,
    elevation: 3,
  },

  infoButton: {
    position: 'absolute',
    top: 15,
    right: 15,
    padding: 5,
  },

  infoBubble: {
    position: 'absolute',
    top: 50,
    right: 10,
    width: 180,
    backgroundColor: 'rgba(100, 100, 100, 0.8)',
    padding: 10,
    borderRadius: 8,
    alignItems: 'center',
  },

  infoText: {
    color: 'white',
    fontSize: 14,
    textAlign: 'center',
  },
  congratsOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.2)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 10,
  },
  congratsCard: {
    backgroundColor: '#fff',
    padding: 20,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
    alignItems: 'center',
  },
  congratsTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#00c851',
    marginBottom: 10,
  },
  congratsText: {
    fontSize: 16,
    color: '#333',
    textAlign: 'center',
  },
  continueButton: {
    backgroundColor: '#00c851',
    paddingVertical: 12,
    paddingHorizontal: 30,
    borderRadius: 10,
  },
  continueButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});