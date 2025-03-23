import React from 'react';
import { View, Text, TouchableOpacity, Image, StyleSheet } from 'react-native';
export function Header( props : { subtitle: string }) {
   return (
        <View style={styles.header}>
            <View style={styles.headerText}>
                <Text style={styles.greeting}>
                    Hi, Jessica <Text style={styles.wave}>👋</Text>
                </Text>
                <Text style={styles.subtitle}>{props.subtitle}</Text>
            </View>
            <TouchableOpacity style={styles.profileSection}>
                <Image source={require('../assets/images/stock_pfp.jpeg')} style={styles.profileImage} />
                <Text style={styles.tokenText}>12 🪙</Text>
            </TouchableOpacity>
        </View>
    );
};

const styles = StyleSheet.create({
    header: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        paddingHorizontal: 5,
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
});

export default Header;