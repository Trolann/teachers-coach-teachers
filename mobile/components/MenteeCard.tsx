import React from 'react';
import { View, Text, Image, TouchableOpacity, StyleSheet, Animated } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

const MenteeCard = ({
    mentor,
    infoVisible,
    toggleInfo
}) => {
    return (
        <View style={styles.card}>
            {/* Green Online Indicator */}
            <View style={styles.onlineIndicator} />

            {/* Mentor Image */}
            <Image source={typeof mentor.image === 'string' ? { uri: mentor.image } : mentor.image} />
            
            {/* Info Icon */}
            {/*
            infoVisible !== undefined && (
                <TouchableOpacity onPress={() => toggleInfo(mentor.id)} style={styles.infoButton}>
                    <Ionicons name="information-circle-outline" size={30} color="#666" />
                </TouchableOpacity>
            )
            */}

            {/* Info Bubble */}
            {/*
            infoVisible === mentor.id && (
                <View style={styles.infoBubble}>
                    <Text style={styles.infoText}>{mentor.bio}</Text>
                </View>
            )
            */}


            <View style={styles.overlay}>
                <Text style={styles.mentorName}>{mentor.name}, {mentor.subject}</Text>
                <Text style={styles.mentorLocation}>
                    <Ionicons name="location-outline" size={16} /> {mentor.location}
                </Text>
                {/*
                <View style={styles.ratingContainer}>
                    <Text style={styles.mentorRating}>⭐️ {mentor.rating}</Text>
                </View>
                */}
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
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

export default MenteeCard;
