import React, { useRef, useState } from 'react';
import { Text, View, StyleSheet, Image, Dimensions, Platform, FlatList, Button } from 'react-native';
import { ResizeMode, Video } from 'expo-av';

const { width, height } = Dimensions.get('window');
const isMobile = Platform.OS === 'android' || Platform.OS === 'ios';


const abate = {
  "meaning": "Reduce, diminish",
  "wordIndex": 2,
  "wordUsed": false,
  "clipsFound": 4,
  "clipData": {
    "1": {
      "videoURL": "https://www.playphrase.me/video/5b183a2a8079eb4cd4a588b3/62952c6eb071e724e9e59568.mp4",
      "subtitle": "There lives within the very flame of love... a kind of wick or snuff that will abate it.",
      "videoInfo": "Hamlet (1996) [03:00:25]"
    },
    "2": {
      "videoURL": "https://www.playphrase.me/video/5b1839dc8079eb4cd4a57f59/629c44b514bb6d3b4fc38840.mp4",
      "subtitle": "Consumes it with a burning flame that does not abate.",
      "videoInfo": "Born of Hope (2009) [00:23:20]"
    },
    "3": {
      "videoURL": "https://www.playphrase.me/video/5b96ab52cc77853d885611ef/628b9403b071e717a65fbf21.mp4",
      "subtitle": "You basically want to try to either aggravate the demon or abate it.",
      "videoInfo": "Demon House (2018) [00:20:45]"
    },
    "4": {
      "videoURL": "https://www.playphrase.me/video/5b183b3d8079eb4cd4a5a9b8/627826d4b05db515a22da6b1.mp4",
      "subtitle": "l have unleashed a raging shit storm of epic proportions on the board of trustees of that pissant school that will not abate until those girls seek enrollment elsewhere.",
      "videoInfo": "Remember Me (2010) [01:33:10]"
    }
  },
  "searched": true
};

export const cardWidth = Dimensions.get('screen').width * 0.8;

const SwiperCards = () => {
  const video = useRef(null);
  const [status, setStatus] = useState({});
  const videoWidth = isMobile ? width * 0.95 : width * 0.4;

  
  return (
    <FlatList style={styles.container}
      data={Object.values(abate.clipData)}
      keyExtractor={(item) => item.videoURL}
      renderItem={({ item }) => (
        <View style={styles.card}>
          <Text style={styles.word}>{"abate"}</Text>
          <Text style={styles.meaning}>{abate.meaning}</Text>
          <Video
            videoStyle={[styles.video, { width: videoWidth }]}
            ref={video}
            style={[styles.video, { width: videoWidth }]}
            source={{uri: 'https://www.playphrase.me/video/5b183a2a8079eb4cd4a588b3/62952c6eb071e724e9e59568.mp4',}}
            useNativeControls
            resizeMode={ResizeMode.CONTAIN}
            isLooping
            onPlaybackStatusUpdate={(status) => setStatus(() => status)}
          />
          <View style={styles.buttons}>
          <Button
            style={styles.testButton}
            title={(status.isPlaying ? 'Pause' : 'Play')}
            onPress={() =>status.isPlaying? video.current.pauseAsync(): video.current.playAsync()}
          />
          </View>
          <Text style={styles.movieName}>{item.videoInfo}</Text>
          <Text style={styles.subtitleData}>{item.subtitle}</Text>
        </View>
      )}
      horizontal
      pagingEnabled
    />
  );
};

const styles = StyleSheet.create({
    container: {
        width: cardWidth,
    },
  card: {
    width: cardWidth,
    aspectRatio: 1 / 1.67,
    backgroundColor: '#ecf0f1',
    alignItems:"center",
  },
  name: {
    textAlign: 'center', // Add this to center the text
    fontSize: 18, // Set your desired font size
  },
  video: {
    alignSelf: 'center',
    aspectRatio: 1.672/1,
    // height: height * 0.4, // Adjust the height as needed
  },
  word: {textTransform: "uppercase", fontFamily: "Roboto"},
  meaning: {},
  movieName: {},
  subtitleData: {},
});

export default SwiperCards;
