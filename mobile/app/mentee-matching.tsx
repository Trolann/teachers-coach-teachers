import React, { useState } from 'react';
import { View, Text, Image, TouchableOpacity, FlatList, ScrollView, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { Alert } from 'react-native';


export default function MenteeLandingScreen() {
  const [likedMentors, setLikedMentors] = useState({});
  const [selectedFilter, setSelectedFilter] = useState('Popular'); 
  const router = useRouter();

  
  const mentors = [
    { id: 1, name: 'Melissa Gao', subject: 'Biology', location: 'Austin, Texas', rating: 4.8, image: require('../assets/images/stock_mentor2.jpg') },
    { id: 2, name: 'Mark Smith', subject: 'Physics', location: 'San Jose, CA', rating: 4.6, image: require('../assets/images/stock_mentor3.jpg') },
    { id: 3, name: 'Jennifer Miller', subject: 'History', location: 'San Francisco, CA', rating: 4.6, image: require('../assets/images/stock_mentor4.jpeg') },
  ];

  const filters = ['Popular', 'Nearby', 'Organization', 'Teaching', 'STEM', 'Urban', 'Local', 'College', 'K-12', 'Powerpoints', 'Top-Rated'];

  // Toggle the liked state
  const handleLikeToggle = (mentor) => {
    setLikedMentors((prev) => ({
      ...prev,
      [mentor.id]: !prev[mentor.id],
    }));

    console.log(`${mentor.name} is ${!likedMentors[mentor.id] ? "Liked" : "Unliked"}`);
  };

  // Handle filter selection with logging
  const handleFilterSelection = (filter) => {
    setSelectedFilter(filter);
    console.log(`Selected Filter: ${filter}`); // ✅ Logs the selected filter
  };

  return (
    <View style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.greeting}>Hi, Jessica <Text style={styles.wave}>👋</Text></Text>
            <Text style={styles.subtitle}>Find yourself a Mentor</Text>
          </View>
          <TouchableOpacity>
            <Image source={require('../assets/images/stock_pfp.jpeg')} style={styles.profileImage} />
            <View style={styles.tokenContainer}>
              <Text style={styles.tokenText}>12 🪙</Text>
            </View>
          </TouchableOpacity>
        </View>

        {/* Tag Filters (Scrollable) */}
        <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.tagsContainer}>
          {filters.map((filter, index) => (
            <TouchableOpacity
              key={index}
              style={[styles.tag, selectedFilter === filter && styles.selectedTag]}
              onPress={() => handleFilterSelection(filter)}
            >
              <Text style={[styles.tagText, selectedFilter === filter && styles.selectedTagText]}>
                {filter}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>

        {/* Mentor Matches Section */}
        <Text style={styles.sectionTitle}>Mentors Matched for You ❤️</Text>
        <FlatList
          data={mentors}
          horizontal
          showsHorizontalScrollIndicator={false}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => (
            <TouchableOpacity 
              style={styles.mentorCard}
              onPress={() => Alert.alert(
                "Join Call",
                `Do you want to join a call with ${item.name}?`,
                [
                  { text: "Cancel", style: "cancel" },
                  { text: "Join", onPress: () => console.log(`Joining call with ${item.name}`) }
                ]
              )}
            >
              <View style={styles.onlineIndicator} />
              <Image source={item.image} style={styles.mentorImage} />
              <View style={styles.mentorOverlay}>
                <Text style={styles.mentorName}>{item.name}, {item.subject}</Text>
                <View style={styles.mentorMeta}>
                    <View style={styles.locationContainer}>
                        <Ionicons name="location-outline" size={14} color="#fff" />
                        <Text style={styles.mentorLocation}>{item.location}</Text>
                    </View>
                    <View style={styles.ratingContainer}>
                        <Text style={styles.mentorRating}>⭐ {item.rating}</Text>
                    </View>
                </View>
              </View>
              <TouchableOpacity 
                style={styles.heartIcon} 
                onPress={() => handleLikeToggle(item)}
              >
                <Ionicons 
                  name={likedMentors[item.id] ? "heart" : "heart-outline"} 
                  size={22} 
                  color={likedMentors[item.id] ? "red" : "white"} 
                />
              </TouchableOpacity>
            </TouchableOpacity>
          )}
        />

        {/* CTA Button */}
        <View style={styles.ctaContainer}>
          <Text style={styles.noMatchText}>Not finding the right match?</Text>
          <TouchableOpacity onPress={() => router.back()} style={styles.ctaButton}>
            <Text style={styles.ctaText}>Click here</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>

      {/* Sticky Navbar */}
      <View style={styles.navbar}>
        <Ionicons name="home" size={24} color="black" />
        <Ionicons name="time-outline" size={24} color="gray" />
        <Ionicons name="heart-outline" size={24} color="gray" />
        <Ionicons name="person-outline" size={24} color="gray" />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: 'white',
    paddingTop: 10,
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingTop: 50,
    paddingBottom: 100, 
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  greeting: {
    fontSize: 30,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  wave: {
    fontSize: 30,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
  },
  profileImage: {
    width: 45,
    height: 45,
    borderRadius: 25,
  },
  tokenText: {
    fontSize: 14,
    color: '#333',
    marginLeft: 4,
  },
  tokenContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 5,
  },
  tagsContainer: {
    flexDirection: 'row',
    marginBottom: 10,
    paddingTop: 10,
    paddingBottom: 5,
    paddingRight: 5,
  },
  tag: {
    backgroundColor: '#f2f2f2',
    paddingVertical: 8,
    paddingHorizontal: 15,
    borderRadius: 20,
    marginRight: 10,
  },
  selectedTag: {
    backgroundColor: 'black',
  },
  tagText: {
    fontSize: 14,
    fontWeight: '500',
  },
  selectedTagText: {
    color: 'white',
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 10,
    paddingTop: 10,
    paddingBottom: 15,
  },
  mentorCard: {
    width: 230,
    backgroundColor: '#fff',
    borderRadius: 20,
    overflow: 'hidden',
    marginRight: 15,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 3,
    position: 'relative',
  },
  mentorImage: {
    width: '100%',
    height: 350,
  },
  onlineIndicator: {
    position: 'absolute',
    top: 22,
    left: 17,
    width: 12,
    height: 12,
    backgroundColor: 'green',
    borderRadius: 6,
    borderWidth: 2,
    borderColor: 'green', 
    zIndex: 2, 
  },
  mentorOverlay: {
    position: 'absolute',
    bottom: 0,
    width: '100%',
    backgroundColor: 'rgba(0, 0, 0, 0.2)', 
    padding: 12,
    borderBottomLeftRadius: 20,
    borderBottomRightRadius: 20,
  },
  mentorName: {
    fontSize: 16,
    fontWeight: 'bold',
    color: 'white',
    paddingTop: 5,
    paddingBottom: 7,
  },
  mentorMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between', 
    marginTop: 2,
    paddingBottom: 5,
  },
  
  locationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  
  ratingContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'flex-end', 
  },  
  mentorLocation: {
    fontSize: 12,
    color: 'white',
    marginLeft: 4,
  },
  mentorRating: {
    fontSize: 14,
    fontWeight: 'bold',
    color: 'gold',
    marginTop: 4,
  },
  heartIcon: {
    position: 'absolute',
    top: 10,
    right: 10,
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    padding: 8,
    borderRadius: 50,
  },
  ctaContainer: {
    marginTop: 15,
    alignItems: 'center',
    padding: 25,
  },
  noMatchText: {
    fontSize: 19,
    fontWeight: 'bold',
    textAlign: 'center',
    paddingBottom: 10,
  },
  ctaButton: {
    backgroundColor: '#48B2EE',
    paddingVertical: 12,
    paddingHorizontal: 25,
    borderRadius: 20,
    alignItems: 'center',
    marginTop: 10,
  },
  ctaText: {
    color: 'white',
    fontSize: 16,
    fontWeight: 'bold',
  },
  navbar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingVertical: 10,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderColor: '#ddd',
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    paddingBottom: 40,
  },
});
