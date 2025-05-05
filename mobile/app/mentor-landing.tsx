import React, { useState, useRef, useEffect } from 'react';
import { View, Text, Switch, StyleSheet, Image, TouchableOpacity, ImageBackground } from 'react-native';
import Swiper from 'react-native-deck-swiper';
import BackendManager from './auth/BackendManager';

/*
// Dummy mentees
const mentees = [
  {
    id: 1,
    name: 'Alex Johnson',
    primarySubject: 'Math',
    district: 'Sacramento City Unified School District',
    //goal: 'Improve teaching skills in math',
    image: require('../assets/images/mentor-profile-picture.png'),
  },
  {
    id: 2,
    name: 'Maria Gomez',
    primarySubject: 'Science',
    district: 'East Side Union High School District',
    //goal: 'Explore science curriculum options',
    image: require('../assets/images/mentor-profile-picture.png'),
  },
];
*/

const MentorLandingScreen = () => {
  const [isOnline, setIsOnline] = useState(false);
  const [acceptedMentee, setAcceptedMentee] = useState(null);
  const swiperRef = useRef(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [allSwiped, setAllSwiped] = useState(false);
  const [buttonsDisabled, setButtonsDisabled] = useState(false);
  const [mentees, setMentees] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const intervalRef = useRef(null);

  // Trigger fetch when mentor goes online
  useEffect(() => {
    if (isOnline) {
      fetchMentees();
      intervalRef.current = setInterval(fetchMentees, 10000); // Set interval to update mentees every 10 seconds
    } else {
      clearInterval(intervalRef.current); // Clear interval when offline
      setMentees([]); // Clear cards when going offline
    }

    return () => clearInterval(intervalRef.current); // Clear interval when component unmounts or goes offline
  }, [isOnline]);

  const userName = 'Susie'; // Replace with dynamic username

  const toggleSwitch = async (value: boolean) => {
    // Update local state immediately
    setIsOnline(value);
  
    // Decide which endpoint to call
    const path = value
      ? '/api/mentor_status/set_online'
      : '/api/mentor_status/set_offline';
  
    try {
      // Make the authenticated POST
      const response = await BackendManager
        .getInstance()
        .sendRequest(path, 'POST');
  
      if (!response.ok) {
        setIsOnline(!value);
        const err = await response.json();
        console.error('Status toggle failed:', err);
      }
    } catch (error) {
      setIsOnline(!value);
      console.error('Error toggling status:', error);
    }
  };

  const fetchMentees = async () => {
    setIsLoading(true);
    try {
      const backend = BackendManager.getInstance();
      const requests = await backend.getRequestsForMentor();

      // Transform requests into format compatible with swipe cards
      const formatted = requests.map((mentee, index) => ({
        card_id: index + 1,
        mentee_id: mentee.user_id,
        name: `${mentee.firstName} ${mentee.lastName}`,
        primarySubject: mentee.primarySubject,
        location: `${mentee.county}, ${mentee.state_province}, ${mentee.country}`,
        image: { uri: mentee.picture }
      }));

      setMentees(formatted);
      setAllSwiped(false);
      setCurrentIndex(0);
    } catch (error) {
      console.error('Error fetching mentees:', error);
    } finally {
      setIsLoading(false);
    }
  };  

  const Card = ({ name, primarySubject, location, image }) => (
    <View style={styles.card}>
      <ImageBackground source={image} style={styles.cardImage} imageStyle={{ borderRadius: 16 }}>
        <View style={styles.cardOverlay}>
          <Text style={styles.cardTitle}>{name}</Text>
          <Text style={styles.cardText}>Primary Subject: {primarySubject}</Text>
          <Text style={styles.cardText}>Location: {location}</Text>
        </View>
      </ImageBackground>
    </View>
  );

  const handleAccept = () => {
    if (swiperRef.current) {
      const mentee = mentees[currentIndex];
      setAcceptedMentee(mentee);
      setButtonsDisabled(true);
      console.log('Accepted Mentee:', mentee);
    }
  };  
  
  const handleReject = () => {
    if (!buttonsDisabled && swiperRef.current) {
      swiperRef.current.swipeLeft();
    }
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
      {isOnline && mentees.length > 0 && !allSwiped ? (
        <View style={{ alignItems: 'center' }}>
          <Text style={styles.noMatchesTitle}>Mentee Request ❤️</Text>
          <View style={styles.swiperWrapper}>
            <Swiper
              ref={swiperRef}
              cards={mentees}
              cardIndex={currentIndex}
              renderCard={renderCard}
              onSwiped={(cardIndex) => {
                setCurrentIndex(cardIndex + 1);
                setButtonsDisabled(false);
              }}
              onSwipedAll={() => {
                console.log('All mentee requests rejected');
                setAllSwiped(true);
              }}
              stackSize={2}
              backgroundColor="transparent"
              cardVerticalMargin={20}
              disableTopSwipe
              disableBottomSwipe
              containerStyle={styles.swiperContainer}
              swipeBackCard={false}
            />
            {buttonsDisabled && (   // Disable swipe interaction when mentor clicks "Accept"
              <View style={styles.overlayBlocker} pointerEvents="auto" />
            )}
          </View>
          <View style={styles.buttonContainer}>
            <TouchableOpacity
              style={[styles.rejectButton, buttonsDisabled && { opacity: 0.5 }]}
              onPress={handleReject}
              disabled={buttonsDisabled}
            >
              <Text style={styles.rejectButtonText}>Reject</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.acceptButton, buttonsDisabled && { opacity: 0.5 }]}
              onPress={handleAccept}
              disabled={buttonsDisabled}
            >
              <Text style={styles.acceptButtonText}>Accept</Text>
            </TouchableOpacity>
          </View>
        </View>
      ) : isOnline && mentees.length > 0 && allSwiped ? (
        <View style={styles.emptyCard}>
          <Text style={styles.emptyCardText}>No more mentees</Text>
        </View>
      ) : isOnline && mentees.length === 0 ? (
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
  swiperWrapper: {
    height: 360,
    justifyContent: 'center',
    alignItems: 'center',
    width: '100%',
  },
  swiperContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
    paddingHorizontal: 0,
    marginHorizontal: 0,
  },  
  card: {
    width: '90%',
    maxWidth: 320,
    height: 320,
    backgroundColor: '#f0f0f0',
    borderRadius: 16,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 10,
    elevation: 5,
    overflow: 'hidden',
    alignSelf: 'center',
    marginLeft: -40,
  },
  cardImage: {
    width: '100%',
    height: '100%',
    justifyContent: 'flex-end',
  },
  cardOverlay: {
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    padding: 16,
    borderBottomLeftRadius: 16,
    borderBottomRightRadius: 16,
  },
  cardTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#fff',
    marginBottom: 4,
  },
  cardText: {
    fontSize: 14,
    color: '#ddd',
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
    marginTop: 32,
    gap: 20,
  },
  rejectButton: {
    paddingVertical: 12,
    paddingHorizontal: 40,
    backgroundColor: '#FF3B30',
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
    backgroundColor: '#34C759',
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  acceptButtonText: {
    fontSize: 18,
    color: '#fff',
    fontWeight: '600',
  },
  overlayBlocker: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    zIndex: 10,
  },
});