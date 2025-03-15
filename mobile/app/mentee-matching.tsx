import React, { useState, useRef, useEffect } from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet, Alert, Animated, Platform } from 'react-native';
import SwipeCards from 'react-native-swipe-cards';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

export default function MenteeLandingScreen() {
  const router = useRouter();

  const [infoVisible, setInfoVisible] = useState(null);

  const toggleInfo = (mentorId) => {
    setInfoVisible(infoVisible === mentorId ? null : mentorId);
  };

  const [mentorList, setMentorList] = useState([
    { id: 1, name: 'Melissa Gao', subject: 'Biology', location: 'Austin, Texas', rating: 4.8, image: require('../assets/images/stock_mentor2.jpg'), 
      bio: "Passionate about helping students succeed in Biology. Over 5 years of experience in teaching and mentoring." },
    { id: 2, name: 'Mark Smith', subject: 'Physics', location: 'San Jose, CA', rating: 4.6, image: require('../assets/images/stock_mentor3.jpg'),
      bio: "Physics enthusiast with expertise in quantum mechanics and astrophysics. Loves solving complex problems!" },
    { id: 3, name: 'Jennifer Miller', subject: 'History', location: 'San Francisco, CA', rating: 4.6, image: require('../assets/images/stock_mentor4.jpeg'),
      bio: "History geek with a knack for storytelling. Specializes in American and European history." },
  ]);

  const animatedValue = useRef(new Animated.Value(0)).current;

  // Function to remove the first mentor from the list (mimics swiping)
  const removeTopCard = () => {
    setMentorList((prevMentors) => prevMentors.slice(1));
  };

  const handleLike = (card) => {
    Animated.timing(animatedValue, {
      toValue: 500,
      duration: 300,
      useNativeDriver: true,
    }).start(() => {
      console.log(`Liked ${ card.name }`);
      setMentorList((prevMentors) => prevMentors.filter((mentor) => mentor.id !== card.id));
    });
    if(Platform.OS === 'ios' || Platform.OS === 'android') {
      Alert.alert(
        "Join Call",
        `Do you want to join a call with ${ card.name }?`,
      [
        { text: "Cancel", style: "cancel" },
        { text: "Join", onPress: () => console.log(`Joining call with ${ card.name }`) }
        ]
      );
    } else if(Platform.OS === 'web') {
      if(window.confirm(`Do you want to join a call with ${ card.name }?`)) {
        console.log(`Joining call with ${ card.name }`);
      }
    }
};

const handleSkip = (card) => {
  Animated.timing(animatedValue, {
    toValue: -500, 
    duration: 300,
    useNativeDriver: true, 
  }).start(() => {
    console.log(`Skipped ${ card.name }`);
    setMentorList((prevMentors) => prevMentors.filter((mentor) => mentor.id !== card.id));
  });
};

// Handle Refine Search to go back button
const handleRefineSearch = () => {
  router.back();
};

const renderCard = (mentor) => {
  return (
    <Animated.View style={{ transform: [{ translateX: new Animated.Value(0) }] }}>
      <View style={styles.card}>
        <Image source={mentor.image} style={styles.mentorImage} />
        
        {/* Info Icon */}
        <TouchableOpacity onPress={() => toggleInfo(mentor.id)} style={styles.infoButton}>
          <Ionicons name="information-circle-outline" size={30} color="#666" />
        </TouchableOpacity>

        {/* Info Bubble (Appears Only on Toggle) */}
        {infoVisible === mentor.id && (
          <View style={styles.infoBubble}>
            <Text style={styles.infoText}>
              {mentor.bio}
            </Text>
          </View>
        )}

        <View style={styles.overlay}>
          <Text style={styles.mentorName}>{mentor.name}, {mentor.subject}</Text>
          <Text style={styles.mentorLocation}>
            <Ionicons name="location-outline" size={16} /> {mentor.location}
          </Text>
          <View style={styles.ratingContainer}>
            <Text style={styles.mentorRating}>⭐️ {mentor.rating.toFixed(1)}</Text>
          </View>
        </View>
      </View>
    </Animated.View>
  );
};


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
    <View style={styles.header}>
      <View style={styles.headerText}>
        <Text style={styles.greeting}>Hi, Jessica <Text style={styles.wave}>👋</Text></Text>
        <Text style={styles.subtitle}>Swipe Right for a Mentor</Text>
      </View>
      <TouchableOpacity style={styles.profileSection}>
        <Image source={require('../assets/images/stock_pfp.jpeg')} style={styles.profileImage} />
        <Text style={styles.tokenText}>12 🪙</Text>
      </TouchableOpacity>
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
        <Ionicons name="close-circle" size={55} color="red" />
      </TouchableOpacity>

      {/* Refine Search Button */}
      <TouchableOpacity style={styles.refineButton} onPress={handleRefineSearch}>
        <Ionicons name="arrow-back-circle" size={45} color="black" />
      </TouchableOpacity>

      {/* Heart Button -> Right Swipe */}
      <TouchableOpacity
        style={styles.likeButton}
        onPress={() => mentorList.length > 0 && handleLike(mentorList[0])}>
        <Ionicons name="heart-circle" size={55} color="green" />
      </TouchableOpacity>

    </View>
  </View>
);
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f7f7f7',
    paddingTop: 65,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    marginBottom: 20,
  },
  headerText: {
    flexDirection: 'column',
  },
  greeting: {
    fontSize: 28,
    fontWeight: 'bold',
  },
  wave: {
    fontSize: 30,
  },
  subtitle: {
    fontSize: 16,
    paddingTop: 5,
    color: '#666',
  },
  profileSection: {
    flexDirection: 'column',  
    alignItems: 'center', 
  },
  profileImage: {
    width: 45,
    height: 45,
    borderRadius: 25,
  },
  tokenText: {
    fontSize: 14,       
    fontWeight: '600',  
    color: '#333',      
    marginTop: 4,       
    textAlign: 'center',
  },
  swipeContainer: {
    flex: 1,
    alignItems: 'center',
    marginTop: 10,
  },
  card: {
    width: 310,
    height: 550,
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
    paddingVertical: 4,
    paddingHorizontal: 8,
    borderRadius: 6,
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
  
});